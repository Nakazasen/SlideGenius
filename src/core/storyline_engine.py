"""Storyline and rewrite engine for sharpening semantic slide specs."""
from __future__ import annotations

from collections import Counter
import json
import re
from typing import Any, Dict, List, Optional

from src.core.presentation_spec import normalize_outline
from src.data.models import Outline, SlideItem
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StorylineEngine:
    """Refine a semantic deck into a sharper business narrative."""

    def __init__(self, cascade, config):
        self.cascade = cascade
        self.config = config

    def rewrite_outline(self, outline: Outline, prompt: str, context: Optional[dict] = None) -> Outline:
        """Apply AI rewrite when possible, then always run local rewrite rules."""
        context = context or {}
        outline = normalize_outline(outline)
        outline.candidate_strategy = context.get("candidate_strategy", outline.candidate_strategy)
        if not context.get("fast_interactive_path") and not context.get("stable_mode"):
            rewritten = self._rewrite_with_model(outline, prompt, context)
            if rewritten:
                outline = rewritten
                outline.candidate_strategy = context.get("candidate_strategy", outline.candidate_strategy)
        outline = self._rewrite_locally(outline, prompt, context)
        outline = self._critique_and_refine(outline)
        if not context.get("fast_interactive_path") and not context.get("stable_mode"):
            outline = self._self_critique_with_model(outline, prompt, context)
        return self._finalize_outline(outline, context)

    def improve_if_needed(self, outline: Outline, prompt: str, context: Optional[dict] = None, max_rounds: int = 1) -> Outline:
        """Run one extra controlled refinement round when deck quality is still weak."""
        context = context or {}
        if context.get("fast_interactive_path") or context.get("stable_mode"):
            return outline
        rounds = 0
        while outline.should_rewrite_again and rounds < max_rounds:
            improved, applied = self._quality_retry_with_model(outline, prompt, context)
            if not applied:
                break
            outline = self._finalize_outline(improved, context)
            outline.quality_retry_count += 1
            rounds += 1
        return outline

    def _finalize_outline(self, outline: Outline, context: dict) -> Outline:
        """Apply final visual refinement, QA, and scoring."""
        outline = self._apply_visual_refinement(outline, context)
        outline = self._build_qa_report(outline)
        return self._score_outline(outline)

    def _rewrite_with_model(self, outline: Outline, prompt: str, context: dict) -> Optional[Outline]:
        """Attempt a structured rewrite pass via the configured model cascade."""
        try:
            progress_callback = context.get("_progress_callback")
            if progress_callback:
                progress_callback("Đang làm sắc nét dàn ý bằng AI...")
            creativity = min(0.55, self.config.get("generation.creativity_level", 70) / 100)
            generation_config: Any = {
                "temperature": creativity,
                "response_mime_type": "application/json",
            }
            rewrite_prompt = self._build_rewrite_prompt(outline, prompt, context)
            response = self._generate_with_optional_progress(
                rewrite_prompt,
                generation_config=generation_config,
                progress_callback=progress_callback,
            )
            candidate = Outline.from_dict(json.loads(response.text))
            logger.info("Storyline AI rewrite succeeded.")
            return normalize_outline(candidate)
        except Exception as exc:
            logger.warning("Storyline AI rewrite skipped: %s", exc)
            return None

    def _build_rewrite_prompt(self, outline: Outline, prompt: str, context: dict) -> str:
        """Build the rewrite prompt for the second-pass model call."""
        audience = context.get("audience", "Business audience")
        tone = context.get("tone", "Professional")
        style = context.get("style", "Balanced")
        return f"""
You are an editorial deck strategist rewriting an existing PowerPoint semantic spec.
Improve storyline quality, slide clarity, and executive readability without changing the core topic.

Rules:
1. Keep the same number of slides.
2. Preserve slide order unless a title/agenda/closing role is obviously wrong.
3. Rewrite titles to be sharper and more outcome-oriented.
4. Rewrite summaries and bullets to be shorter, clearer, and more business-ready.
5. Keep layout_variant valid and appropriate for the slide's job.
6. Prefer one key message per slide.
7. Avoid dense wording, repetition, and vague statements.
8. Output valid JSON only.

Audience: {audience}
Tone: {tone}
Style: {style}
Original user request: {prompt}

Return a full Outline schema 2.0 JSON object.

Current outline:
{outline.to_json()}
""".strip()

    def _self_critique_with_model(self, outline: Outline, prompt: str, context: dict) -> Outline:
        """Run a tightly constrained AI self-critique pass after heuristic refinement."""
        if not self.config.get("generation.enable_self_critique", True):
            return outline
        try:
            progress_callback = context.get("_progress_callback")
            if progress_callback:
                progress_callback("Đang tự rà soát và tinh chỉnh dàn ý...")
            generation_config: Any = {
                "temperature": min(0.25, self.config.get("generation.creativity_level", 70) / 100),
                "response_mime_type": "application/json",
            }
            critique_prompt = self._build_self_critique_prompt(outline, prompt, context)
            response = self._generate_with_optional_progress(
                critique_prompt,
                generation_config=generation_config,
                progress_callback=progress_callback,
            )
            candidate = normalize_outline(Outline.from_dict(json.loads(response.text)))
            if len(candidate.slides) != len(outline.slides):
                raise ValueError("Self-critique changed slide count.")
            merged = self._merge_self_critique(outline, candidate)
            logger.info("Storyline AI self-critique succeeded.")
            return merged
        except Exception as exc:
            logger.warning("Storyline AI self-critique skipped: %s", exc)
            return outline

    def _build_self_critique_prompt(self, outline: Outline, prompt: str, context: dict) -> str:
        """Build a minimal, deck-level critique prompt."""
        audience = context.get("audience", "Business audience")
        tone = context.get("tone", "Professional")
        style = context.get("style", "Balanced")
        return f"""
You are the final editorial quality gate for a PowerPoint semantic spec.
Review the deck and make only minimal fixes to improve narrative quality.

Allowed fixes:
1. Sharpen weak slide titles.
2. Improve one-line summaries or key_message when they are vague.
3. Add stronger transitions between adjacent slides when needed.
4. Strengthen the closing CTA if it is too weak.
5. Reduce repetition across slides.

Hard constraints:
1. Keep the same number of slides.
2. Keep slide order unchanged.
3. Keep layout_variant unchanged unless the current one is clearly invalid.
4. Do not expand content; only tighten or slightly reframe.
5. Output valid JSON only.

Audience: {audience}
Tone: {tone}
Style: {style}
Original user request: {prompt}

Current deck after heuristic critique:
{outline.to_json()}
""".strip()

    def _quality_retry_with_model(self, outline: Outline, prompt: str, context: dict) -> tuple[Outline, bool]:
        """Ask the model for one more tightly-scoped refinement round based on rubric flags."""
        try:
            progress_callback = context.get("_progress_callback")
            if progress_callback:
                progress_callback("Chất lượng còn yếu, đang thử một vòng cải thiện nữa...")
            generation_config: Any = {
                "temperature": min(0.2, self.config.get("generation.creativity_level", 70) / 100),
                "response_mime_type": "application/json",
            }
            retry_prompt = self._build_quality_retry_prompt(outline, prompt, context)
            response = self._generate_with_optional_progress(
                retry_prompt,
                generation_config=generation_config,
                progress_callback=progress_callback,
            )
            candidate = normalize_outline(Outline.from_dict(json.loads(response.text)))
            if len(candidate.slides) != len(outline.slides):
                raise ValueError("Quality retry changed slide count.")
            merged = self._merge_self_critique(outline, candidate)
            for slide in merged.slides:
                slide.critique_notes.append("Applied one extra quality retry pass.")
            logger.info("Storyline quality retry succeeded.")
            return merged, True
        except Exception as exc:
            logger.warning("Storyline quality retry skipped: %s", exc)
            return outline, False

    def _generate_with_optional_progress(
        self,
        prompt: str,
        generation_config: Any,
        progress_callback=None,
    ):
        """Call the cascade while remaining compatible with older test doubles."""
        if progress_callback is None:
            return self.cascade.generate_content(prompt, generation_config=generation_config)
        try:
            return self.cascade.generate_content(
                prompt,
                generation_config=generation_config,
                progress_callback=progress_callback,
            )
        except TypeError as exc:
            if "progress_callback" not in str(exc):
                raise
            return self.cascade.generate_content(prompt, generation_config=generation_config)

    def _build_quality_retry_prompt(self, outline: Outline, prompt: str, context: dict) -> str:
        """Build a rubric-aware retry prompt when the deck still scores weakly."""
        audience = context.get("audience", "Business audience")
        tone = context.get("tone", "Professional")
        style = context.get("style", "Balanced")
        return f"""
You are performing one final corrective rewrite on a PowerPoint semantic spec.
The deck has already been rewritten and critiqued, but it still scores weakly on specific rubric dimensions.

Current rubric:
{json.dumps(outline.quality_scores, ensure_ascii=False)}

Quality flags:
{json.dumps(outline.quality_flags, ensure_ascii=False)}

QA summary:
{outline.qa_summary}

QA findings:
{json.dumps(outline.qa_findings, ensure_ascii=False)}

Your job:
1. Fix only the weak dimensions shown above.
2. Keep the same number of slides and the same order.
3. Preserve layout_variant unless obviously invalid.
4. Make minimal edits with maximum editorial impact.
5. Strengthen transitions, remove repeated ideas, sharpen insight statements, and improve the CTA when needed.
6. Output valid JSON only.

Audience: {audience}
Tone: {tone}
Style: {style}
Original user request: {prompt}

Current deck:
{outline.to_json()}
""".strip()

    def _merge_self_critique(self, baseline: Outline, candidate: Outline) -> Outline:
        """Merge the self-critique candidate conservatively into the baseline outline."""
        for base_slide, crit_slide in zip(baseline.slides, candidate.slides):
            title = self._clean_text(crit_slide.title)
            summary = self._clean_text(crit_slide.summary)
            key_message = self._clean_text(crit_slide.key_message)
            subtitle = self._clean_text(crit_slide.subtitle)

            if title and title != self._clean_text(base_slide.title):
                base_slide.title = self._compress_line(title, max_len=80)
                base_slide.critique_notes.append("AI self-critique sharpened the slide title.")
            if summary and summary != self._clean_text(base_slide.summary):
                base_slide.summary = self._compress_line(summary)
                base_slide.critique_notes.append("AI self-critique improved the slide summary.")
            if key_message and key_message != self._clean_text(base_slide.key_message):
                base_slide.key_message = self._compress_line(key_message)
                base_slide.critique_notes.append("AI self-critique strengthened the key message.")
            if subtitle and subtitle != self._clean_text(base_slide.subtitle):
                base_slide.subtitle = self._compress_line(subtitle)
            if crit_slide.bullets and crit_slide.bullets != base_slide.bullets:
                base_slide.bullets = [self._compress_line(item) for item in crit_slide.bullets[:4]]
                base_slide.content = base_slide.bullets.copy()
                base_slide.critique_notes.append("AI self-critique tightened bullet wording.")
            if crit_slide.sections and crit_slide.sections != base_slide.sections:
                base_slide.sections = [self._rewrite_section(section) for section in crit_slide.sections]
                base_slide.critique_notes.append("AI self-critique reduced repetition in section content.")
            base_slide.self_critique_applied = True
        return baseline

    def _score_outline(self, outline: Outline) -> Outline:
        """Score the deck against a small narrative rubric and store quality signals."""
        clarity = self._score_clarity(outline)
        flow = self._score_flow(outline)
        distinctness = self._score_distinctness(outline)
        cta_strength = self._score_cta_strength(outline)
        overall = round((clarity + flow + distinctness + cta_strength) / 4)

        flags: List[str] = []
        if clarity < 70:
            flags.append("Clarity is weak: some slides are still too vague or dense.")
        if flow < 70:
            flags.append("Flow is weak: transitions or roadmap coherence need another pass.")
        if distinctness < 70:
            flags.append("Distinctness is weak: too many slides still feel semantically similar.")
        if cta_strength < 70:
            flags.append("CTA strength is weak: the deck does not end with a strong action signal.")

        outline.quality_scores = {
            "clarity": clarity,
            "flow": flow,
            "distinctness": distinctness,
            "cta_strength": cta_strength,
            "overall": overall,
        }
        outline.quality_flags = flags
        outline.should_rewrite_again = bool(flags) or overall < 72 or any(
            score < 65 for score in [clarity, flow, distinctness, cta_strength]
        )
        outline.quality_summary = self._build_quality_summary(outline)
        return outline

    def _score_clarity(self, outline: Outline) -> int:
        """Estimate clarity based on slide density and specificity."""
        score = 88
        for slide in outline.slides:
            if len(slide.title) > 60:
                score -= 4
            if len(slide.summary) > 130:
                score -= 5
            if len(slide.normalized_bullets) > 4:
                score -= 4
            if not slide.summary and not slide.key_message and slide.storyline_role != "opener":
                score -= 6
            if slide.render_warnings:
                score -= 2 * len(slide.render_warnings[:2])
            generic_count = sum(1 for bullet in slide.normalized_bullets if self._is_generic_line(bullet))
            score -= generic_count * 4
        return max(40, min(98, score))

    def _score_flow(self, outline: Outline) -> int:
        """Estimate narrative flow based on role sequence and bridge quality."""
        score = 86
        roles = [slide.storyline_role for slide in outline.slides]
        if roles and roles[0] != "opener":
            score -= 12
        if roles and roles[-1] != "call_to_action":
            score -= 12
        if "roadmap" not in roles and len(outline.slides) >= 5:
            score -= 8
        for slide in outline.slides[1:-1]:
            if slide.storyline_role in {"insight", "mechanism", "evidence"} and not (slide.summary or slide.key_message):
                score -= 5
        if any("transition" in note.lower() for slide in outline.slides for note in slide.critique_notes):
            score += 2
        return max(40, min(98, score))

    def _score_distinctness(self, outline: Outline) -> int:
        """Estimate how distinct the slides feel from one another."""
        score = 88
        seen = set()
        duplicate_count = 0
        for slide in outline.slides:
            signature = self._slide_signature(slide)
            if signature in seen and signature:
                duplicate_count += 1
            seen.add(signature)
            if any("duplicate" in note.lower() for note in slide.critique_notes):
                duplicate_count += 1
        score -= duplicate_count * 14
        unique_roles = len({slide.storyline_role for slide in outline.slides if slide.storyline_role})
        if unique_roles < 3 and len(outline.slides) >= 5:
            score -= 8
        generic_titles = sum(1 for slide in outline.slides if self._is_generic_line(slide.title))
        score -= generic_titles * 5
        return max(35, min(98, score))

    def _score_cta_strength(self, outline: Outline) -> int:
        """Estimate the strength of the closing action signal."""
        if not outline.slides:
            return 40
        slide = outline.slides[-1]
        score = 78
        if slide.storyline_role == "call_to_action":
            score += 8
        if slide.key_message:
            score += 4
        bullets = slide.normalized_bullets
        if bullets:
            tokens = self._tokenize(bullets[0])
            if len(tokens) >= 5:
                score += 6
            else:
                score -= 10
            action_verbs = {"start", "choose", "commit", "ask", "share", "report", "improve", "bắt", "chọn", "cam", "hỏi", "chia", "báo", "cải"}
            if not any(token in action_verbs for token in tokens):
                score -= 8
        else:
            score -= 18
        if any("closing cta" in note.lower() for note in slide.critique_notes):
            score += 4
        return max(35, min(98, score))

    def _build_quality_summary(self, outline: Outline) -> str:
        """Create a one-line summary of deck quality."""
        scores = outline.quality_scores
        if not scores:
            return ""
        overall = scores.get("overall", 0)
        if overall >= 85:
            level = "strong"
        elif overall >= 72:
            level = "usable"
        else:
            level = "needs another rewrite"
        return (
            f"Deck quality is {level}: clarity {scores.get('clarity', 0)}, "
            f"flow {scores.get('flow', 0)}, distinctness {scores.get('distinctness', 0)}, "
            f"CTA {scores.get('cta_strength', 0)}."
        )

    def _is_generic_line(self, text: str) -> bool:
        """Detect very generic wording that usually signals weak deck quality."""
        cleaned = self._clean_text(text).lower()
        generic_lines = {
            "thing",
            "topic",
            "summary",
            "plan",
            "context",
            "discussion",
            "overview",
            "do it",
        }
        return cleaned in generic_lines or len(self._tokenize(cleaned)) <= 1

    def _rewrite_locally(self, outline: Outline, prompt: str, context: dict) -> Outline:
        """Deterministic rewrite rules that sharpen the deck even without a second model call."""
        theme = self._derive_theme(prompt, outline)
        strategy = context.get("candidate_strategy", "").strip().lower()
        for index, slide in enumerate(outline.slides):
            self._assign_storyline_role(slide, index, len(outline.slides))
            self._rewrite_slide(slide, theme, strategy)
        return outline

    def _derive_theme(self, prompt: str, outline: Outline) -> str:
        """Get a short thematic phrase for the deck."""
        title = outline.title.strip()
        if title:
            return self._clean_text(title)
        prompt = self._clean_text(prompt)
        return prompt[:60] if prompt else "Presentation"

    def _assign_storyline_role(self, slide: SlideItem, index: int, total: int) -> None:
        """Assign narrative roles by layout and position."""
        if index == 0 or slide.layout_variant == "title_hero":
            slide.storyline_role = "opener"
            slide.storyline_intent = "Frame the session and establish why it matters."
        elif slide.layout_variant == "agenda":
            slide.storyline_role = "roadmap"
            slide.storyline_intent = "Set expectations and make the journey easy to follow."
        elif slide.layout_variant == "section_break":
            slide.storyline_role = "pivot"
            slide.storyline_intent = "Create a clear transition into the next section."
        elif slide.layout_variant in {"stats_highlight", "kpi_grid", "chart_focus", "table_summary"}:
            slide.storyline_role = "evidence"
            slide.storyline_intent = "Anchor the story with concrete proof points."
        elif slide.layout_variant in {"comparison_before_after", "decision_matrix", "process_flow"}:
            slide.storyline_role = "mechanism"
            slide.storyline_intent = "Explain how the change works or why the contrast matters."
        elif index == total - 1 or slide.layout_variant == "closing_cta":
            slide.storyline_role = "call_to_action"
            slide.storyline_intent = "Convert insight into a practical next step."
        else:
            slide.storyline_role = "insight"
            slide.storyline_intent = "Develop one core idea cleanly."

    def _rewrite_slide(self, slide: SlideItem, theme: str, strategy: str = "") -> None:
        """Rewrite titles and supporting text in place."""
        slide.title = self._rewrite_title(slide, theme)
        slide.summary = self._rewrite_summary(slide)
        slide.subtitle = self._rewrite_subtitle(slide)
        slide.key_message = self._rewrite_key_message(slide)
        slide.bullets = [self._compress_line(item) for item in slide.normalized_bullets]
        slide.content = slide.bullets.copy()
        slide.sections = [self._rewrite_section(section) for section in slide.sections]
        slide.stats = [self._rewrite_stat(stat) for stat in slide.stats]
        slide.table_spec = self._rewrite_table_spec(slide.table_spec)
        slide.chart_spec = self._rewrite_chart_spec(slide.chart_spec)
        slide.notes_short = slide.notes_short or slide.key_message or slide.summary
        slide.rewritten = True
        slide.critique_notes = []
        slide.qa_flags = []
        self._apply_strategy_voice(slide, strategy)

    def _critique_and_refine(self, outline: Outline) -> Outline:
        """Run a deck-level critique pass and refine weak areas."""
        duplicate_indices = self._find_duplicate_slide_indices(outline.slides)
        for idx in duplicate_indices:
            slide = outline.slides[idx]
            slide.critique_notes.append("Potential duplicate idea detected across adjacent slides.")
            self._differentiate_slide(slide, idx)

        self._repair_transitions(outline.slides)
        self._strengthen_closing_cta(outline.slides)
        self._repair_roadmap_alignment(outline.slides)
        return outline

    def _find_duplicate_slide_indices(self, slides: List[SlideItem]) -> List[int]:
        """Detect adjacent slides carrying nearly the same message."""
        duplicates: List[int] = []
        seen_signatures: Dict[str, int] = {}
        for index, slide in enumerate(slides):
            signature = self._slide_signature(slide)
            if not signature:
                continue
            previous_index = seen_signatures.get(signature)
            if previous_index is not None and index - previous_index <= 2:
                duplicates.append(index)
            else:
                seen_signatures[signature] = index
        return duplicates

    def _slide_signature(self, slide: SlideItem) -> str:
        """Create a short semantic signature for duplicate detection."""
        parts = [slide.title, slide.summary, slide.key_message]
        parts.extend(slide.normalized_bullets[:2])
        tokens = []
        for part in parts:
            tokens.extend(self._tokenize(part))
        important = [token for token, _ in Counter(tokens).most_common(6)]
        return " ".join(important)

    def _differentiate_slide(self, slide: SlideItem, index: int) -> None:
        """Sharpen a slide so it carries a distinct role in the story."""
        role_prefix = {
            "evidence": "Bằng chứng:",
            "mechanism": "Cơ chế:",
            "insight": "Điểm cần thấy:",
            "call_to_action": "Hành động:",
            "roadmap": "Lộ trình:",
        }.get(slide.storyline_role, "Góc nhìn:")
        if not slide.title.startswith(role_prefix):
            slide.title = f"{role_prefix} {slide.title}"
        if slide.summary:
            slide.summary = self._compress_line(f"Slide này nhấn mạnh một góc khác: {slide.summary}")
        elif slide.key_message:
            slide.summary = self._compress_line(f"Slide này bổ sung một góc khác cho câu chuyện: {slide.key_message}")

    def _repair_transitions(self, slides: List[SlideItem]) -> None:
        """Ensure narrative bridges exist between major slides."""
        for index in range(1, len(slides)):
            prev_slide = slides[index - 1]
            slide = slides[index]
            if slide.storyline_role in {"mechanism", "evidence", "insight"} and not slide.summary:
                slide.summary = self._compress_line(
                    f"Sau phần {prev_slide.storyline_role.replace('_', ' ')}, slide này đào sâu vào ý chính tiếp theo."
                )
                slide.critique_notes.append("Added a bridge summary to improve narrative flow.")
            elif slide.storyline_role == "mechanism" and "sau" not in slide.summary.lower():
                slide.summary = self._compress_line(f"Sau phần trước, đây là cách khác biệt hành vi thực sự xuất hiện. {slide.summary}")
                slide.critique_notes.append("Strengthened transition into mechanism slide.")

    def _strengthen_closing_cta(self, slides: List[SlideItem]) -> None:
        """Upgrade a weak or missing CTA on the final slide."""
        if not slides:
            return
        closing = slides[-1]
        if closing.storyline_role != "call_to_action":
            return

        bullets = closing.normalized_bullets
        cta_text = bullets[0] if bullets else ""
        weak_cta = not cta_text or len(self._tokenize(cta_text)) < 4
        if weak_cta:
            closing.bullets = ["Chọn một hành động cụ thể và bắt đầu ngay từ ngày làm việc tiếp theo."]
            closing.content = closing.bullets.copy()
            closing.critique_notes.append("Closing CTA was too weak; replaced with a concrete next-step prompt.")
        if not closing.key_message or len(self._tokenize(closing.key_message)) < 5:
            closing.key_message = "Chốt workshop bằng một cam kết rõ, nhỏ và làm được ngay để biến nhận thức thành hành vi."
            closing.critique_notes.append("Strengthened closing key message.")

    def _repair_roadmap_alignment(self, slides: List[SlideItem]) -> None:
        """Make roadmap slides accurately preview the rest of the deck."""
        roadmap_slides = [slide for slide in slides if slide.storyline_role == "roadmap"]
        if not roadmap_slides:
            return
        future_titles = [
            self._compress_line(slide.title, max_len=42)
            for slide in slides
            if slide.storyline_role in {"mechanism", "evidence", "insight", "call_to_action"}
        ]
        for slide in roadmap_slides:
            if len(slide.bullets) < 3 or self._too_generic_roadmap(slide.bullets):
                slide.bullets = future_titles[:4]
                slide.content = slide.bullets.copy()
                slide.critique_notes.append("Roadmap bullets were too generic; aligned them to the actual deck flow.")
            if not slide.key_message:
                slide.key_message = "Người tham gia nên thấy trước logic của buổi làm việc để theo dõi dễ hơn."

    def _too_generic_roadmap(self, bullets: List[str]) -> bool:
        """Detect roadmap bullets that are too abstract to guide the audience."""
        generic_tokens = {"context", "scope", "plan", "overview", "discussion", "summary"}
        lowered = [self._clean_text(item).lower() for item in bullets]
        return sum(1 for item in lowered if item in generic_tokens) >= max(1, len(lowered) // 2)

    def _rewrite_title(self, slide: SlideItem, theme: str) -> str:
        title = self._clean_text(slide.title)
        if slide.storyline_role == "opener":
            return title
        if slide.storyline_role == "roadmap" and "lộ trình" not in title.lower():
            return title if len(title) <= 42 else self._compress_line(title)
        if slide.storyline_role == "call_to_action":
            return title if "hành động" in title.lower() else f"{title}: Hành động tiếp theo"
        if slide.storyline_role == "evidence":
            return title if len(title) <= 38 else self._compress_line(title)
        if slide.storyline_role == "mechanism" and len(title) < 18:
            return f"{title} hoạt động như thế nào"
        if len(title) > 52:
            return self._compress_line(title)
        return title

    def _rewrite_summary(self, slide: SlideItem) -> str:
        base = slide.summary or slide.subtitle or slide.key_message
        if not base:
            if slide.storyline_role == "roadmap":
                return "Tóm tắt hành trình chính để người tham gia biết mình sẽ đi qua điều gì."
            if slide.storyline_role == "call_to_action":
                return "Chốt lại bài học chính và chuyển thành cam kết cụ thể."
            if slide.storyline_role == "mechanism":
                return "Giải thích trải nghiệm hoặc cơ chế tạo ra khác biệt trong hành vi."
            if slide.normalized_bullets:
                base = slide.normalized_bullets[0]
        return self._compress_line(base)

    def _rewrite_subtitle(self, slide: SlideItem) -> str:
        subtitle = slide.subtitle or ""
        if subtitle:
            return self._compress_line(subtitle)
        if slide.storyline_role == "opener":
            return self._compress_line(slide.summary)
        return ""

    def _rewrite_key_message(self, slide: SlideItem) -> str:
        if slide.key_message:
            return self._compress_line(slide.key_message)
        if slide.storyline_role == "roadmap":
            return "Người tham gia cần thấy rõ logic của workshop ngay từ đầu."
        if slide.storyline_role == "evidence" and slide.stats:
            return "Giữ phần dữ liệu thật gọn để nhường chỗ cho insight."
        if slide.storyline_role == "mechanism":
            return "Khác biệt về hành vi xuất hiện khi mức độ an toàn tâm lý thay đổi."
        if slide.storyline_role == "call_to_action":
            return "Nếu không chuyển thành hành động cụ thể, workshop sẽ dừng ở mức nhận thức."
        if slide.normalized_bullets:
            return self._compress_line(slide.normalized_bullets[0])
        return ""

    def _rewrite_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        items = [self._compress_line(item) for item in section.get("items", []) if self._clean_text(item)]
        return {
            **section,
            "title": self._compress_line(section.get("title", "")),
            "items": items[:3] if items else [],
        }

    def _rewrite_stat(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "label": self._compress_line(stat.get("label", "")),
            "value": self._clean_text(stat.get("value", "")),
            "insight": self._compress_line(stat.get("insight", "")),
        }

    def _rewrite_table_spec(self, table_spec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Rewrite table headers and rows for readability."""
        if not table_spec:
            return table_spec
        headers = [self._compress_line(cell, max_len=26) for cell in table_spec.get("headers", [])[:4]]
        rows = []
        for row in table_spec.get("rows", [])[:5]:
            if isinstance(row, list):
                rows.append([self._compress_line(cell, max_len=42) for cell in row[:4]])
        return {"headers": headers, "rows": rows}

    def _rewrite_chart_spec(self, chart_spec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Normalize chart spec labels for future renderers."""
        if not chart_spec:
            return chart_spec
        series = []
        for point in chart_spec.get("series", [])[:6]:
            if isinstance(point, dict):
                series.append(
                    {
                        "label": self._compress_line(point.get("label", ""), max_len=22),
                        "value": point.get("value", 0),
                    }
                )
        series_groups = []
        for group in chart_spec.get("series_groups", [])[:2]:
            if isinstance(group, dict):
                points = []
                for point in group.get("points", [])[:6]:
                    if isinstance(point, dict):
                        points.append(
                            {
                                "label": self._compress_line(point.get("label", ""), max_len=22),
                                "value": point.get("value", 0),
                            }
                        )
                if points:
                    series_groups.append(
                        {
                            "name": self._compress_line(group.get("name", "Series"), max_len=20),
                            "points": points,
                        }
                    )
        return {
            "type": self._clean_text(chart_spec.get("type", "bar")),
            "series": series,
            "series_groups": series_groups,
            "insight": self._compress_line(chart_spec.get("insight", ""), max_len=96),
        }

    def _apply_strategy_voice(self, slide: SlideItem, strategy: str) -> None:
        """Nudge wording based on the active candidate strategy."""
        if not strategy:
            return
        if strategy == "executive":
            slide.visual_treatment = "executive_clean"
            if slide.summary:
                slide.summary = self._compress_line(slide.summary, max_len=88)
        elif strategy == "workshop":
            slide.visual_treatment = "facilitated_flow"
            if slide.storyline_role == "roadmap" and slide.key_message:
                slide.key_message = self._compress_line(f"Make the session easy to follow and safe to join: {slide.key_message}")
        elif strategy == "persuasive":
            slide.visual_treatment = "contrast_led"
            if slide.storyline_role in {"evidence", "mechanism"} and slide.key_message:
                slide.key_message = self._compress_line(f"The decisive point is: {slide.key_message}")
        elif strategy == "data_storytelling":
            slide.visual_treatment = "insight_first"
            if slide.storyline_role == "evidence" and slide.summary:
                slide.summary = self._compress_line(f"Key takeaway: {slide.summary}", max_len=96)

    def _apply_visual_refinement(self, outline: Outline, context: dict) -> Outline:
        """Refine layout density and visual treatment before final scoring."""
        strategy = (context.get("candidate_strategy") or outline.candidate_strategy or "").strip().lower()
        for slide in outline.slides:
            slide.qa_flags = []
            density_score = self._estimate_density_score(slide)
            if density_score >= 8:
                slide.density_level = "dense"
            elif density_score >= 5:
                slide.density_level = "balanced"
            else:
                slide.density_level = "light"

            if slide.layout_variant == "content_image_right" and not (slide.image_prompt or slide.image_path):
                slide.layout_variant = "content_2col"
                slide.critique_notes.append("Visual refinement switched image layout to text layout because no image input was available.")

            if slide.layout_variant == "stats_highlight" and len(slide.stats) >= 3:
                slide.layout_variant = "kpi_grid"
                slide.critique_notes.append("Visual refinement promoted the slide to KPI grid for denser metric storytelling.")
            elif slide.layout_variant == "kpi_grid" and len(slide.stats) <= 2:
                slide.layout_variant = "stats_highlight"
                slide.critique_notes.append("Visual refinement simplified the KPI grid to a stats highlight layout.")
            elif slide.layout_variant == "chart_focus" and not slide.chart_spec:
                if len(slide.stats) >= 3:
                    slide.layout_variant = "kpi_grid"
                else:
                    slide.layout_variant = "content_2col"
                slide.critique_notes.append("Visual refinement downgraded the chart layout because no chart data was available.")

            if slide.layout_variant == "content_2col" and not slide.normalized_bullets and (slide.key_message or slide.summary):
                if slide.storyline_role in {"pivot", "insight"}:
                    slide.layout_variant = "section_break"
                    slide.critique_notes.append("Visual refinement converted a low-density content slide into a section-style emphasis slide.")

            if slide.layout_variant == "table_summary" and slide.table_spec:
                column_count = len(slide.table_spec.get("headers", []))
                slide.visual_treatment = "compact_table" if column_count >= 4 else (slide.visual_treatment or "clean_table")
            elif slide.layout_variant == "decision_matrix":
                slide.visual_treatment = slide.visual_treatment or "matrix_quadrants"
            elif slide.layout_variant == "kpi_grid":
                slide.visual_treatment = slide.visual_treatment or "metric_cards"
            elif slide.layout_variant == "chart_focus":
                slide.visual_treatment = slide.visual_treatment or "native_chart"
            elif not slide.visual_treatment:
                slide.visual_treatment = "editorial_standard"

            if strategy == "data_storytelling" and slide.layout_variant in {"kpi_grid", "chart_focus", "table_summary", "decision_matrix"}:
                slide.visual_treatment = "insight_first_data"

            slide.emphasis_terms = self._derive_emphasis_terms(slide)
        return outline

    def _build_qa_report(self, outline: Outline) -> Outline:
        """Build lightweight QA findings so weak slides are visible in the UI and ranking."""
        findings: List[Dict[str, Any]] = []
        for index, slide in enumerate(outline.slides):
            slide.qa_flags = []
            if len(slide.title) > 68:
                slide.qa_flags.append("Title is long and may weaken hierarchy.")
            if len(slide.summary) > 140:
                slide.qa_flags.append("Summary is too dense for a clean business slide.")
            if slide.layout_variant == "content_image_right" and not (slide.image_prompt or slide.image_path):
                slide.qa_flags.append("Image layout is missing an image source.")
            if slide.layout_variant in {"comparison_before_after", "decision_matrix"} and len(slide.sections) < 2:
                slide.qa_flags.append("Comparison logic is underspecified.")
            if slide.layout_variant == "table_summary" and slide.table_spec and len(slide.table_spec.get("rows", [])) >= 5:
                slide.qa_flags.append("Table is near the row limit and may feel busy.")
            if slide.layout_variant == "kpi_grid" and len(slide.stats) < 3:
                slide.qa_flags.append("KPI grid has too few metrics to justify the layout.")
            if slide.layout_variant == "chart_focus":
                if not slide.chart_spec or (not slide.chart_spec.get("series") and not slide.chart_spec.get("series_groups")):
                    slide.qa_flags.append("Chart slide is missing usable series data.")
                elif len(slide.chart_spec.get("series", [])) >= 6:
                    slide.qa_flags.append("Chart is near the point limit and may feel crowded.")
            if slide.render_warnings:
                slide.qa_flags.append("Renderer fallback or warning detected.")
            if slide.density_level == "dense":
                slide.qa_flags.append("Slide density is high and may need more whitespace.")
            for flag in slide.qa_flags:
                findings.append(
                    {
                        "slide_index": index,
                        "title": slide.title,
                        "severity": "warning",
                        "message": flag,
                    }
                )

        outline.qa_findings = findings
        if not findings:
            outline.qa_summary = "QA check passed: no major slide-density or layout-fit risks detected."
        else:
            dense_count = sum(1 for slide in outline.slides if slide.density_level == "dense")
            outline.qa_summary = (
                f"QA found {len(findings)} issue(s) across {len({item['slide_index'] for item in findings})} slide(s); "
                f"{dense_count} slide(s) are dense."
            )
        return outline

    def _estimate_density_score(self, slide: SlideItem) -> int:
        """Estimate visual density before export."""
        score = 0
        score += min(3, len(slide.normalized_bullets))
        score += min(2, len(slide.sections))
        score += min(2, len(slide.stats))
        score += 2 if slide.chart_spec and slide.layout_variant == "chart_focus" else 0
        score += 1 if len(slide.title) > 56 else 0
        score += 1 if len(slide.summary) > 110 else 0
        score += 1 if slide.table_spec and len(slide.table_spec.get("rows", [])) >= 4 else 0
        return score

    def _derive_emphasis_terms(self, slide: SlideItem) -> List[str]:
        """Extract a few short emphasis terms for future visual hierarchy decisions."""
        pool: List[str] = []
        pool.extend(self._tokenize(slide.title))
        pool.extend(self._tokenize(slide.key_message))
        for stat in slide.stats[:2]:
            pool.extend(self._tokenize(stat.get("label", "")))
        if slide.table_spec:
            pool.extend(self._tokenize(" ".join(slide.table_spec.get("headers", [])[:2])))
        ordered: List[str] = []
        seen = set()
        for token in pool:
            if token not in seen and len(token) >= 4:
                seen.add(token)
                ordered.append(token)
        return ordered[:3]

    def _compress_line(self, text: str, max_len: int = 110) -> str:
        """Condense a line while preserving Vietnamese and English punctuation."""
        text = self._clean_text(text)
        if len(text) <= max_len:
            return text
        parts = re.split(r"[.;:!?]\s+|,\s+", text)
        candidate = parts[0].strip() if parts else text
        if 0 < len(candidate) <= max_len:
            return candidate
        truncated = text[:max_len].rsplit(" ", 1)[0].strip()
        return truncated or text[:max_len].strip()

    def _clean_text(self, value: Any) -> str:
        text = str(value or "").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _tokenize(self, text: Any) -> List[str]:
        """Tokenize text for rough semantic comparison."""
        cleaned = self._clean_text(text).lower()
        return [token for token in re.findall(r"\w+", cleaned) if len(token) > 2]
