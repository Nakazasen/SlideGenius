"""Data models and semantic slide schema for SlideGenius."""
from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any, Dict, List, Optional


class SlideType(Enum):
    """Types of slides available."""

    TITLE = "title"
    CONTENT = "content"
    BULLET = "bullet"
    IMAGE_TEXT = "image_text"
    QUOTE = "quote"
    COMPARISON = "comparison"
    SECTION = "section"
    CLOSING = "closing"
    DIAGRAM = "diagram"


LAYOUT_VARIANTS = {
    "title_hero",
    "agenda",
    "section_break",
    "content_2col",
    "content_image_right",
    "stats_highlight",
    "kpi_grid",
    "chart_focus",
    "comparison_before_after",
    "decision_matrix",
    "process_flow",
    "table_summary",
    "closing_cta",
}


def _safe_list(value: Any) -> List[Any]:
    """Return a list for scalar or iterable inputs."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_text(value: Any) -> str:
    """Normalize scalar text values."""
    if value is None:
        return ""
    return str(value).strip()


def infer_layout_variant(data: Dict[str, Any], slide_type: SlideType) -> str:
    """Infer a stable layout variant from schema-v1 or partial schema-v2 payloads."""
    requested = _safe_text(data.get("layout_variant")).lower()
    if requested in LAYOUT_VARIANTS:
        return requested

    diagram = data.get("diagram") or {}
    diagram_type = _safe_text(diagram.get("type")).lower()

    if slide_type == SlideType.TITLE:
        return "title_hero"
    if slide_type == SlideType.CLOSING:
        return "closing_cta"
    if slide_type == SlideType.SECTION:
        return "section_break"
    if slide_type == SlideType.COMPARISON or diagram_type == "comparison":
        return "comparison_before_after"
    if slide_type == SlideType.DIAGRAM or diagram_type in {"process", "hierarchy", "cycle", "timeline"}:
        return "process_flow"
    if data.get("table_spec"):
        return "table_summary"
    if data.get("chart_spec"):
        return "chart_focus"
    if len(_safe_list(data.get("stats"))) >= 3:
        return "kpi_grid"
    if data.get("stats"):
        return "stats_highlight"
    if data.get("image_prompt") or data.get("image_path"):
        return "content_image_right"
    if any(len(_safe_text(point)) > 110 for point in _safe_list(data.get("content"))):
        return "content_2col"
    return "agenda" if _safe_text(data.get("title")).lower() in {"agenda", "mục lục"} else "content_2col"


def normalize_slide_type(layout_variant: str, original: str) -> SlideType:
    """Map layout variants and legacy values into stable slide types."""
    slide_type_str = _safe_text(original).lower()

    try:
        return SlideType(slide_type_str)
    except ValueError:
        pass

    if layout_variant == "title_hero":
        return SlideType.TITLE
    if layout_variant == "closing_cta":
        return SlideType.CLOSING
    if layout_variant == "section_break":
        return SlideType.SECTION
    if layout_variant == "comparison_before_after":
        return SlideType.COMPARISON
    if layout_variant == "process_flow":
        return SlideType.DIAGRAM
    if layout_variant == "content_image_right":
        return SlideType.IMAGE_TEXT
    if slide_type_str in ["process", "hierarchy", "cycle", "timeline", "mindmap", "structure"]:
        return SlideType.DIAGRAM
    return SlideType.CONTENT


@dataclass
class SlideItem:
    """Represents a single slide in the presentation."""

    title: str
    content: List[str] = field(default_factory=list)
    slide_type: SlideType = SlideType.CONTENT
    speaker_notes: str = ""
    image_prompt: Optional[str] = None
    image_path: Optional[str] = None
    diagram: Optional[dict] = None
    layout_variant: str = "content_2col"
    subtitle: str = ""
    summary: str = ""
    bullets: List[str] = field(default_factory=list)
    key_message: str = ""
    stats: List[dict] = field(default_factory=list)
    sections: List[dict] = field(default_factory=list)
    visual_intent: str = ""
    image_slots: List[dict] = field(default_factory=list)
    chart_spec: Optional[dict] = None
    table_spec: Optional[dict] = None
    emphasis_terms: List[str] = field(default_factory=list)
    notes_short: str = ""
    render_warnings: List[str] = field(default_factory=list)
    storyline_role: str = ""
    storyline_intent: str = ""
    rewritten: bool = False
    critique_notes: List[str] = field(default_factory=list)
    self_critique_applied: bool = False
    qa_flags: List[str] = field(default_factory=list)
    visual_treatment: str = ""
    density_level: str = ""
    micro_polish_applied: bool = False
    preview_density_score: float = 0.0
    remediation_variant: str = ""

    @property
    def normalized_bullets(self) -> List[str]:
        """Return semantic bullets, falling back to legacy content."""
        bullets = [item for item in self.bullets if _safe_text(item)]
        if bullets:
            return bullets
        return [item for item in self.content if _safe_text(item)]

    @property
    def semantic_preview(self) -> List[str]:
        """Return a short content preview for UI cards."""
        preview: List[str] = []
        if self.summary:
            preview.append(self.summary)
        if self.key_message:
            preview.append(self.key_message)
        if self.subtitle:
            preview.append(self.subtitle)
        preview.extend(self.normalized_bullets[:3])
        if self.stats and not preview:
            preview.extend(
                f"{_safe_text(stat.get('label', 'Stat'))}: {_safe_text(stat.get('value', ''))}"
                for stat in self.stats[:3]
            )
        return [item for item in preview if _safe_text(item)]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "slide_type": self.slide_type.value,
            "speaker_notes": self.speaker_notes,
            "image_prompt": self.image_prompt,
            "image_path": self.image_path,
            "diagram": self.diagram,
            "layout_variant": self.layout_variant,
            "subtitle": self.subtitle,
            "summary": self.summary,
            "bullets": self.bullets,
            "key_message": self.key_message,
            "stats": self.stats,
            "sections": self.sections,
            "visual_intent": self.visual_intent,
            "image_slots": self.image_slots,
            "chart_spec": self.chart_spec,
            "table_spec": self.table_spec,
            "emphasis_terms": self.emphasis_terms,
            "notes_short": self.notes_short,
            "render_warnings": self.render_warnings,
            "storyline_role": self.storyline_role,
            "storyline_intent": self.storyline_intent,
            "rewritten": self.rewritten,
            "critique_notes": self.critique_notes,
            "self_critique_applied": self.self_critique_applied,
            "qa_flags": self.qa_flags,
            "visual_treatment": self.visual_treatment,
            "density_level": self.density_level,
            "micro_polish_applied": self.micro_polish_applied,
            "preview_density_score": self.preview_density_score,
            "remediation_variant": self.remediation_variant,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlideItem":
        """Create SlideItem from dictionary with schema-v1 compatibility."""
        raw_content = _safe_list(data.get("content"))
        bullets = [_safe_text(item) for item in _safe_list(data.get("bullets")) if _safe_text(item)]
        content = [_safe_text(item) for item in raw_content if _safe_text(item)]
        if not bullets:
            bullets = content.copy()

        layout_variant = infer_layout_variant(data, SlideType.CONTENT)
        slide_type = normalize_slide_type(layout_variant, data.get("slide_type", "content"))
        # Re-infer once we know the true slide type.
        layout_variant = infer_layout_variant(data, slide_type)
        slide_type = normalize_slide_type(layout_variant, slide_type.value)

        subtitle = _safe_text(data.get("subtitle"))
        summary = _safe_text(data.get("summary"))
        key_message = _safe_text(data.get("key_message"))
        if not summary and slide_type in {SlideType.SECTION, SlideType.CLOSING, SlideType.TITLE}:
            summary = _safe_text(data.get("speaker_notes"))

        stats = [item for item in _safe_list(data.get("stats")) if isinstance(item, dict)]
        sections = [item for item in _safe_list(data.get("sections")) if isinstance(item, dict)]
        image_slots = [item for item in _safe_list(data.get("image_slots")) if isinstance(item, dict)]
        emphasis_terms = [_safe_text(item) for item in _safe_list(data.get("emphasis_terms")) if _safe_text(item)]
        render_warnings = [_safe_text(item) for item in _safe_list(data.get("render_warnings")) if _safe_text(item)]

        notes_short = _safe_text(data.get("notes_short"))
        speaker_notes = _safe_text(data.get("speaker_notes"))
        if not notes_short:
            notes_short = speaker_notes

        return cls(
            title=_safe_text(data.get("title", "")),
            content=content,
            slide_type=slide_type,
            speaker_notes=speaker_notes,
            image_prompt=_safe_text(data.get("image_prompt")) or None,
            image_path=_safe_text(data.get("image_path")) or None,
            diagram=data.get("diagram") if isinstance(data.get("diagram"), dict) else None,
            layout_variant=layout_variant,
            subtitle=subtitle,
            summary=summary,
            bullets=bullets,
            key_message=key_message,
            stats=stats,
            sections=sections,
            visual_intent=_safe_text(data.get("visual_intent")),
            image_slots=image_slots,
            chart_spec=data.get("chart_spec") if isinstance(data.get("chart_spec"), dict) else None,
            table_spec=data.get("table_spec") if isinstance(data.get("table_spec"), dict) else None,
            emphasis_terms=emphasis_terms,
            notes_short=notes_short,
            render_warnings=render_warnings,
            storyline_role=_safe_text(data.get("storyline_role")),
            storyline_intent=_safe_text(data.get("storyline_intent")),
            rewritten=bool(data.get("rewritten", False)),
            critique_notes=[_safe_text(item) for item in _safe_list(data.get("critique_notes")) if _safe_text(item)],
            self_critique_applied=bool(data.get("self_critique_applied", False)),
            qa_flags=[_safe_text(item) for item in _safe_list(data.get("qa_flags")) if _safe_text(item)],
            visual_treatment=_safe_text(data.get("visual_treatment")),
            density_level=_safe_text(data.get("density_level")),
            micro_polish_applied=bool(data.get("micro_polish_applied", False)),
            preview_density_score=float(data.get("preview_density_score", 0.0) or 0.0),
            remediation_variant=_safe_text(data.get("remediation_variant")),
        )


@dataclass
class Outline:
    """Represents a complete presentation outline."""

    title: str
    slides: List[SlideItem] = field(default_factory=list)
    language: str = "vi"
    schema_version: str = "2.0"
    quality_scores: Dict[str, int] = field(default_factory=dict)
    quality_flags: List[str] = field(default_factory=list)
    quality_summary: str = ""
    should_rewrite_again: bool = False
    quality_retry_count: int = 0
    candidate_count_generated: int = 1
    selected_candidate_index: int = 0
    candidate_scores: List[dict] = field(default_factory=list)
    selected_candidate_rationale: str = ""
    candidate_strategy: str = ""
    qa_findings: List[dict] = field(default_factory=list)
    qa_summary: str = ""
    preview_qa_applied: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "language": self.language,
            "schema_version": self.schema_version,
            "quality_scores": self.quality_scores,
            "quality_flags": self.quality_flags,
            "quality_summary": self.quality_summary,
            "should_rewrite_again": self.should_rewrite_again,
            "quality_retry_count": self.quality_retry_count,
            "candidate_count_generated": self.candidate_count_generated,
            "selected_candidate_index": self.selected_candidate_index,
            "candidate_scores": self.candidate_scores,
            "selected_candidate_rationale": self.selected_candidate_rationale,
            "candidate_strategy": self.candidate_strategy,
            "qa_findings": self.qa_findings,
            "qa_summary": self.qa_summary,
            "preview_qa_applied": self.preview_qa_applied,
            "slides": [s.to_dict() for s in self.slides],
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Outline":
        """Create Outline from dictionary."""
        slides = [SlideItem.from_dict(s) for s in data.get("slides", [])]
        schema_version = _safe_text(data.get("schema_version")) or "1.0"
        return cls(
            title=_safe_text(data.get("title", "Untitled")),
            slides=slides,
            language=_safe_text(data.get("language", "vi")) or "vi",
            schema_version=schema_version if schema_version else "1.0",
            quality_scores=data.get("quality_scores") if isinstance(data.get("quality_scores"), dict) else {},
            quality_flags=[_safe_text(item) for item in _safe_list(data.get("quality_flags")) if _safe_text(item)],
            quality_summary=_safe_text(data.get("quality_summary")),
            should_rewrite_again=bool(data.get("should_rewrite_again", False)),
            quality_retry_count=int(data.get("quality_retry_count", 0) or 0),
            candidate_count_generated=int(data.get("candidate_count_generated", 1) or 1),
            selected_candidate_index=int(data.get("selected_candidate_index", 0) or 0),
            candidate_scores=[item for item in _safe_list(data.get("candidate_scores")) if isinstance(item, dict)],
            selected_candidate_rationale=_safe_text(data.get("selected_candidate_rationale")),
            candidate_strategy=_safe_text(data.get("candidate_strategy")),
            qa_findings=[item for item in _safe_list(data.get("qa_findings")) if isinstance(item, dict)],
            qa_summary=_safe_text(data.get("qa_summary")),
            preview_qa_applied=bool(data.get("preview_qa_applied", False)),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Outline":
        """Create Outline from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_slide(self, slide: SlideItem) -> None:
        """Add a slide to the outline."""
        self.slides.append(slide)

    def remove_slide(self, index: int) -> None:
        """Remove slide at given index."""
        if 0 <= index < len(self.slides):
            self.slides.pop(index)

    def move_slide(self, from_index: int, to_index: int) -> None:
        """Move slide from one position to another."""
        if 0 <= from_index < len(self.slides) and 0 <= to_index < len(self.slides):
            slide = self.slides.pop(from_index)
            self.slides.insert(to_index, slide)

    @property
    def slide_count(self) -> int:
        """Get number of slides."""
        return len(self.slides)


@dataclass
class Template:
    """Represents a presentation template / theme."""

    name: str
    display_name: str
    description: str
    category: str
    primary_color: str = "#1D4ED8"
    secondary_color: str = "#0F172A"
    accent_color: str = "#EA580C"
    background_color: str = "#FFFFFF"
    surface_color: str = "#F8FAFC"
    muted_text_color: str = "#64748B"
    font_heading: str = "Arial"
    font_body: str = "Arial"
    title_scale: float = 1.0
    body_scale: float = 1.0
    corner_style: str = "rounded"
    accent_style: str = "bar"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "accent_color": self.accent_color,
            "background_color": self.background_color,
            "surface_color": self.surface_color,
            "muted_text_color": self.muted_text_color,
            "font_heading": self.font_heading,
            "font_body": self.font_body,
            "title_scale": self.title_scale,
            "body_scale": self.body_scale,
            "corner_style": self.corner_style,
            "accent_style": self.accent_style,
        }


@dataclass
class FontPreset:
    """Represents a font combination preset."""

    name: str
    display_name: str
    heading_font: str
    body_font: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "heading_font": self.heading_font,
            "body_font": self.body_font,
        }


FONT_PRESETS = [
    FontPreset("modern", "Modern", "Montserrat", "Open Sans"),
    FontPreset("classic", "Classic", "Georgia", "Times New Roman"),
    FontPreset("clean", "Clean", "Helvetica", "Arial"),
    FontPreset("tech", "Tech", "Roboto", "Roboto Mono"),
    FontPreset("elegant", "Elegant", "Playfair Display", "Lato"),
    FontPreset("minimal", "Minimal", "Inter", "Inter"),
    FontPreset("bold", "Bold", "Impact", "Arial"),
    FontPreset("friendly", "Friendly", "Poppins", "Nunito"),
    FontPreset("corporate", "Corporate", "Calibri", "Calibri Light"),
    FontPreset("creative", "Creative", "Raleway", "Source Sans Pro"),
]


def get_font_preset(name: str) -> Optional[FontPreset]:
    """Get a font preset by name."""
    for preset in FONT_PRESETS:
        if preset.name == name:
            return preset
    return FONT_PRESETS[0]
