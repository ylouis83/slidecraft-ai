"""
SlideCraft-AI 全流程 LLM 驱动生成管线
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

使用阿里云百炼 (Bailian) API 接入 Qwen 系列最强模型：
  • Planner:  qwen3-max  → 内容架构规划
  • Writer:   qwen3-max  → 专业文案撰写
  • Designer: qwen-plus   → 视觉设计方案
  • Reviewer:  qwen3-max  → 质量评审优化
  • Builder:  BuilderV2  → 渲染引擎组装

百炼 API 兼容 OpenAI 接口，base_url:
  https://dashscope.aliyuncs.com/compatible-mode/v1
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from openai import OpenAI

from slidecraft.agents.builder_v2 import BuilderV2Agent
from slidecraft.config import SlideCraftConfig
from slidecraft.models import (
    ColorPalette,
    DesignSpec,
    DesignStyle,
    FontScheme,
    GeneratedImage,
    PresentationContent,
    PresentationPlan,
    SlideContent,
    SlideOutline,
    SlideType,
)

# ══════════════════════════════════════════════════════════════
#  Configuration
# ══════════════════════════════════════════════════════════════

BAILIAN_API_KEY = os.getenv("BAILIAN_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Model selection per agent role
MODELS = {
    "planner":  "qwen3-max",     # 旗舰推理模型 — 最强结构化思考
    "writer":   "qwen3-max",     # 旗舰模型 — 最好的文案质量
    "designer": "qwen-plus",     # 均衡模型 — 设计方案生成
    "reviewer": "qwen3-max",     # 旗舰模型 — 质量审查
}

TOPIC = "企业级数据治理框架"
DESCRIPTION = """请生成一份面向 CTO/CDO/数据管理负责人的企业级数据治理框架 PPT。

要求覆盖以下关键内容：
1. 数据治理的定义、目标与价值主张
2. 当前企业数据管理面临的核心挑战（数据孤岛、质量、合规等）
3. 完整的治理框架架构（战略层、组织层、制度层、技术层、运营层）
4. 治理组织架构与角色定义（CDO、DMO、Data Steward等）
5. 核心治理能力：数据质量管理、元数据管理、数据安全与合规
6. 数据治理成熟度模型（含数据图表）
7. 实施路线图（分阶段里程碑）
8. 治理前后效果对比
9. 国际标准参考（DAMA-DMBOK、ISO 8000、DCMM）

风格要求：专业严谨、逻辑清晰、内容充实、适合高管汇报
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("pipeline")


# ══════════════════════════════════════════════════════════════
#  LLM Calling Utilities
# ══════════════════════════════════════════════════════════════

if not BAILIAN_API_KEY:
    raise RuntimeError(
        "Missing API key. Please set BAILIAN_API_KEY (or OPENAI_API_KEY) in environment."
    )

client = OpenAI(api_key=BAILIAN_API_KEY, base_url=BAILIAN_BASE_URL)


def call_llm(role: str, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """Call a Bailian LLM model with the given prompts."""
    model = MODELS[role]
    log.info(f"🤖 [{role.upper()}] 调用模型 {model}...")

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=8192,
    )
    elapsed = time.time() - start

    content = response.content if hasattr(response, 'content') else ""
    if hasattr(response, 'choices') and response.choices:
        msg = response.choices[0].message
        # qwen3-max may include <think>...</think> reasoning blocks
        content = msg.content or ""
        # Strip thinking blocks if present
        if "<think>" in content:
            import re
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    tokens = response.usage.total_tokens if response.usage else 0
    log.info(f"   ✅ 完成 ({elapsed:.1f}s, {tokens} tokens)")
    return content


def extract_json(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    raw = raw.strip()
    # Remove markdown code block wrappers
    if "```json" in raw:
        start = raw.index("```json") + 7
        end = raw.index("```", start)
        raw = raw[start:end].strip()
    elif "```" in raw:
        start = raw.index("```") + 3
        # Skip language identifier if on same line
        if "\n" in raw[start:start + 20]:
            start = raw.index("\n", start) + 1
        end = raw.index("```", start)
        raw = raw[start:end].strip()
    return json.loads(raw)


# ══════════════════════════════════════════════════════════════
#  Agent 1: PLANNER — 内容架构规划
# ══════════════════════════════════════════════════════════════

def run_planner() -> PresentationPlan:
    """Use qwen3-max to plan the presentation structure."""
    log.info("━" * 60)
    log.info("📋 PHASE 1: PLANNER AGENT")
    log.info("━" * 60)

    system_prompt = """你是 SlideCraft-AI 的内容规划师（Planner Agent），专门负责设计 PPT 的整体结构和内容大纲。

## 你的专长
- 信息架构设计、叙事设计与故事线构建
- 受众分析与内容策略
- 视觉叙事规划

## 你的任务
根据用户需求，产出一份详细的 PPT 大纲。

## 设计原则
- **金字塔原理** - 先总后分，层层递进
- **MECE** - 相互独立、完全穷尽
- **一页一主题** - 每张幻灯片聚焦一个核心观点
- **节奏感** - 内容页之间穿插视觉页
- **视觉优先** - 善用图表和配图

## 可用的幻灯片类型
- cover: 封面
- toc: 目录
- section: 章节标题页
- content: 内容页（标题+要点列表）
- two_column: 双栏对比
- image_full: 全屏图片页
- image_text: 图文混排
- chart: 数据图表页
- comparison: 对比分析
- timeline: 时间线/路线图
- quote: 引用名言
- thank_you: 感谢结束页

## 输出格式
请以 JSON 格式返回，结构如下：
```json
{
  "title": "PPT主标题",
  "subtitle": "副标题",
  "narrative_arc": "整体叙事主线描述",
  "target_audience": "目标受众",
  "slides": [
    {
      "slide_number": 1,
      "slide_type": "cover",
      "title": "幻灯片标题",
      "key_points": ["要点1", "要点2"],
      "notes": "演讲者备注",
      "needs_image": true,
      "image_description": "配图描述（英文，用于AI生图）",
      "needs_chart": false,
      "chart_description": ""
    }
  ]
}
```

只返回 JSON，不要包含其他内容。"""

    user_prompt = f"""请为以下需求规划一份 PPT 大纲：

## 需求信息
- **主题**: {TOPIC}
- **详细描述**: {DESCRIPTION}
- **目标受众**: CTO / CDO / 数据管理负责人
- **幻灯片数量**: 18-22张
- **设计风格**: dark（深色科技风）
- **语言**: 中文

请产出完整的规划，确保：
1. 包含 18-22 张幻灯片
2. 合理使用所有可用的幻灯片类型
3. 内容充实、逻辑严谨
4. 标注哪些页面需要配图(needs_image=true)并提供英文图片描述
5. 标注哪些页面需要图表(needs_chart=true)并描述图表数据"""

    raw = call_llm("planner", system_prompt, user_prompt, temperature=0.7)
    data = extract_json(raw)
    plan = PresentationPlan.model_validate(data)
    log.info(f"   📊 规划完成: {len(plan.slides)} 张幻灯片")
    log.info(f"   📖 叙事主线: {plan.narrative_arc[:80]}...")
    return plan


# ══════════════════════════════════════════════════════════════
#  Agent 2: WRITER — 专业文案撰写
# ══════════════════════════════════════════════════════════════

def run_writer(plan: PresentationPlan) -> PresentationContent:
    """Use qwen3-max to write content for all slides."""
    log.info("")
    log.info("━" * 60)
    log.info("✍️  PHASE 2: WRITER AGENT")
    log.info("━" * 60)

    system_prompt = """你是 SlideCraft-AI 的文案撰写师（Writer Agent），负责为每张幻灯片撰写精炼、专业的内容。

## 你的专长
- 企业级业务文档撰写
- 数据治理、IT治理领域专业知识
- 简洁有力的表达，适合高管阅读
- 演讲者备注撰写

## 写作原则
- **精炼** - 每个要点控制在 25 字以内
- **专业** - 使用行业标准术语
- **可演讲** - 内容适合口头讲解
- **层次分明** - 用 emoji 图标增强视觉层次

## 特殊页面要求
- **chart 页**: 必须提供 data 字段，包含 labels、values、series_name
- **quote 页**: body_text 放名言内容，subtitle 放署名
- **comparison 页**: bullet_points 前半部分是方案A，后半部分是方案B
- **timeline 页**: 每个 bullet_point 代表一个里程碑
- **two_column 页**: bullet_points 前半是左栏，后半是右栏

## 输出格式
```json
{
  "slides": [
    {
      "slide_number": 1,
      "title": "标题",
      "subtitle": "副标题",
      "body_text": "正文（引用页用）",
      "bullet_points": ["要点1", "要点2"],
      "notes": "演讲者备注（每页都要写）",
      "data": null  // 或 {"labels": [...], "values": [...], "series_name": "..."}
    }
  ]
}
```
只返回 JSON。"""

    slides_info = json.dumps(
        [{"slide_number": s.slide_number, "slide_type": s.slide_type.value,
          "title": s.title, "key_points": s.key_points, "needs_chart": s.needs_chart,
          "chart_description": s.chart_description}
         for s in plan.slides],
        ensure_ascii=False, indent=2,
    )

    user_prompt = f"""请为以下 PPT 大纲撰写每一页的详细内容。

## PPT 信息
- **标题**: {plan.title}
- **副标题**: {plan.subtitle}
- **叙事主线**: {plan.narrative_arc}
- **受众**: {plan.target_audience}

## 幻灯片大纲
```json
{slides_info}
```

## 要求
1. 为每张幻灯片撰写完整内容
2. 每个 content 页面至少 4-6 个 bullet_points
3. chart 页面必须提供真实的数据 (data 字段)
4. 每页都要写演讲者备注 (notes)
5. 内容要专业、充实、有深度
6. 善用 emoji 图标增强可读性（如 🏗️ ⚙️ 📊 🔒 等）"""

    raw = call_llm("writer", system_prompt, user_prompt, temperature=0.6)
    data = extract_json(raw)
    content = PresentationContent.model_validate(data)
    log.info(f"   ✅ 文案完成: {len(content.slides)} 页内容")

    # Validate chart slides have data
    for sc in content.slides:
        slide_outline = next((s for s in plan.slides if s.slide_number == sc.slide_number), None)
        if slide_outline and slide_outline.slide_type == SlideType.CHART and not sc.data:
            log.warning(f"   ⚠️  Slide {sc.slide_number} is chart type but missing data, adding fallback")
            sc.data = {
                "labels": ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
                "values": [20, 40, 60, 80, 95],
                "series_name": "成熟度评分",
            }

    return content


# ══════════════════════════════════════════════════════════════
#  Agent 3: DESIGNER — 视觉设计方案
# ══════════════════════════════════════════════════════════════

def run_designer(plan: PresentationPlan) -> DesignSpec:
    """Use qwen-plus to create visual design specification."""
    log.info("")
    log.info("━" * 60)
    log.info("🎨 PHASE 3: DESIGNER AGENT")
    log.info("━" * 60)

    system_prompt = """你是 SlideCraft-AI 的视觉设计师（Designer Agent），负责设计 PPT 的完整视觉方案。

## 你的专长
- 色彩理论与配色方案设计
- 企业级演示文档的视觉设计
- 深色主题设计 (Dark Mode)
- 专业感与科技感的平衡

## 配色要求
针对深色科技风格，请设计和谐的 7 色配色方案：
- primary: 主色（用于标题、重要元素、装饰）
- secondary: 辅色（用于图表、次要元素）
- accent: 强调色（用于CTA、亮点突出）
- background: 背景色（深色系，如 #0f172a 或 #111827）
- surface: 表面色（卡片/区块底色，略浅于背景）
- text_primary: 主文字色（确保高对比度，如 #f1f5f9）
- text_secondary: 次要文字色

## 输出格式
```json
{
  "style": "dark",
  "colors": {
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "surface": "#hex",
    "text_primary": "#hex",
    "text_secondary": "#hex"
  },
  "fonts": {
    "title_font": "字体名称",
    "body_font": "字体名称",
    "title_size_pt": 36,
    "subtitle_size_pt": 22,
    "body_size_pt": 18,
    "caption_size_pt": 14
  },
  "use_gradient_backgrounds": true
}
```
只返回 JSON。"""

    user_prompt = f"""请为以下 PPT 设计视觉方案：

## PPT 信息
- **标题**: {plan.title}
- **副标题**: {plan.subtitle}
- **风格**: 深色科技风 (Dark Tech)
- **受众**: CTO / CDO / 数据管理负责人
- **页数**: {len(plan.slides)} 页

## 设计要求
1. 配色要高级、专业、有科技感
2. 背景色要深色系
3. 主色要有辨识度，避免过于普通
4. 使用渐变背景 (use_gradient_backgrounds: true)
5. 确保文字在深色背景上有足够对比度
6. 字体选择适合中文显示的字体"""

    raw = call_llm("designer", system_prompt, user_prompt, temperature=0.5)
    data = extract_json(raw)

    # Build DesignSpec from LLM response
    design = DesignSpec(
        style=DesignStyle.DARK,
        colors=ColorPalette(**data.get("colors", {})),
        fonts=FontScheme(**data.get("fonts", {})),
        use_gradient_backgrounds=data.get("use_gradient_backgrounds", True),
    )

    log.info(f"   🎨 配色: primary={design.colors.primary}, secondary={design.colors.secondary}")
    log.info(f"   🎨 accent={design.colors.accent}, bg={design.colors.background}")
    log.info(f"   🔤 字体: {design.fonts.title_font}")

    return design


# ══════════════════════════════════════════════════════════════
#  Agent 4: REVIEWER — 质量评审
# ══════════════════════════════════════════════════════════════

def run_reviewer(plan: PresentationPlan, content: PresentationContent, design: DesignSpec) -> dict:
    """Use qwen3-max to review and suggest improvements."""
    log.info("")
    log.info("━" * 60)
    log.info("🔍 PHASE 5: REVIEWER AGENT")
    log.info("━" * 60)

    system_prompt = """你是 SlideCraft-AI 的质量审查官（Reviewer Agent），负责对 PPT 进行全面的质量评审。

## 评审维度
1. **内容质量** (0-10): 专业度、准确性、深度、完整性
2. **设计质量** (0-10): 配色、排版、视觉层次
3. **逻辑连贯** (0-10): 叙事流畅性、结构清晰度
4. **综合评分** (0-10): 加权平均

## 输出格式
```json
{
  "overall_score": 8.5,
  "content_score": 9.0,
  "design_score": 8.0,
  "coherence_score": 8.5,
  "approved": true,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"],
  "highlights": ["亮点1", "亮点2"]
}
```
只返回 JSON。"""

    slides_summary = "\n".join([
        f"  {sc.slide_number}. [{next((s.slide_type.value for s in plan.slides if s.slide_number == sc.slide_number), '?')}] {sc.title}"
        + (f" ({len(sc.bullet_points)} points)" if sc.bullet_points else "")
        for sc in content.slides
    ])

    user_prompt = f"""请评审以下 PPT 方案的整体质量。

## PPT 概览
- **标题**: {plan.title}
- **受众**: {plan.target_audience}
- **页数**: {len(plan.slides)} 页
- **配色**: {design.colors.primary} / {design.colors.secondary} / {design.colors.accent}

## 内容概览
{slides_summary}

## 叙事主线
{plan.narrative_arc}

## 部分内容示例
{json.dumps([sc.model_dump() for sc in content.slides[:4]], ensure_ascii=False, indent=2)[:3000]}

请给出详细的评审意见。"""

    raw = call_llm("reviewer", system_prompt, user_prompt, temperature=0.3)
    data = extract_json(raw)
    return data


# ══════════════════════════════════════════════════════════════
#  Main Pipeline
# ══════════════════════════════════════════════════════════════

def main():
    total_start = time.time()

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🚀  SlideCraft-AI · LLM 全流程生成管线               ║
║                                                              ║
║        📡  API: 阿里云百炼 (Bailian)                         ║
║        🤖  模型: qwen3-max / qwen-plus                      ║
║        📊  主题: 企业级数据治理框架                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # ── Phase 1: PLANNER ──
    plan = run_planner()

    # ── Phase 2: WRITER ──
    content = run_writer(plan)

    # ── Phase 3: DESIGNER ──
    design = run_designer(plan)

    # ── Phase 4: IMAGE LOADING ──
    log.info("")
    log.info("━" * 60)
    log.info("🖼️  PHASE 4: IMAGE AGENT (使用已生成的AI配图)")
    log.info("━" * 60)

    IMAGE_DIR = "/Users/louisliu/.gemini/antigravity/brain/afa968b6-2b7d-4c0a-b101-c0a6a52612cb"
    available_images = {
        "data_governance_cover": None,
        "data_architecture_diagram": None,
        "data_quality_visual": None,
        "data_security_shield": None,
    }

    for f in os.listdir(IMAGE_DIR):
        for key in available_images:
            if f.startswith(key) and f.endswith(".png"):
                available_images[key] = os.path.join(IMAGE_DIR, f)

    # Map images to slides that need them
    images = []
    for slide in plan.slides:
        if slide.needs_image:
            img_path = None
            desc_lower = slide.image_description.lower() if slide.image_description else ""
            title_lower = slide.title.lower()

            # Smart matching
            if slide.slide_type == SlideType.COVER:
                img_path = available_images.get("data_governance_cover")
            elif "架构" in slide.title or "architecture" in desc_lower or "framework" in desc_lower:
                img_path = available_images.get("data_architecture_diagram")
            elif "质量" in slide.title or "quality" in desc_lower:
                img_path = available_images.get("data_quality_visual")
            elif "安全" in slide.title or "security" in desc_lower or "合规" in slide.title:
                img_path = available_images.get("data_security_shield")

            if img_path:
                images.append(GeneratedImage(
                    slide_number=slide.slide_number,
                    image_path=img_path,
                    prompt_used=slide.image_description,
                ))
                log.info(f"   🖼️  Slide {slide.slide_number}: {os.path.basename(img_path)}")

    log.info(f"   📸 匹配到 {len(images)} 张配图")

    # ── Phase 5: BUILDER V2 ──
    log.info("")
    log.info("━" * 60)
    log.info("🔧 PHASE 5: BUILDER V2 AGENT (渲染引擎)")
    log.info("━" * 60)

    config = SlideCraftConfig()
    builder = BuilderV2Agent(config)

    output_path = os.path.join(
        os.path.dirname(__file__), "output",
        "企业级数据治理框架_LLM.pptx",
    )

    build_start = time.time()
    result = builder.build(plan, content, design, images, output_path)
    build_time = time.time() - build_start
    log.info(f"   ✅ PPT 构建完成 ({build_time:.1f}s)")

    # ── Phase 6: REVIEWER ──
    review = run_reviewer(plan, content, design)

    # ── Summary ──
    total_time = time.time() - total_start
    file_size = os.path.getsize(result)

    print(f"""
{'═' * 62}

  🎉  SlideCraft-AI · LLM 全流程生成完成!

  📄  文件: {result}
  📦  大小: {file_size / 1024:.1f} KB
  📊  页数: {len(plan.slides)} 张幻灯片
  🖼️   配图: {len(images)} 张 AI 生成图片
  ⏱️   总耗时: {total_time:.1f}s

  🤖  模型调用:
      • Planner:  {MODELS['planner']} → {len(plan.slides)} 页结构
      • Writer:   {MODELS['writer']} → {len(content.slides)} 页文案
      • Designer: {MODELS['designer']} → 配色 + 字体方案
      • Reviewer:  {MODELS['reviewer']} → 质量评审

  🎨  设计方案:
      • Primary:   {design.colors.primary}
      • Secondary: {design.colors.secondary}
      • Accent:    {design.colors.accent}
      • Background: {design.colors.background}
      • 渐变背景: ✅  阴影效果: ✅  自适应排版: ✅

  📋  REVIEWER 评审报告:
      ┌─────────────────────────────────────┐
      │  内容质量: {review.get('content_score', 'N/A')}/10                   │
      │  设计质量: {review.get('design_score', 'N/A')}/10                   │
      │  逻辑连贯: {review.get('coherence_score', 'N/A')}/10                   │
      │  综合评分: {review.get('overall_score', 'N/A')}/10                   │
      │  审核结果: {'✅ APPROVED' if review.get('approved') else '⚠️ NEEDS REVISION'}   │
      └─────────────────────────────────────┘
""")

    if review.get("highlights"):
        print("  ✨ 亮点:")
        for h in review["highlights"][:5]:
            print(f"      • {h}")

    if review.get("suggestions"):
        print("\n  💡 改进建议:")
        for s in review["suggestions"][:5]:
            print(f"      • {s}")

    print(f"\n{'═' * 62}\n")

    # Save review report
    review_path = result.replace(".pptx", "_review.json")
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump({
            "plan_summary": {
                "title": plan.title,
                "subtitle": plan.subtitle,
                "narrative_arc": plan.narrative_arc,
                "slide_count": len(plan.slides),
            },
            "design_summary": {
                "style": design.style.value,
                "colors": design.colors.model_dump(),
                "fonts": design.fonts.model_dump(),
            },
            "review": review,
            "models_used": MODELS,
            "total_time_seconds": total_time,
        }, f, ensure_ascii=False, indent=2)
    log.info(f"📝 评审报告已保存: {review_path}")

    return result


if __name__ == "__main__":
    main()
