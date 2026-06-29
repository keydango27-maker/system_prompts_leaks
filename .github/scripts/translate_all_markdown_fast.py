from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT = Path('.github/scripts/translate_all_markdown.py')
spec = importlib.util.spec_from_file_location('translator', SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit(f'Unable to load {SCRIPT}')
translator = importlib.util.module_from_spec(spec)
# Python 3.12 dataclasses expects the defining module to be present in
# sys.modules while the module body is executed.
sys.modules[spec.name] = translator
spec.loader.exec_module(translator)

# Final-stage profile: isolate one large document per run and translate its
# chunks concurrently. Short request timeouts prevent one throttled endpoint
# from consuming the entire GitHub Actions time budget.
translator.MAX_FILES_PER_RUN = int(os.environ.get('MAX_FILES_PER_RUN', '1'))
translator.MAX_WORKERS = int(os.environ.get('TRANSLATE_WORKERS', '10'))
translator.MAX_ATTEMPTS = int(os.environ.get('MAX_FILE_ATTEMPTS', '5'))
translator.RATE_GATE.interval = float(os.environ.get('REQUEST_INTERVAL', '0.05'))

_original_split_text = translator.split_text


def split_text_fast(text: str, limit: int = 4800) -> list[str]:
    return _original_split_text(text, limit)


translator.split_text = split_text_fast


def request_translation_fast(text: str) -> str:
    payload = urllib.parse.urlencode(
        [
            ('client', 'gtx'),
            ('sl', 'en'),
            ('tl', 'zh-CN'),
            ('dt', 't'),
            ('q', text),
        ]
    ).encode('utf-8')
    last_error: Exception | None = None

    for attempt in range(1, 4):
        for endpoint in translator.ENDPOINTS:
            translator.RATE_GATE.wait()
            request = urllib.request.Request(
                endpoint,
                data=payload,
                method='POST',
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; MarkdownMirrorTranslator/2.1)',
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'Accept': 'application/json,text/plain,*/*',
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    return translator.parse_google_response(response.read())
            except urllib.error.HTTPError as error:
                detail = error.read().decode('utf-8', errors='replace')
                last_error = RuntimeError(f'HTTP {error.code}: {detail[:200]}')
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
                last_error = error
        time.sleep(attempt)

    raise RuntimeError(f'fast translation request failed: {last_error}')


translator.request_translation = request_translation_fast

if __name__ == '__main__':
    remaining = translator.run_batch()
    print(f'Fast-profile run complete; remaining eligible files: {remaining}', flush=True)

# Trigger refresh after loader fix.
