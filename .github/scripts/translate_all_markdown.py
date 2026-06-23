from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(".")
STATE_FILE = Path(".translation-state.json")
STATUS_FILE = Path("TRANSLATION_STATUS.md")
MAX_FILES_PER_RUN = int(os.environ.get("MAX_FILES_PER_RUN", "12"))
MAX_WORKERS = int(os.environ.get("TRANSLATE_WORKERS", "3"))
MAX_CHUNK_CHARS = int(os.environ.get("MAX_CHUNK_CHARS", "2600"))
MAX_ATTEMPTS = int(os.environ.get("MAX_FILE_ATTEMPTS", "3"))

ENDPOINTS = (
    "https://translate.googleapis.com/translate_a/single",
    "https://translate.google.com/translate_a/single",
)
EXCLUDED_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".venv",
    "venv",
}
TRANSLATED_SUFFIXES = (
    ".zh-CN.md",
    ".zh_CN.md",
    ".zh.md",
    "-zh-CN.md",
    "-zh.md",
    "_zh-CN.md",
    "_zh.md",
)

FENCED_BLOCK_RE = re.compile(r"(```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~)", re.DOTALL)
PROTECTED_RE = re.compile(
    r"(`[^`\n]+`|https?://[^\s)>\]}]+|<[^>\n]+>|"
    r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|"
    r"\b[a-zA-Z][\w.]*_[\w.]+\b|"
    r"\b(?:GET|POST|PUT|PATCH|DELETE|JSON|YAML|XML|HTML|HTTP|HTTPS|API|URL|URI|"
    r"MCP|OAuth|SHA-256|UTF-8|CLI|SDK|SQL|CSS|JavaScript|TypeScript|Python|Bash)\b|"
    r"\"[A-Za-z_][A-Za-z0-9_.:/-]*\")",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"QZX\d{5}P\d{5}XZQ")
SOURCE_SHA_RE = re.compile(r"<!-- source-sha256: ([0-9a-f]{64}) -->")


@dataclass(frozen=True)
class Piece:
    text: str
    translate: bool


class RateGate:
    def __init__(self, interval: float = 0.2) -> None:
        self.interval = interval
        self.lock = threading.Lock()
        self.last = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            delay = self.interval - (now - self.last)
            if delay > 0:
                time.sleep(delay)
            self.last = time.monotonic()


RATE_GATE = RateGate()


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def target_for(source: Path) -> Path:
    return source.with_name(source.stem + ".zh-CN.md")


def is_translation_file(path: Path) -> bool:
    name = path.name
    return any(name.endswith(suffix) for suffix in TRANSLATED_SUFFIXES)


def visible_language_text(text: str) -> str:
    text = FENCED_BLOCK_RE.sub(" ", text)
    text = PROTECTED_RE.sub(" ", text)
    return text


def looks_english(text: str) -> bool:
    visible = visible_language_text(text)
    latin = len(re.findall(r"[A-Za-z]", visible))
    han = len(re.findall(r"[\u4e00-\u9fff]", visible))
    return latin >= 40 and latin > max(20, int(han * 1.5))


def discover_sources() -> list[Path]:
    sources: list[Path] = []
    for path in ROOT.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path == STATUS_FILE or is_translation_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if looks_english(text):
            sources.append(path)
    return sorted(sources, key=lambda p: (p.stat().st_size, p.as_posix().lower()))


def target_is_current(source: Path, target: Path) -> bool:
    if not target.exists():
        return False
    try:
        first = target.read_text(encoding="utf-8")[:1200]
    except UnicodeDecodeError:
        return False
    match = SOURCE_SHA_RE.search(first)
    return bool(match and match.group(1) == sha256_text(source.read_text(encoding="utf-8")))


def split_text(text: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        candidates = [
            remaining.rfind("\n\n", 0, limit),
            remaining.rfind("\n", 0, limit),
            remaining.rfind(". ", 0, limit),
            remaining.rfind("; ", 0, limit),
            remaining.rfind(" ", 0, limit),
        ]
        cut = max(candidates)
        if cut < limit // 2:
            cut = limit
        elif remaining[cut : cut + 2] in {"\n\n", ". ", "; "}:
            cut += 2
        else:
            cut += 1
        chunks.append(remaining[:cut])
        remaining = remaining[cut:]
    if remaining:
        chunks.append(remaining)
    return chunks


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[: end + 5], text[end + 5 :]


def build_pieces(source: str) -> tuple[str, list[Piece]]:
    front_matter, body = split_front_matter(source)
    pieces: list[Piece] = []
    for index, part in enumerate(FENCED_BLOCK_RE.split(body)):
        if not part:
            continue
        if index % 2 == 1:
            pieces.append(Piece(part, False))
            continue
        for chunk in split_text(part):
            pieces.append(Piece(chunk, bool(re.search(r"[A-Za-z]", chunk))))
    return front_matter, pieces


def protect(text: str, piece_index: int) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        token = f"QZX{piece_index:05d}P{len(mapping):05d}XZQ"
        mapping[token] = match.group(0)
        return token

    return PROTECTED_RE.sub(replace, text), mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    missing = [token for token in mapping if token not in text]
    if missing:
        raise ValueError("missing protected tokens: " + ", ".join(missing[:8]))
    for token, original in mapping.items():
        text = text.replace(token, original)
    return text


def parse_google_response(raw: bytes) -> str:
    data = json.loads(raw.decode("utf-8"))
    translated = "".join(
        segment[0]
        for segment in data[0]
        if segment and isinstance(segment[0], str)
    )
    if not translated:
        raise ValueError("empty translation response")
    return translated


def request_translation(text: str) -> str:
    payload = urllib.parse.urlencode(
        [("client", "gtx"), ("sl", "en"), ("tl", "zh-CN"), ("dt", "t"), ("q", text)]
    ).encode("utf-8")
    last_error: Exception | None = None

    for attempt in range(1, 8):
        for endpoint in ENDPOINTS:
            RATE_GATE.wait()
            request = urllib.request.Request(
                endpoint,
                data=payload,
                method="POST",
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; MarkdownMirrorTranslator/1.0)",
                    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                    "Accept": "application/json,text/plain,*/*",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    return parse_google_response(response.read())
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", errors="replace")
                last_error = RuntimeError(f"HTTP {error.code}: {detail[:300]}")
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
                last_error = error
        time.sleep(min(45, 2**attempt))
    raise RuntimeError(f"translation request failed: {last_error}")


def translate_fragments(original: str) -> str:
    parts = PROTECTED_RE.split(original)
    output: list[str] = []
    for part in parts:
        if not part:
            continue
        if PROTECTED_RE.fullmatch(part) or not re.search(r"[A-Za-z]", part):
            output.append(part)
        else:
            output.append(request_translation(part))
    return "".join(output)


def translate_piece(index: int, text: str) -> tuple[int, str, bool]:
    protected, mapping = protect(text, index)
    used_fallback = False
    try:
        translated = restore(request_translation(protected), mapping)
    except Exception as error:
        print(f"Piece {index}: {error}; using fragment fallback", flush=True)
        translated = translate_fragments(text)
        used_fallback = True

    source_len = max(1, len(text.strip()))
    if source_len > 300 and len(translated.strip()) < source_len * 0.16:
        raise RuntimeError(f"Piece {index} appears truncated")
    return index, translated, used_fallback


def translate_document(source_path: Path) -> tuple[Path, int, int]:
    source = source_path.read_text(encoding="utf-8")
    source_sha = sha256_text(source)
    front_matter, pieces = build_pieces(source)
    results: dict[int, str] = {}
    fallback_count = 0
    translatable = [(i, p.text) for i, p in enumerate(pieces) if p.translate]

    for index, piece in enumerate(pieces):
        if not piece.translate:
            results[index] = piece.text

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(translate_piece, index, text): index
            for index, text in translatable
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            index, translated, used_fallback = future.result()
            results[index] = translated
            fallback_count += int(used_fallback)
            completed += 1
            print(
                f"{source_path}: completed {completed}/{len(translatable)} pieces",
                flush=True,
            )

    missing = [i for i in range(len(pieces)) if i not in results]
    if missing:
        raise RuntimeError(f"Missing output pieces: {missing[:20]}")

    translated_body = front_matter + "".join(results[i] for i in range(len(pieces)))
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", translated_body))
    source_latin = len(re.findall(r"[A-Za-z]", visible_language_text(source)))
    minimum_chinese = min(1000, max(8, source_latin // 18))
    if chinese_count < minimum_chinese:
        raise RuntimeError(
            f"Chinese character count too low: {chinese_count} < {minimum_chinese}"
        )
    if PLACEHOLDER_RE.search(translated_body):
        raise RuntimeError("Unrestored placeholder remains")

    target = target_for(source_path)
    header = (
        "<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->\n"
        f"<!-- source-file: {source_path.as_posix()} -->\n"
        f"<!-- source-sha256: {source_sha} -->\n"
        "<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->\n"
        f"<!-- fragment-fallback-pieces: {fallback_count} -->\n\n"
    )
    target.write_text(header + translated_body, encoding="utf-8")
    return target, chinese_count, fallback_count


def commit_and_push(paths: list[Path], message: str) -> None:
    run_git("config", "user.name", "github-actions[bot]")
    run_git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run_git("add", *[path.as_posix() for path in paths])
    staged = run_git("diff", "--cached", "--quiet", check=False)
    if staged.returncode == 0:
        return
    run_git("commit", "-m", message)
    pushed = run_git("push", "origin", "HEAD:main", check=False)
    if pushed.returncode != 0:
        print(pushed.stdout, flush=True)
        run_git("pull", "--rebase", "origin", "main")
        run_git("push", "origin", "HEAD:main")


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"attempts": {}, "errors": {}}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"attempts": {}, "errors": {}}


def pending_sources(state: dict) -> tuple[list[Path], list[Path]]:
    pending: list[Path] = []
    blocked: list[Path] = []
    attempts = state.setdefault("attempts", {})
    for source in discover_sources():
        target = target_for(source)
        if target_is_current(source, target):
            continue
        if int(attempts.get(source.as_posix(), 0)) >= MAX_ATTEMPTS:
            blocked.append(source)
        else:
            pending.append(source)
    return pending, blocked


def write_status(state: dict) -> None:
    sources = discover_sources()
    completed = [s for s in sources if target_is_current(s, target_for(s))]
    pending, blocked = pending_sources(state)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Markdown 中文翻译状态",
        "",
        f"更新时间：{now}",
        "",
        f"- 检测到的英文 Markdown：{len(sources)}",
        f"- 已生成且与源文件同步：{len(completed)}",
        f"- 待翻译：{len(pending)}",
        f"- 连续失败、等待人工处理：{len(blocked)}",
        "",
        "中文文件与英文源文件放在同一目录，文件名后缀为 `.zh-CN.md`。",
    ]
    if blocked:
        lines.extend(["", "## 等待人工处理", ""])
        for path in blocked:
            error = state.get("errors", {}).get(path.as_posix(), "unknown error")
            lines.append(f"- `{path.as_posix()}`：{error}")
    STATUS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_state_and_status(state: dict) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_status(state)
    commit_and_push([STATE_FILE, STATUS_FILE], "Update Markdown translation status")


def run_batch() -> int:
    state = load_state()
    pending, _ = pending_sources(state)
    selected = pending[:MAX_FILES_PER_RUN]
    print(f"Pending files: {len(pending)}; processing this run: {len(selected)}", flush=True)

    for source in selected:
        key = source.as_posix()
        state.setdefault("attempts", {})[key] = int(state["attempts"].get(key, 0)) + 1
        try:
            target, chinese_count, fallback_count = translate_document(source)
            state.setdefault("errors", {}).pop(key, None)
            print(
                f"Translated {source} -> {target}; Chinese={chinese_count}; "
                f"fallback pieces={fallback_count}",
                flush=True,
            )
            commit_and_push([target], f"Add Chinese translation for {source.as_posix()}")
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            state.setdefault("errors", {})[key] = message[:1000]
            print(f"Failed {source}: {message}", flush=True)
        finally:
            STATE_FILE.write_text(
                json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    save_state_and_status(state)
    remaining, blocked = pending_sources(state)
    print(f"Remaining eligible files: {len(remaining)}; blocked: {len(blocked)}", flush=True)
    return len(remaining)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pending-count", action="store_true")
    args = parser.parse_args()
    state = load_state()
    if args.pending_count:
        pending, _ = pending_sources(state)
        print(len(pending))
        return
    run_batch()


if __name__ == "__main__":
    main()
