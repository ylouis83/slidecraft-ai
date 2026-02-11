"""
SlideCraft CLI — Command-line interface for PPT generation.
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        prog="slidecraft",
        description="🎨 SlideCraft-AI — Multi-Agent PPT Generator",
    )
    parser.add_argument("topic", help="PPT 主题")
    parser.add_argument("-n", "--slides", type=int, default=10, help="幻灯片数量")
    parser.add_argument("-a", "--audience", default="通用", help="目标受众")
    parser.add_argument(
        "-s", "--style",
        default="business",
        choices=["business", "tech", "minimal", "creative", "academic", "dark", "gradient"],
        help="设计风格",
    )
    parser.add_argument("-l", "--language", default="zh-CN", help="语言")
    parser.add_argument("-o", "--output", default="", help="输出文件路径")
    parser.add_argument("--ref-image", action="append", default=[], help="参考图片路径")
    parser.add_argument("--ref-doc", action="append", default=[], help="参考文档路径")
    parser.add_argument("--brand-color", action="append", default=[], help="品牌色号")
    parser.add_argument("-d", "--description", default="", help="补充描述")

    args = parser.parse_args()

    from slidecraft import SlideCraft

    craft = SlideCraft()
    result = craft.generate(
        topic=args.topic,
        description=args.description,
        audience=args.audience,
        slide_count=args.slides,
        style=args.style,
        language=args.language,
        reference_images=args.ref_image,
        reference_documents=args.ref_doc,
        brand_colors=args.brand_color,
    )

    if result.success and args.output:
        result.save(args.output)

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
