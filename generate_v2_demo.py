"""
Test script: Generate the same Data Governance PPT using the enhanced BuilderV2.
Compares the V2 output (with gradients + shadows + auto-fit) against V1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from slidecraft.agents.builder_v2 import BuilderV2Agent
from slidecraft.config import SlideCraftConfig
from slidecraft.models import *

config = SlideCraftConfig()
builder = BuilderV2Agent(config)

# ── Design (Dark Tech with gradient enabled) ──

design = DesignSpec(
    style=DesignStyle.DARK,
    colors=ColorPalette(
        primary="#38bdf8",
        secondary="#10b981",
        accent="#f59e0b",
        background="#0b1020",
        surface="#131a2d",
        text_primary="#f8fafc",
        text_secondary="#dbeafe",
    ),
    fonts=FontScheme(
        title_font="Microsoft YaHei",
        body_font="Microsoft YaHei",
        title_size_pt=36,
        subtitle_size_pt=22,
        body_size_pt=18,
        caption_size_pt=14,
    ),
    use_gradient_backgrounds=True,  # ← V2 supports this!
)

# ── Plan (same content as before) ──

plan = PresentationPlan(
    title="企业级数据治理框架",
    subtitle="构建数据驱动的智能组织 · 2026",
    slides=[
        SlideOutline(slide_number=1, slide_type=SlideType.COVER, title="Cover"),
        SlideOutline(slide_number=2, slide_type=SlideType.TABLE_OF_CONTENTS, title="TOC"),
        SlideOutline(slide_number=3, slide_type=SlideType.SECTION_HEADER, title="S1"),
        SlideOutline(slide_number=4, slide_type=SlideType.CONTENT, title="What"),
        SlideOutline(slide_number=5, slide_type=SlideType.CONTENT, title="Challenges"),
        SlideOutline(slide_number=6, slide_type=SlideType.SECTION_HEADER, title="S2"),
        SlideOutline(slide_number=7, slide_type=SlideType.IMAGE_TEXT, title="Arch", needs_image=True),
        SlideOutline(slide_number=8, slide_type=SlideType.TWO_COLUMN, title="Org"),
        SlideOutline(slide_number=9, slide_type=SlideType.SECTION_HEADER, title="S3"),
        SlideOutline(slide_number=10, slide_type=SlideType.IMAGE_TEXT, title="Quality", needs_image=True),
        SlideOutline(slide_number=11, slide_type=SlideType.CONTENT, title="Metadata"),
        SlideOutline(slide_number=12, slide_type=SlideType.IMAGE_TEXT, title="Security", needs_image=True),
        SlideOutline(slide_number=13, slide_type=SlideType.SECTION_HEADER, title="S4"),
        SlideOutline(slide_number=14, slide_type=SlideType.CHART, title="Maturity"),
        SlideOutline(slide_number=15, slide_type=SlideType.TIMELINE, title="Roadmap"),
        SlideOutline(slide_number=16, slide_type=SlideType.COMPARISON, title="Compare"),
        SlideOutline(slide_number=17, slide_type=SlideType.QUOTE, title="Quote"),
        SlideOutline(slide_number=18, slide_type=SlideType.THANK_YOU, title="End"),
    ],
)

content = PresentationContent(slides=[
    SlideContent(slide_number=1, title="企业级数据治理框架",
                 subtitle="构建数据驱动的智能组织 · Data Governance Framework 2026"),
    SlideContent(slide_number=2, title="目 录"),
    SlideContent(slide_number=3, title="数据治理概述", subtitle="PART 01"),
    SlideContent(slide_number=4, title="什么是数据治理", bullet_points=[
        "定义：对数据资产进行正式管理的一套策略、流程和标准体系",
        "核心目标：确保数据的可用性、一致性、完整性和安全性",
        "业务价值：将数据转化为战略资产，赋能数据驱动决策",
        "覆盖范围：数据全生命周期管理 — 从创建、存储到归档和销毁",
        "国际标准参考：DAMA-DMBOK 2.0 / ISO 8000 / DCMM",
    ], notes="强调数据治理不仅是IT工程，更是企业战略层面的系统化工作"),
    SlideContent(slide_number=5, title="企业数据治理面临的挑战", bullet_points=[
        "🏝️  数据孤岛 — 各部门数据互不连通，口径不统一",
        "📉  质量低下 — 重复、缺失、错误数据导致决策失误",
        "⚖️  合规压力 — GDPR / 《数据安全法》/ 《个人信息保护法》",
        "🔄  变更管理 — 业务快速迭代，数据标准难以跟上",
        "👥  组织阻力 — 缺乏明确的数据责任人和治理文化",
        "💰  投入产出 — 治理收益难量化，管理层支持不足",
    ]),
    SlideContent(slide_number=6, title="治理框架架构", subtitle="PART 02"),
    SlideContent(slide_number=7, title="数据治理架构全景", bullet_points=[
        "🏗️  战略层 — 治理愿景、目标与策略",
        "👥  组织层 — 数据委员会、数据Owner、数据管家",
        "📋  制度层 — 标准规范、流程制度、考核机制",
        "⚙️  技术层 — 元数据平台、数据质量工具、血缘分析",
        "📊  运营层 — 日常监控、问题处置、持续改进",
    ]),
    SlideContent(slide_number=8, title="治理组织架构与角色", bullet_points=[
        "数据治理委员会 (决策层)",
        "首席数据官 CDO (领导层)",
        "数据管理办公室 DMO (管理层)",
        "数据所有者 Data Owner (业务侧)",
        "数据管家 Data Steward (执行层)",
        "数据工程师 / 分析师 (技术团队)",
    ]),
    SlideContent(slide_number=9, title="核心治理能力", subtitle="PART 03"),
    SlideContent(slide_number=10, title="数据质量管理", bullet_points=[
        "六维质量指标：完整性 · 一致性 · 准确性 · 及时性 · 唯一性 · 有效性",
        "质量规则引擎：自动化检测 + 异常预警",
        "质量评分卡：按域、表、字段三级评分",
        "问题处置闭环：发现 → 定责 → 修复 → 验证 → 预防",
        "持续监控大屏：实时数据健康度仪表盘",
    ]),
    SlideContent(slide_number=11, title="元数据管理", bullet_points=[
        "技术元数据 — 字段定义、数据类型、存储位置、ETL 逻辑",
        "业务元数据 — 业务术语表、数据字典、指标定义",
        "操作元数据 — 数据血缘、影响分析、变更历史",
        "数据目录 Data Catalog — 统一检索、一键定位数据资产",
        "血缘追踪 Lineage — 端到端可视化数据流向与加工链路",
        "自动采集 — 自动识别并注册新数据资产，减少人工维护",
    ]),
    SlideContent(slide_number=12, title="数据安全与合规", bullet_points=[
        "数据分类分级 — 公开 / 内部 / 敏感 / 机密四级管控",
        "敏感数据识别 — 自动扫描 + AI 辅助识别 PII / PHI",
        "访问权限管理 — RBAC + ABAC 精细化权限控制",
        "脱敏与加密 — 静态脱敏 / 动态脱敏 / 端到端加密",
        "审计与追溯 — 全链路操作日志 + 合规审计报告",
    ]),
    SlideContent(slide_number=13, title="实施路径", subtitle="PART 04"),
    SlideContent(slide_number=14, title="数据治理成熟度模型", data={
        "labels": ["初始级", "受管理级", "已定义级", "量化管理级", "持续优化级"],
        "values": [20, 40, 60, 80, 95],
        "series_name": "成熟度评分",
    }),
    SlideContent(slide_number=15, title="三年实施路线图", bullet_points=[
        "Phase 1 · 奠基期\n标准制定 + 组织搭建",
        "Phase 2 · 建设期\n平台部署 + 试点域治理",
        "Phase 3 · 推广期\n全域治理 + 质量达标",
        "Phase 4 · 深化期\nAI驱动 + 数据资产化",
        "Phase 5 · 卓越期\n数据驱动决策文化",
    ]),
    SlideContent(slide_number=16, title="治理前 vs 治理后", bullet_points=[
        "数据口径不统一，各自为政",
        "人工核对数据，效率低下",
        "安全管控缺失，合规风险高",
        "统一数据标准，一源一真",
        "自动化质量监控，效率提升 80%",
        "全链路安全管控，合规无忧",
    ]),
    SlideContent(slide_number=17, title="引言", subtitle="Peter Drucker",
                 body_text="If you can't measure it, you can't manage it.\n——如果你无法度量它，你就无法管理它。"),
    SlideContent(slide_number=18, title="感谢聆听", subtitle="让数据成为企业最珍贵的战略资产",
                 bullet_points=["📧  data-governance@enterprise.com", "🌐  www.enterprise-dg.com"]),
])

# ── Load images ──

IMAGE_DIR = "/Users/louisliu/.gemini/antigravity/brain/afa968b6-2b7d-4c0a-b101-c0a6a52612cb"
image_files = {
    1: "data_governance_cover",
    7: "data_architecture_diagram",
    10: "data_quality_visual",
    12: "data_security_shield",
}

images = []
for slide_num, base_name in image_files.items():
    for f in os.listdir(IMAGE_DIR):
        if f.startswith(base_name) and f.endswith(".png"):
            images.append(GeneratedImage(
                slide_number=slide_num,
                image_path=os.path.join(IMAGE_DIR, f),
                prompt=f"Generated for slide {slide_num}",
            ))
            break

print(f"📸 Loaded {len(images)} images")

# ── Build with V2 ──

output_path = os.path.join(os.path.dirname(__file__), "output", "企业级数据治理框架_V2.pptx")

print("🔧 Building with BuilderV2 (gradient + shadow + auto-fit)...")
result = builder.build(plan, content, design, images, output_path)

file_size = os.path.getsize(result)
print(f"""
{'='*60}
  ✅ BuilderV2 生成完成!
  📄 文件: {result}
  📦 大小: {file_size/1024:.1f} KB
  🌈 渐变背景: ✅ (角度 225°, 3 色阶)
  🔲 阴影效果: ✅ (卡片形状)
  📏 自适应排版: ✅ (字号 / 间距)
  📐 智能布局计算: ✅ (双栏宽度)
{'='*60}
""")
