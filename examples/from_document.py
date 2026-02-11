"""
Generate PPT from a document (PDF / DOCX / Markdown).
The Planner Agent will extract key content and structure it into slides.
"""

from slidecraft import SlideCraft

def main():
    craft = SlideCraft()

    result = craft.generate_from_document(
        document_path="./quarterly_report.pdf",
        style="minimal",
        audience="公司管理层",
        slide_count=20,
    )

    if result.success:
        print(f"✅ 生成成功: {result.output_path}")
    else:
        print(f"❌ 生成失败: {result.error_message}")


if __name__ == "__main__":
    main()
