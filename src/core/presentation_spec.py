"""Semantic slide spec normalization and content fitting utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from src.data.models import Outline, SlideItem, SlideType


LAYOUT_ITEM_BUDGETS = {
    "title_hero": 1,
    "agenda": 6,
    "section_break": 1,
    "content_2col": 4,
    "content_image_right": 4,
    "stats_highlight": 3,
    "kpi_grid": 4,
    "chart_focus": 4,
    "comparison_before_after": 3,
    "decision_matrix": 4,
    "process_flow": 5,
    "table_summary": 6,
    "closing_cta": 2,
}


@dataclass
class FitResult:
    """Result of content fitting prior to rendering."""

    title_size: int = 30
    subtitle_size: int = 18
    body_size: int = 18
    stat_value_size: int = 28
    layout_variant: str = "content_2col"
    warnings: List[str] = field(default_factory=list)
    trimmed_bullets: List[str] = field(default_factory=list)
    trimmed_sections: List[dict] = field(default_factory=list)
    trim_applied: bool = False
    fallback_to_text: bool = False
    visible_bullets: List[str] = field(default_factory=list)
    visible_stats: List[dict] = field(default_factory=list)
    visible_sections: List[dict] = field(default_factory=list)
    visible_table_rows: List[list] = field(default_factory=list)
    visible_chart_spec: Dict[str, object] | None = None
    overflow_notice: str = ""
    requires_manual_review: bool = False


def normalize_outline(outline: Outline) -> Outline:
    """Normalize an outline in-place for schema v2 rendering."""
    outline.schema_version = "2.0"
    for slide in outline.slides:
        normalize_slide_item(slide)
    return outline


def normalize_slide_item(slide: SlideItem) -> SlideItem:
    """Populate semantic defaults for a single slide item."""
    if not slide.bullets and slide.content:
        slide.bullets = [item for item in slide.content if item.strip()]
    if not slide.content and slide.bullets:
        slide.content = slide.bullets.copy()
    if slide.layout_variant == "agenda" and not slide.summary:
        slide.summary = "Presentation roadmap"
    if slide.layout_variant == "section_break" and not slide.key_message:
        slide.key_message = slide.summary or slide.subtitle or (slide.bullets[0] if slide.bullets else "")
    if slide.layout_variant == "closing_cta" and not slide.key_message:
        slide.key_message = slide.summary or (slide.bullets[0] if slide.bullets else "")
    if slide.layout_variant == "stats_highlight" and not slide.stats and slide.bullets:
        slide.stats = [{"label": f"Metric {index + 1}", "value": bullet, "insight": ""} for index, bullet in enumerate(slide.bullets[:3])]
    if slide.layout_variant == "kpi_grid" and not slide.stats and slide.bullets:
        slide.stats = [{"label": f"KPI {index + 1}", "value": bullet, "insight": ""} for index, bullet in enumerate(slide.bullets[:4])]
    if slide.layout_variant == "chart_focus" and not slide.chart_spec:
        if slide.stats:
            slide.chart_spec = {
                "type": "bar",
                "series": [
                    {"label": stat.get("label", f"Metric {index + 1}"), "value": index + 1}
                    for index, stat in enumerate(slide.stats[:4])
                ],
                "insight": slide.key_message or slide.summary,
            }
        elif slide.bullets:
            slide.chart_spec = {
                "type": "bar",
                "series": [{"label": bullet[:24], "value": index + 1} for index, bullet in enumerate(slide.bullets[:4])],
                "insight": slide.key_message or slide.summary,
            }
    if slide.layout_variant == "comparison_before_after" and not slide.sections:
        left = slide.diagram.get("before", {}) if slide.diagram else {}
        right = slide.diagram.get("after", {}) if slide.diagram else {}
        sections = []
        if left:
            sections.append(
                {
                    "title": left.get("title", "Before"),
                    "items": [node.get("text", "") for node in left.get("nodes", []) if node.get("text")],
                    "tone": "before",
                }
            )
        if right:
            sections.append(
                {
                    "title": right.get("title", "After"),
                    "items": [node.get("text", "") for node in right.get("nodes", []) if node.get("text")],
                    "tone": "after",
                }
            )
        if not sections and slide.bullets:
            midpoint = max(1, len(slide.bullets) // 2)
            sections = [
                {"title": "Before", "items": slide.bullets[:midpoint], "tone": "before"},
                {"title": "After", "items": slide.bullets[midpoint: midpoint * 2], "tone": "after"},
            ]
        slide.sections = sections
    if slide.layout_variant == "decision_matrix" and not slide.sections:
        matrix_items = slide.diagram.get("quadrants", []) if slide.diagram else []
        if matrix_items:
            slide.sections = matrix_items[:4]
        elif slide.bullets:
            quadrants = ["Quick Wins", "Strategic Bets", "Low Priority", "Watchlist"]
            slide.sections = [
                {"title": quadrants[index], "items": [item], "tone": "matrix"}
                for index, item in enumerate(slide.bullets[:4])
            ]
    if slide.layout_variant == "process_flow" and not slide.sections:
        nodes = slide.diagram.get("nodes", []) if slide.diagram else []
        items = [node.get("text", "") for node in nodes if node.get("text")]
        if not items:
            items = slide.bullets[:5]
        slide.sections = [{"title": "Steps", "items": items, "tone": "process"}]
    if slide.layout_variant == "table_summary" and not slide.table_spec:
        rows = []
        if slide.sections:
            for section in slide.sections[:5]:
                first_item = section.get("items", [""])
                rows.append([section.get("title", ""), first_item[0] if first_item else ""])
        elif slide.bullets:
            rows = [[f"Row {index + 1}", bullet] for index, bullet in enumerate(slide.bullets[:5])]
        if rows:
            slide.table_spec = {"headers": ["Category", "Summary"], "rows": rows}

    if slide.slide_type == SlideType.CONTENT and slide.layout_variant == "content_2col" and slide.image_prompt:
        slide.layout_variant = "content_image_right"
    if slide.slide_type == SlideType.TITLE:
        slide.layout_variant = "title_hero"
    elif slide.slide_type == SlideType.CLOSING:
        slide.layout_variant = "closing_cta"
    elif slide.slide_type == SlideType.SECTION:
        slide.layout_variant = "section_break"
    elif slide.slide_type == SlideType.COMPARISON and slide.layout_variant == "content_2col":
        slide.layout_variant = "comparison_before_after"
    elif slide.slide_type == SlideType.DIAGRAM and slide.layout_variant == "content_2col":
        slide.layout_variant = "process_flow"
    return slide


def fit_slide_content(slide: SlideItem) -> Tuple[SlideItem, FitResult]:
    """Return a normalized slide and a fit profile for rendering."""
    normalize_slide_item(slide)
    fit = FitResult(layout_variant=slide.layout_variant)

    title_length = len(slide.title or "")
    if title_length > 80:
        fit.title_size = 24
        fit.subtitle_size = 15
        fit.warnings.append("Title compressed for readability.")
    elif title_length > 50:
        fit.title_size = 27

    max_bullets = LAYOUT_ITEM_BUDGETS.get(slide.layout_variant, 4)
    bullets = slide.normalized_bullets
    fit.visible_bullets = bullets.copy()
    fit.visible_stats = [dict(stat) for stat in slide.stats]
    fit.visible_sections = [dict(section) for section in slide.sections]
    fit.visible_chart_spec = dict(slide.chart_spec) if slide.chart_spec else None
    fit.visible_table_rows = [list(row) for row in slide.table_spec.get("rows", [])] if slide.table_spec else []

    if any(len(point) > 120 for point in bullets):
        fit.body_size = 16
        fit.warnings.append("Long bullet text reduced in size.")
    if len(bullets) > max_bullets and slide.layout_variant in {"content_2col", "content_image_right", "agenda", "closing_cta"}:
        fit.visible_bullets = bullets[:max_bullets]
        fit.trimmed_bullets = bullets[max_bullets:]
        fit.trim_applied = True
        fit.requires_manual_review = True
        fit.overflow_notice = "Slide có nhiều ý hơn sức chứa an toàn. Cần tách slide hoặc rút gọn thêm."
        fit.warnings.append("Content exceeds layout budget; only a visible summary will be rendered.")

    if slide.layout_variant == "stats_highlight" and len(slide.stats) > 3:
        fit.trimmed_sections = [{"label": stat.get("label", ""), "value": stat.get("value", "")} for stat in slide.stats[3:]]
        fit.visible_stats = [dict(stat) for stat in slide.stats[:3]]
        fit.trim_applied = True
        fit.requires_manual_review = True
        fit.overflow_notice = "Slide KPI đang bị nén. Cân nhắc tách thêm slide số liệu."
        fit.warnings.append("Extra stats will not be shown on-slide.")
    if slide.layout_variant == "kpi_grid" and len(slide.stats) > 4:
        fit.trimmed_sections = [{"label": stat.get("label", ""), "value": stat.get("value", "")} for stat in slide.stats[4:]]
        fit.visible_stats = [dict(stat) for stat in slide.stats[:4]]
        fit.trim_applied = True
        fit.requires_manual_review = True
        fit.overflow_notice = "KPI grid vượt ngân sách hiển thị. Cần rút gọn hoặc chia slide."
        fit.warnings.append("Extra KPIs will not be shown on-slide.")
    if slide.layout_variant == "chart_focus" and slide.chart_spec:
        fit.visible_chart_spec = dict(slide.chart_spec)
        series = list(fit.visible_chart_spec.get("series", []))
        series_groups = list(fit.visible_chart_spec.get("series_groups", []))
        if len(series) > 6:
            fit.trim_applied = True
            fit.requires_manual_review = True
            fit.overflow_notice = "Biểu đồ có quá nhiều điểm dữ liệu cho một slide."
            fit.warnings.append("Chart data exceeds the safe point budget.")
            fit.trimmed_sections.append({"title": "Chart points", "items": [str(item) for item in series[6:]]})
            fit.visible_chart_spec["series"] = series[:6]
        if len(series_groups) > 2:
            fit.trim_applied = True
            fit.requires_manual_review = True
            fit.overflow_notice = "Biểu đồ có quá nhiều nhóm dữ liệu cho một slide."
            fit.warnings.append("Chart series groups exceed the safe limit.")
            fit.trimmed_sections.append({"title": "Chart series", "items": [str(item.get('name', 'Series')) for item in series_groups[2:]]})
            fit.visible_chart_spec["series_groups"] = series_groups[:2]

    if slide.layout_variant == "comparison_before_after":
        normalized_sections = []
        for section in slide.sections[:2]:
            items = list(section.get("items", []))
            if len(items) > 3:
                fit.trim_applied = True
                fit.requires_manual_review = True
                fit.overflow_notice = "Slide so sánh có quá nhiều ý trên mỗi cột."
                fit.warnings.append("Comparison content exceeds the safe item budget.")
                fit.trimmed_sections.append({"title": section.get("title", ""), "items": items[3:]})
                items = items[:3]
            normalized_sections.append({**section, "items": items})
        fit.visible_sections = normalized_sections

    if slide.layout_variant == "decision_matrix":
        normalized_sections = []
        for section in slide.sections[:4]:
            items = list(section.get("items", []))
            if len(items) > 2:
                fit.trim_applied = True
                fit.requires_manual_review = True
                fit.overflow_notice = "Decision matrix có quá nhiều item trong một quadrant."
                fit.warnings.append("Decision matrix content exceeds the safe item budget.")
                fit.trimmed_sections.append({"title": section.get("title", ""), "items": items[2:]})
                items = items[:2]
            normalized_sections.append({**section, "items": items})
        fit.visible_sections = normalized_sections

    if slide.layout_variant == "process_flow":
        items = list(slide.sections[0].get("items", [])) if slide.sections else []
        if len(items) > 5:
            fit.trim_applied = True
            fit.trimmed_sections.append({"title": "Steps", "items": items[5:]})
            fit.requires_manual_review = True
            fit.overflow_notice = "Process flow có quá nhiều bước cho một slide."
            fit.warnings.append("Process steps exceed the safe diagram budget.")
            fit.visible_sections = [{**slide.sections[0], "items": items[:5]}]

    if slide.layout_variant == "table_summary" and slide.table_spec:
        rows = list(slide.table_spec.get("rows", []))
        if len(rows) > 5:
            fit.trim_applied = True
            fit.requires_manual_review = True
            fit.overflow_notice = "Bảng có quá nhiều dòng cho một slide."
            fit.warnings.append("Table rows exceed the safe slide budget.")
            fit.trimmed_sections.append({"title": "Table rows", "items": [str(row) for row in rows[5:]]})
            fit.visible_table_rows = [list(row) for row in rows[:5]]

    if fit.trimmed_bullets or fit.trimmed_sections:
        extra_lines = []
        if fit.trimmed_bullets:
            extra_lines.append("Additional points: " + "; ".join(fit.trimmed_bullets))
        if fit.trimmed_sections:
            for section in fit.trimmed_sections:
                items = section.get("items", [])
                if items:
                    extra_lines.append(f"{section.get('title', 'Extra')}: " + "; ".join(items))
        notes = [slide.speaker_notes.strip(), slide.notes_short.strip(), " ".join(extra_lines).strip()]
        merged = "\n".join(line for line in notes if line)
        slide.speaker_notes = merged
        slide.notes_short = merged
        if fit.overflow_notice:
            slide.notes_short = "\n".join(line for line in [fit.overflow_notice, slide.notes_short] if line)
            slide.speaker_notes = slide.notes_short

    slide.render_warnings = fit.warnings.copy()
    return slide, fit
