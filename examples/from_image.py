"""
Generate PPT from a reference image.
Uses multimodal vision to analyze the image style and replicate it.
"""

from slidecraft import SlideCraft

def main():
    craft = SlideCraft()

    # Generate from a reference image — the Designer Agent will analyze
    # the image's color scheme, layout, and typography, then replicate it
    result = craft.generate_from_image(
        image_path="./reference_slide.png",
        topic="我们的产品介绍",
        audience="潜在客户",
        slide_count=12,
        replicate_style=True,
    )

    if result.success:
        print(f"✅ 生成成功: {result.output_path}")
    else:
        print(f"❌ 生成失败: {result.error_message}")


if __name__ == "__main__":
    main()
