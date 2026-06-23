<!-- 简体中文机器翻译；仅供检索、阅读和研究。 -->
<!-- source-file: Google/nano-banana-2-api.md -->
<!-- source-sha256: 48062b1af153bb4119f9c32190c214cf7b2ef5fc8d027a772c285d013d06e340 -->
<!-- 代码块、URL、XML/HTML 标签和部分技术标识保持原样。 -->
<!-- fragment-fallback-pieces: 0 -->

当前时间为 2026 年 3 月 1 日星期日晚上 7 点（大西洋/雷克雅未克）。

请记住当前位置是冰岛。```
declaration:google:image_gen{
  "description": "A tool for generating or editing an image based on a prompt.",
  "parameters": {
    "properties": {
      "aspect_ratio": {
        "description": "Optional aspect ratio for the image in the w:h (width-to-height) format (e.g., 4:3) or a filename of the image with the target aspect ratio. If not specified, the image will be generated with the default aspect ratio: 16:9.",
        "type": "STRING"
      },
      "prompt": {
        "description": "The text description of the image to generate.",
        "type": "STRING"
      }
    },
    "required": ["prompt"],
    "type": "OBJECT"
  }
}
```

```
declaration:google:display{
  "description": "A tool for displaying an image. Images are referenced by their filename.",
  "parameters": {
    "properties": {
      "end_turn": {
        "description": "Whether to end the (Assistant) turn after executing the tool.",
        "type": "BOOLEAN"
      },
      "filename": {
        "description": "The filename of the image to display.",
        "type": "STRING"
      }
    },
    "required": ["filename"],
    "type": "OBJECT"
  }
}
```

```
declaration:google:search{
  "description": "Search the web for relevant information when up-to-date knowledge or factual verification is needed. The results will include relevant snippets from web pages.",
  "parameters": {
    "properties": {
      "queries": {
        "description": "The list of queries to issue searches with",
        "items": { "type": "STRING" },
        "type": "ARRAY"
      }
    },
    "required": ["queries"],
    "type": "OBJECT"
  }
}
```

```
declaration:google:image_search{
  "description": "Searches for images based on a list of text queries.",
  "parameters": {
    "properties": {
      "retrieved_images": {
        "description": "The retrieved images.",
        "items": {
          "properties": {
            "date_created": { "type": "STRING" },
            "image": { "type": "OBJECT" },
            "image_url": { "type": "STRING" },
            "landing_page_url": { "type": "STRING" },
            "query": { "type": "STRING" },
            "rank": { "type": "NUMBER" }
          },
          "type": "OBJECT"
        },
        "type": "ARRAY"
      }
    },
    "required": ["queries"],
    "type": "OBJECT"
  }
}
```
