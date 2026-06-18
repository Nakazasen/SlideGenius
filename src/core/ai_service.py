"""AI Service - Gemini API integration for semantic presentation specs."""
import json
from copy import deepcopy
from typing import List, Optional, Tuple

from google.genai import types

from src.core.model_cascade import ModelCascade
from src.core.preview_qa import PreviewQAGate
from src.core.presentation_spec import normalize_outline
from src.core.storyline_engine import StorylineEngine
from src.data.config_manager import ConfigManager
from src.data.models import Outline
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """Service to interact with Gemini for content generation."""

    def __init__(self):
        self.config = ConfigManager()
        self.cascade = ModelCascade()
        self.storyline_engine = StorylineEngine(self.cascade, self.config)
        self.preview_qa = PreviewQAGate(self.config)
        self._configure_api()

    def _configure_api(self) -> None:
        """Configure Gemini API with keys from config."""
        api_keys = self.config.get("api.gemini_keys", [])
        if not api_keys:
            single = self.config.get("api.gemini_key", "")
            if single:
                api_keys = [single]
        self.cascade.configure_api(api_keys)

    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return bool(self.config.get("api.gemini_keys") or self.config.get("api.gemini_key"))

    def reconfigure(self) -> None:
        """Reconfigure API after settings change."""
        self._configure_api()

    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection using the current model cascade."""
        if not self.is_configured():
            return False, "API key chưa được cấu hình"

        try:
            response = self.cascade.generate_content("Say 'OK' if you can hear me.")
            if response.text:
                return True, "Kết nối thành công"
            return False, "Không nhận được phản hồi từ model"
        except Exception as exc:
            return False, f"Lỗi kết nối: {exc}"

    def generate_outline(self, prompt: str, num_slides: int = 8, context: dict = None, progress_callback=None) -> Optional[Outline]:
        """Generate, rewrite, rank, and return the strongest semantic presentation spec."""
        if not self.is_configured():
            raise ValueError("API key chưa được cấu hình. Vui lòng vào Settings để nhập.")

        num_slides = max(1, min(20, num_slides))
        context = context or {}
        stable_mode = bool(context.get("stable_mode", self.config.get("generation.stable_mode", True)))
        context = {**context, "stable_mode": stable_mode}
        if progress_callback:
            progress_callback("Đang tạo dàn ý...")
            if stable_mode:
                progress_callback("Đang chạy chế độ ổn định để ưu tiên bố cục an toàn hơn...")
        if self._use_fast_interactive_path(context):
            context = {**context, "fast_interactive_path": True}
            logger.info("Fast interactive path enabled for UI generation.")
        if progress_callback:
            context["_progress_callback"] = progress_callback
        system_prompt = self._build_system_prompt(num_slides, context)

        try:
            candidate_count = self._resolve_candidate_count(num_slides, context)
            candidates: List[Outline] = []

            for candidate_index in range(candidate_count):
                strategy_name, strategy_hint = self._candidate_strategy_hint(candidate_index, candidate_count, context)
                candidate_context = {**context, "candidate_strategy": strategy_name}
                if progress_callback and candidate_count > 1:
                    progress_callback(f"Đang tạo phương án {candidate_index + 1}/{candidate_count}...")
                raw_outline = self._generate_raw_outline_candidate(
                    system_prompt,
                    prompt,
                    candidate_context,
                    candidate_index,
                    candidate_count,
                    strategy_hint,
                )
                if not raw_outline:
                    continue
                raw_outline.candidate_strategy = strategy_name
                if stable_mode:
                    raw_outline = self._stabilize_outline(raw_outline)
                if progress_callback:
                    progress_callback("Đang chuẩn hóa và chấm chất lượng dàn ý...")
                processed = self.storyline_engine.rewrite_outline(raw_outline, prompt, candidate_context)
                if self.config.get("generation.auto_retry_low_quality", True) and not context.get("fast_interactive_path") and not stable_mode:
                    processed = self.storyline_engine.improve_if_needed(processed, prompt, candidate_context, max_rounds=1)
                candidates.append(processed)

            if not candidates:
                return None

            selected = self._select_best_outline(candidates)
            if progress_callback and len(candidates) > 1:
                progress_callback("Đang chọn phương án tốt nhất...")
            selected = self._apply_preview_qa(selected, prompt, context)
            if progress_callback:
                progress_callback("Đã tạo xong dàn ý.")
            logger.info(
                "Generated outline successfully: %s | candidate %s/%s",
                selected.title,
                selected.selected_candidate_index + 1,
                selected.candidate_count_generated,
            )
            return selected
        except json.JSONDecodeError as exc:
            logger.error("JSON parse error: %s", exc)
            return None
        except Exception as exc:
            logger.error("AI error via cascade: %s", exc)
            return None

    def _resolve_candidate_count(self, num_slides: int, context: dict) -> int:
        """Decide how many raw candidates to generate."""
        if context.get("fast_interactive_path") or context.get("stable_mode"):
            return 1
        if not self.config.get("generation.enable_candidate_ranking", True):
            return 1
        requested = int(self.config.get("generation.candidate_count", 3) or 1)
        requested = max(1, min(4, requested))
        if num_slides <= 3:
            return 1
        return requested

    def _use_fast_interactive_path(self, context: dict) -> bool:
        """Use a lower-latency path for interactive UI generation when capacity is limited."""
        return bool(context.get("interactive_ui")) and len(self.cascade.api_keys) <= 1

    def _stabilize_outline(self, outline: Outline) -> Outline:
        """Downgrade fragile layouts into safer production defaults."""
        for slide in outline.slides:
            if slide.layout_variant == "content_image_right":
                slide.layout_variant = "content_2col"
                slide.render_warnings.append("Stable mode switched image layout to text-first layout.")
            elif slide.layout_variant == "kpi_grid":
                slide.layout_variant = "stats_highlight"
                slide.render_warnings.append("Stable mode simplified KPI grid to stats highlight.")
            elif slide.layout_variant == "chart_focus":
                slide.layout_variant = "stats_highlight" if slide.stats else "content_2col"
                slide.render_warnings.append("Stable mode disabled chart layout to avoid render instability.")
            elif slide.layout_variant == "decision_matrix":
                slide.layout_variant = "comparison_before_after"
                slide.render_warnings.append("Stable mode simplified decision matrix to comparison layout.")
            elif slide.layout_variant == "table_summary":
                slide.layout_variant = "content_2col"
                if slide.table_spec:
                    rows = slide.table_spec.get("rows", [])
                    slide.bullets = [
                        f"{row[0]}: {row[-1]}"
                        for row in rows[:4]
                        if isinstance(row, list) and row
                    ]
                    slide.content = slide.bullets.copy()
                slide.render_warnings.append("Stable mode converted table layout to text summary.")
        return normalize_outline(outline)

    def _generate_raw_outline_candidate(
        self,
        system_prompt: str,
        prompt: str,
        context: dict,
        candidate_index: int,
        candidate_count: int,
        strategy_hint: str,
    ) -> Optional[Outline]:
        """Generate one raw semantic candidate from the model."""
        creativity = self.config.get("generation.creativity_level", 70) / 100
        candidate_temperature = min(0.95, creativity + candidate_index * 0.08)
        generation_config = types.GenerateContentConfig(
            temperature=candidate_temperature,
            response_mime_type="application/json",
        )
        response = self.cascade.generate_content(
            f"{system_prompt}\n\nCandidate strategy: {strategy_hint}\nUser request: {prompt}",
            generation_config=generation_config,
            progress_callback=context.get("_progress_callback"),
        )
        data = json.loads(response.text)
        outline = normalize_outline(Outline.from_dict(data))
        outline.selected_candidate_index = candidate_index
        outline.candidate_strategy = context.get("candidate_strategy", "")
        return outline

    def _candidate_strategy_hint(self, candidate_index: int, candidate_count: int, context: dict) -> tuple[str, str]:
        """Provide slight narrative variation across candidates."""
        if context.get("stable_mode"):
            return ("stable", "Prefer the safest, most conservative text-first deck structure with low layout risk.")
        strategies = [
            ("executive", "Prefer a clean executive storyline with direct titles and low text density."),
            ("workshop", "Prefer a workshop or facilitation storyline with clearer transitions and stronger action framing."),
            ("persuasive", "Prefer a persuasive storyline that sharpens contrast, insight, and decision points."),
            ("data_storytelling", "Prefer an insight-first storyline that promotes metrics, comparisons, and decision-ready evidence."),
        ]
        return strategies[candidate_index % len(strategies)]

    def _select_best_outline(self, candidates: List[Outline]) -> Outline:
        """Rank processed candidates and return the strongest one."""
        scored_rows = []
        for index, outline in enumerate(candidates):
            scores = outline.quality_scores or {}
            overall = int(scores.get("overall", 0))
            clarity = int(scores.get("clarity", 0))
            flow = int(scores.get("flow", 0))
            distinctness = int(scores.get("distinctness", 0))
            cta_strength = int(scores.get("cta_strength", 0))
            qa_penalty = len(outline.qa_findings) * 2
            penalty = len(outline.quality_flags) * 8 + outline.quality_retry_count * 2 + qa_penalty
            rank_score = overall * 10 + clarity + flow + distinctness + cta_strength - penalty
            scored_rows.append(
                {
                    "candidate_index": index,
                    "rank_score": rank_score,
                    "quality_scores": scores,
                    "quality_flags": outline.quality_flags,
                    "qa_findings": len(outline.qa_findings),
                    "candidate_strategy": outline.candidate_strategy,
                }
            )

        best_index = max(range(len(candidates)), key=lambda idx: scored_rows[idx]["rank_score"])
        selected = candidates[best_index]
        selected.candidate_count_generated = len(candidates)
        selected.selected_candidate_index = best_index
        selected.candidate_scores = scored_rows
        selected.selected_candidate_rationale = self._build_candidate_rationale(scored_rows[best_index], selected)
        return selected

    def _build_candidate_rationale(self, row: dict, outline: Outline) -> str:
        """Explain why the winning candidate was chosen."""
        scores = row.get("quality_scores", {})
        reasons = [
            f"overall {scores.get('overall', 0)}",
            f"clarity {scores.get('clarity', 0)}",
            f"flow {scores.get('flow', 0)}",
        ]
        if outline.candidate_strategy:
            reasons.append(f"{outline.candidate_strategy} strategy")
        if not outline.quality_flags:
            reasons.append("no major quality flags")
        else:
            reasons.append(f"{len(outline.quality_flags)} quality flag(s)")
        if not outline.qa_findings:
            reasons.append("clean QA report")
        else:
            reasons.append(f"{len(outline.qa_findings)} QA finding(s)")
        return "Selected candidate because it had the strongest " + ", ".join(reasons) + "."

    def _build_system_prompt(self, num_slides: int, context: dict) -> str:
        """Build a schema-first prompt for business deck generation."""
        audience = context.get("audience", "General business audience")
        tone = context.get("tone", "Professional")
        style = context.get("style", "Balanced")
        language = self.config.get("generation.default_language", "vi")
        stable_mode = bool(context.get("stable_mode"))

        if num_slides <= 3:
            structure_hint = (
                f"Create exactly {num_slides} slides. Do not add separate agenda or closing slides unless the user asks for them."
            )
        else:
            structure_hint = (
                "Use a business-deck flow: title hero, roadmap or context, core insight slides, and a closing CTA."
            )

        allowed_layouts = [
            "title_hero",
            "agenda",
            "section_break",
            "content_2col",
            "stats_highlight",
            "comparison_before_after",
            "process_flow",
            "closing_cta",
        ] if stable_mode else [
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
        ]

        content_budgets = [
            "- title_hero: one title, one subtitle, no bullets",
            "- agenda: 3 to 6 short bullets",
            "- section_break: one key_message, no dense text",
            "- content_2col: up to 4 bullets total",
            "- stats_highlight: 1 to 3 stats, each with label, value, insight",
            "- comparison_before_after: 2 sections, each up to 3 items",
            "- process_flow: 3 to 5 steps",
            "- closing_cta: one key_message and one CTA",
        ]
        if not stable_mode:
            content_budgets[4:4] = [
                "- content_image_right: up to 4 bullets plus optional image_prompt",
                "- kpi_grid: 3 to 4 KPIs with short labels and crisp insights",
                "- chart_focus: one chart_spec with up to 6 points, plus one short insight and up to 2 support bullets",
                "- decision_matrix: 4 quadrants or 4 options with clear trade-offs",
                "- table_summary: headers plus up to 5 short rows",
            ]

        extra_rules = (
            "7. Stable mode is ON: prefer text-first layouts and avoid image, chart, table, or matrix layouts unless the user explicitly asks for them.\n"
            "8. If content is too long, summarize the most important points on-slide and keep full detail in speaker_notes."
            if stable_mode
            else
            "7. Prefer the cleanest visual layout that fits the content.\n"
            "8. Avoid dense wording, but you may use richer visual blocks when the content supports them."
        )

        return f"""
You are an expert presentation strategist creating business-ready PowerPoint decks.
Your task is to produce a semantic presentation spec, not a plain bullet outline.

Rules:
1. Create exactly {num_slides} slides.
2. Prioritize clean business deck structure over dense text.
3. Respect content budgets for each layout.
4. Speaker notes must be short and practical.
5. Only include image_prompt, diagram, chart_spec, or table_spec when they materially help the slide.
6. Output valid JSON only. No markdown.
{extra_rules}

Audience: {audience}
Tone: {tone}
Style: {style}
Language: {language}
Structure guidance: {structure_hint}

Allowed layout_variant values:
{chr(10).join(f"- {item}" for item in allowed_layouts)}

Content budgets:
{chr(10).join(content_budgets)}

Return JSON with this shape:
{{
  "title": "Deck title",
  "language": "{language}",
  "schema_version": "2.0",
  "slides": [
    {{
      "title": "Slide title",
      "slide_type": "content",
      "layout_variant": "content_2col",
      "subtitle": "",
      "summary": "",
      "bullets": [],
      "key_message": "",
      "stats": [],
      "sections": [],
      "visual_intent": "",
      "image_prompt": null,
      "image_slots": [],
      "diagram": null,
      "chart_spec": null,
      "table_spec": null,
      "speaker_notes": "",
      "notes_short": ""
    }}
  ]
}}
""".strip()

    def _apply_preview_qa(self, outline: Outline, prompt: str, context: dict) -> Outline:
        """Run render-based QA on the selected outline and optionally retry once more."""
        if context.get("fast_interactive_path") or context.get("stable_mode"):
            return outline
        if not self.config.get("generation.enable_preview_qa", True):
            return outline

        template_id = self.config.get("template.selected", "executive_blue")
        outline = self.preview_qa.evaluate_outline(outline, template_id=template_id)

        if outline.should_rewrite_again and self.config.get("generation.enable_preview_auto_fix", True):
            outline, applied = self.preview_qa.choose_best_remediation_variant(outline, template_id=template_id)
            if not applied:
                outline, applied = self.preview_qa.auto_remediate_outline(outline)
            if applied:
                outline = self.preview_qa.evaluate_outline(outline, template_id=template_id)

        if outline.should_rewrite_again and self.config.get("generation.auto_retry_low_quality", True):
            retry_context = deepcopy(context)
            retry_context["preview_qa_summary"] = outline.qa_summary
            retry_context["preview_qa_findings"] = outline.qa_findings
            outline = self.storyline_engine.improve_if_needed(outline, prompt, retry_context, max_rounds=1)
            outline = self.preview_qa.evaluate_outline(outline, template_id=template_id)

        return outline
