"""
Basic Usage Example — Generate a PPT from natural language.
"""

from slidecraft import SlideCraft

def main():
    # Initialize with default config (reads from .env)
    craft = SlideCraft()

    # Generate a presentation
    result = craft.generate(
        topic="2025年人工智能技术趋势与企业应用",
        description=(
            "涵盖大语言模型、多模态AI、Agent技术、AI编程等方向，"
            "分析各技术的成熟度、应用场景和投资回报"
        ),
        audience="企业CTO和技术决策者",
        slide_count=15,
        style="tech",
        language="zh-CN",
    )

    if result.success:
        print(f"✅ 生成成功: {result.output_path}")
        print(f"   评分: {result.review.overall_score}/10" if result.review else "")
        print(f"   用时: {result.generation_time_seconds}s")
    else:
        print(f"❌ 生成失败: {result.error_message}")


if __name__ == "__main__":
    main()
