"""Preview-based visual QA using rendered slide images."""
from __future__ import annotations

from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from PIL import Image

from src.core.pptx_generator import PPTXGenerator, TEMPLATES
from src.data.models import Outline, SlideItem
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PreviewQAGate:
    """Render slides to images and inspect visual density / clipping heuristics."""

    def __init__(self, config):
        self.config = config

    def evaluate_outline(self, outline: Outline, template_id: str = "executive_blue") -> Outline:
        """Render a temporary PPTX and merge preview QA findings back into the outline."""
        if not outline.slides:
            return outline

        try:
            self._reset_preview_state(outline)
            with TemporaryDirectory(prefix="slidegenius_preview_qa_") as tmp_dir:
                temp_root = Path(tmp_dir)
                pptx_path = temp_root / "preview_qa.pptx"
                preview_dir = temp_root / "slides"
                preview_dir.mkdir(parents=True, exist_ok=True)

                clone = Outline.from_dict(outline.to_dict())
                template = TEMPLATES.get(template_id, PPTXGenerator.DEFAULT_TEMPLATE)
                PPTXGenerator(template).generate(clone, pptx_path)
                image_paths = self._render_preview_images(pptx_path, preview_dir)
                if not image_paths:
                    return outline

                findings = self._collect_findings(outline, image_paths)
                outline.preview_qa_applied = True
                self._merge_findings(outline, findings)
                logger.info("Preview QA analyzed %s slide image(s).", len(image_paths))
                return outline
        except Exception as exc:
            logger.warning("Preview QA skipped: %s", exc)
            return outline

    def auto_remediate_outline(self, outline: Outline) -> Tuple[Outline, bool]:
        """Apply a deterministic single-pass fallback based on preview findings."""
        applied = False
        for index, slide in enumerate(outline.slides):
            variant = self._apply_variant_to_slide(slide, "balanced")
            if variant is not slide:
                outline.slides[index] = variant
                applied = True
        return outline, applied

    def choose_best_remediation_variant(self, outline: Outline, template_id: str = "executive_blue") -> Tuple[Outline, bool]:
        """Try multiple remediation variants and select the best one via rerendered preview score."""
        target_indices = [index for index, slide in enumerate(outline.slides) if self._needs_remediation(slide)]
        if not target_indices:
            return outline, False

        best_outline = outline
        applied = False
        for slide_index in target_indices:
            variant_names = self._variant_names_for_slide(best_outline.slides[slide_index])
            if not variant_names:
                continue

            baseline_report = self._render_variant_report(best_outline, template_id, slide_index)
            best_score = self._score_variant_report(best_outline, slide_index, baseline_report)
            selected_outline = best_outline
            selected_name = None

            for variant_name in variant_names:
                candidate = Outline.from_dict(best_outline.to_dict())
                candidate.slides[slide_index] = self._apply_variant_to_slide(candidate.slides[slide_index], variant_name)
                report = self._render_variant_report(candidate, template_id, slide_index)
                score = self._score_variant_report(candidate, slide_index, report)
                if score < best_score - 0.02:
                    best_score = score
                    selected_outline = report
                    selected_name = variant_name

            if selected_name:
                selected_outline.slides[slide_index].critique_notes.append(
                    f"Preview variant selection chose the {selected_name} remediation after rerender."
                )
                best_outline = selected_outline
                applied = True

        return best_outline, applied

    def _render_preview_images(self, pptx_path: Path, output_dir: Path) -> List[Path]:
        """Use PowerPoint COM to export slide previews to PNG files."""
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        app = None
        presentation = None
        try:
            app = win32com.client.DispatchEx("PowerPoint.Application")
            app.Visible = 1
            app.DisplayAlerts = 0
            presentation = app.Presentations.Open(
                str(pptx_path.resolve()),
                ReadOnly=True,
                Untitled=False,
                WithWindow=True,
            )
            presentation.Export(str(output_dir.resolve()), "PNG", 1600, 900)
            paths = sorted(output_dir.glob("Slide*.PNG")) or sorted(output_dir.glob("slide*.png"))
            return paths
        finally:
            if presentation is not None:
                presentation.Close()
            if app is not None:
                app.Quit()
            pythoncom.CoUninitialize()

    def _collect_findings(self, outline: Outline, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """Analyze each preview image and return structured findings."""
        findings: List[Dict[str, Any]] = []
        for index, image_path in enumerate(image_paths):
            if index >= len(outline.slides):
                break
            report = self.analyze_image(image_path)
            slide = outline.slides[index]
            slide.preview_density_score = report["density_score"]
            for flag in report["flags"]:
                severity = "warning"
                message = flag
                if flag.startswith("Possible clipping"):
                    severity = "error"
                elif flag.startswith("High visual density") or flag.startswith("Crowded"):
                    severity = "warning"
                findings.append(
                    {
                        "slide_index": index,
                        "title": slide.title,
                        "severity": severity,
                        "message": message,
                        "source": "preview",
                    }
                )
        return findings

    def _merge_findings(self, outline: Outline, findings: List[Dict[str, Any]]) -> None:
        """Merge preview findings into existing QA fields and quality flags."""
        preview_findings = [item for item in findings if item.get("source") == "preview"]
        if not preview_findings:
            outline.qa_summary = (
                f"{outline.qa_summary} Preview QA passed: rendered slides stayed within density and margin thresholds."
            ).strip()
            return

        for finding in preview_findings:
            slide_index = finding.get("slide_index", -1)
            if 0 <= slide_index < len(outline.slides):
                outline.slides[slide_index].qa_flags.append(finding["message"])

        outline.qa_findings.extend(preview_findings)
        affected = len({item["slide_index"] for item in preview_findings})
        outline.qa_summary = (
            f"{outline.qa_summary} Preview QA found {len(preview_findings)} issue(s) across {affected} rendered slide(s)."
        ).strip()

        severe = any(item["severity"] == "error" for item in preview_findings)
        if severe:
            outline.quality_flags.append("Preview QA detected possible clipping near slide edges after render.")
            outline.should_rewrite_again = True
        elif len(preview_findings) >= 2:
            outline.quality_flags.append("Preview QA detected visually crowded slides after render.")
            outline.should_rewrite_again = True

    def _needs_remediation(self, slide: SlideItem) -> bool:
        """Return True when preview findings indicate the slide should be remediated."""
        flags = " ".join(slide.qa_flags).lower()
        return bool(
            slide.preview_density_score >= 0.24
            or "high visual density" in flags
            or "crowded" in flags
            or "clipping" in flags
            or "overlap" in flags
        )

    def _variant_names_for_slide(self, slide: SlideItem) -> List[str]:
        """Return candidate remediation variants for the given slide."""
        if not self._needs_remediation(slide):
            return []
        if slide.layout_variant == "table_summary":
            return ["balanced", "compact", "decision_summary"]
        if slide.layout_variant == "kpi_grid":
            return ["balanced", "compact", "evidence_chart"]
        if slide.layout_variant == "chart_focus":
            return ["balanced", "compact", "scorecard_focus"]
        if slide.layout_variant in {"content_2col", "content_image_right"}:
            return ["balanced", "compact", "section_emphasis"]
        return ["balanced"]

    def _apply_variant_to_slide(self, slide: SlideItem, variant_name: str) -> SlideItem:
        """Apply a named remediation variant to a slide copy."""
        flags = " ".join(slide.qa_flags).lower()
        dense = slide.preview_density_score >= 0.24 or "high visual density" in flags or "crowded" in flags
        clipping = "clipping" in flags
        if not dense and not clipping:
            return slide

        candidate = SlideItem.from_dict(slide.to_dict())
        if candidate.layout_variant == "table_summary" and candidate.table_spec:
            if variant_name == "decision_summary":
                headers = candidate.table_spec.get("headers", [])
                rows = candidate.table_spec.get("rows", [])[:4]
                candidate.layout_variant = "content_2col"
                candidate.bullets = []
                for row in rows[:4]:
                    if row:
                        lead = self._compress_text(row[0], 18)
                        tail = self._compress_text(row[2] if len(row) > 2 else row[-1], 44)
                        candidate.bullets.append(f"{lead}: {tail}")
                candidate.content = candidate.bullets.copy()
                candidate.summary = self._compress_text(candidate.summary or "Decision-ready summary of the most important actions.", 82)
                candidate.key_message = self._compress_text(candidate.key_message or "Use the condensed summary to align owners quickly.", 72)
                candidate.table_spec = None
            else:
                row_limit = 4 if variant_name == "balanced" else 3
                rows = list(candidate.table_spec.get("rows", []))
                candidate.table_spec["rows"] = rows[:row_limit]
                header_limit = 20 if variant_name == "balanced" else 16
                row_limit_chars = (28, 28, 34, 22) if variant_name == "balanced" else (20, 18, 28, 18)
                candidate.table_spec["headers"] = [
                    self._compress_text(cell, header_limit) for cell in candidate.table_spec.get("headers", [])[:4]
                ]
                normalized_rows = []
                for row in candidate.table_spec.get("rows", []):
                    normalized_rows.append(
                        [
                            self._compress_text(cell, row_limit_chars[idx] if idx < len(row_limit_chars) else 22)
                            for idx, cell in enumerate(row[:4])
                        ]
                    )
                candidate.table_spec["rows"] = normalized_rows
                candidate.key_message = self._compress_text(candidate.key_message, 88 if variant_name == "balanced" else 68)
                candidate.summary = self._compress_text(candidate.summary, 90 if variant_name == "balanced" else 72)
        elif candidate.layout_variant == "kpi_grid":
            if variant_name == "evidence_chart":
                candidate.layout_variant = "chart_focus"
                candidate.chart_spec = {
                    "type": "bar",
                    "series": [
                        {
                            "label": self._compress_text(stat.get("label", f"Metric {index + 1}"), 18),
                            "value": self._extract_numeric(stat.get("value", index + 1)) or float(index + 1),
                        }
                        for index, stat in enumerate(candidate.stats[:4])
                    ],
                    "insight": self._compress_text(candidate.key_message or candidate.summary, 68),
                }
                candidate.bullets = candidate.normalized_bullets[:1]
                candidate.content = candidate.bullets.copy()
                candidate.summary = self._compress_text(candidate.summary or "Use the chart to compare which KPI needs attention first.", 78)
                candidate.key_message = self._compress_text(candidate.key_message, 70)
            elif variant_name == "balanced":
                if len(candidate.stats) > 3:
                    candidate.stats = candidate.stats[:3]
                    candidate.layout_variant = "stats_highlight"
                for stat in candidate.stats:
                    stat["label"] = self._compress_text(stat.get("label", ""), 16)
                    stat["insight"] = self._compress_text(stat.get("insight", ""), 42)
            else:
                candidate.layout_variant = "stats_highlight"
                candidate.stats = candidate.stats[:2]
                for stat in candidate.stats:
                    stat["label"] = self._compress_text(stat.get("label", ""), 14)
                    stat["insight"] = self._compress_text(stat.get("insight", ""), 28)
                candidate.summary = self._compress_text(candidate.summary, 72)
                candidate.key_message = self._compress_text(candidate.key_message, 88 if variant_name == "balanced" else 70)
        elif candidate.layout_variant == "chart_focus":
            if variant_name == "scorecard_focus":
                candidate.layout_variant = "stats_highlight"
                series = candidate.chart_spec.get("series", []) if candidate.chart_spec else []
                candidate.stats = [
                    {
                        "label": self._compress_text(point.get("label", f"Metric {index + 1}"), 16),
                        "value": str(point.get("value", "")),
                        "insight": "",
                    }
                    for index, point in enumerate(series[:3])
                    if isinstance(point, dict)
                ]
                candidate.chart_spec = None
                candidate.bullets = []
                candidate.content = []
                candidate.summary = self._compress_text(candidate.summary or "Switch to scorecards when the comparison matters more than the shape.", 74)
                candidate.key_message = self._compress_text(candidate.key_message, 68)
            else:
                candidate.bullets = candidate.normalized_bullets[: (1 if variant_name == "balanced" else 0)]
                candidate.content = candidate.bullets.copy()
                candidate.summary = self._compress_text(candidate.summary, 88 if variant_name == "balanced" else 68)
                candidate.key_message = self._compress_text(candidate.key_message, 82 if variant_name == "balanced" else 66)
                if candidate.chart_spec:
                    if "series" in candidate.chart_spec and isinstance(candidate.chart_spec.get("series"), list):
                        candidate.chart_spec["series"] = candidate.chart_spec["series"][: (5 if variant_name == "balanced" else 4)]
                    if "series_groups" in candidate.chart_spec and isinstance(candidate.chart_spec.get("series_groups"), list):
                        for group in candidate.chart_spec["series_groups"][:2]:
                            if isinstance(group, dict) and isinstance(group.get("points"), list):
                                group["points"] = group["points"][: (5 if variant_name == "balanced" else 4)]
                    candidate.chart_spec["insight"] = self._compress_text(candidate.chart_spec.get("insight", ""), 72 if variant_name == "balanced" else 56)
        elif candidate.layout_variant in {"content_2col", "content_image_right"}:
            if variant_name == "section_emphasis":
                candidate.layout_variant = "section_break"
                candidate.key_message = self._compress_text(candidate.key_message or candidate.summary or (candidate.normalized_bullets[0] if candidate.normalized_bullets else ""), 72)
                candidate.summary = self._compress_text(candidate.summary or candidate.key_message, 68)
                candidate.bullets = []
                candidate.content = []
            else:
                bullet_limit = 3 if variant_name == "balanced" else 2
                candidate.bullets = candidate.normalized_bullets[:bullet_limit]
                candidate.content = candidate.bullets.copy()
                candidate.summary = self._compress_text(candidate.summary, 88 if variant_name == "balanced" else 66)
                candidate.key_message = self._compress_text(candidate.key_message, 78 if variant_name == "balanced" else 60)

        if clipping:
            candidate.title = self._compress_text(candidate.title, 44 if variant_name == "balanced" else 34)
            candidate.summary = self._compress_text(candidate.summary, 84 if variant_name == "balanced" else 62)
        if candidate.to_dict() != slide.to_dict():
            candidate.remediation_variant = variant_name
            candidate.critique_notes.append(f"Preview auto-fix applied the {variant_name} remediation variant.")
        return candidate

    def _render_variant_report(self, outline: Outline, template_id: str, slide_index: int) -> Outline:
        """Render and score a remediation candidate outline."""
        candidate = Outline.from_dict(outline.to_dict())
        return self.evaluate_outline(candidate, template_id=template_id)

    def _score_variant_report(self, outline: Outline, slide_index: int, report_outline: Outline) -> float:
        """Score one remediation candidate after rerender."""
        slide = report_outline.slides[slide_index]
        preview_flags = [flag for flag in slide.qa_flags if self._is_preview_flag(flag)]
        severe = sum(1 for flag in preview_flags if "clipping" in flag.lower())
        crowded = sum(1 for flag in preview_flags if "density" in flag.lower() or "crowded" in flag.lower() or "overlap" in flag.lower())
        family_bonus = self._family_alignment_bonus(slide)
        layout_penalty = 0.03 if slide.layout_variant in {"section_break"} and slide.storyline_role not in {"pivot", "insight"} else 0.0
        return (
            slide.preview_density_score
            + severe * 0.5
            + crowded * 0.18
            + len([item for item in report_outline.qa_findings if item.get("source") == "preview"]) * 0.02
            + layout_penalty
            - family_bonus
        )

    def _reset_preview_state(self, outline: Outline) -> None:
        """Clear previous preview-derived findings before a new render-based QA pass."""
        outline.qa_findings = [item for item in outline.qa_findings if item.get("source") != "preview"]
        outline.quality_flags = [
            item
            for item in outline.quality_flags
            if not item.startswith("Preview QA detected")
        ]
        outline.qa_summary = re.sub(r"\s*Preview QA[^.]*\.", "", outline.qa_summary).strip()
        for slide in outline.slides:
            slide.qa_flags = [
                flag
                for flag in slide.qa_flags
                if not (
                    flag.startswith("High visual density")
                    or flag.startswith("Crowded")
                    or flag.startswith("Possible overlap")
                    or flag.startswith("Possible clipping")
                )
            ]
            slide.preview_density_score = 0.0

    def _is_preview_flag(self, flag: str) -> bool:
        """Return True when the QA flag came from preview image analysis."""
        return flag.startswith("High visual density") or flag.startswith("Crowded") or flag.startswith("Possible overlap") or flag.startswith("Possible clipping")

    def _compress_text(self, value: Any, max_len: int) -> str:
        """Shorten text conservatively for auto-remediation."""
        text = " ".join(str(value or "").split())
        if len(text) <= max_len:
            return text
        candidate = text[:max_len].rsplit(" ", 1)[0].strip()
        return candidate or text[:max_len].strip()

    def _extract_numeric(self, value: Any) -> float:
        """Extract a numeric value from mixed KPI text."""
        text = str(value or "").strip().replace(",", "")
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return 0.0
        try:
            return float(match.group(0))
        except ValueError:
            return 0.0

    def _family_alignment_bonus(self, slide: SlideItem) -> float:
        """Reward variants whose layout family matches the slide's narrative role."""
        role = slide.storyline_role
        layout = slide.layout_variant
        if role == "evidence" and layout in {"chart_focus", "stats_highlight", "kpi_grid", "table_summary"}:
            return 0.05
        if role == "call_to_action" and layout in {"content_2col", "section_break", "closing_cta"}:
            return 0.03
        if role == "insight" and layout in {"section_break", "content_2col"}:
            return 0.04
        if role == "mechanism" and layout in {"comparison_before_after", "decision_matrix", "process_flow"}:
            return 0.04
        return 0.0

    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze a rendered slide image for density and clipping heuristics."""
        image = Image.open(image_path).convert("RGB")
        arr = np.array(image)
        h, w, _ = arr.shape

        corner_size = max(20, min(h, w) // 18)
        corners = np.concatenate(
            [
                arr[:corner_size, :corner_size].reshape(-1, 3),
                arr[:corner_size, -corner_size:].reshape(-1, 3),
                arr[-corner_size:, :corner_size].reshape(-1, 3),
                arr[-corner_size:, -corner_size:].reshape(-1, 3),
            ],
            axis=0,
        )
        background = np.median(corners, axis=0)
        distance = np.linalg.norm(arr.astype(np.float32) - background.astype(np.float32), axis=2)
        fg_mask = (distance > 28).astype(np.uint8)

        kernel = np.ones((3, 3), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        foreground_ratio = float(fg_mask.mean())
        lower_third_ratio = float(fg_mask[int(h * 0.66) :, :].mean())
        bottom_edge_ratio = float(fg_mask[int(h * 0.92) :, :].mean())
        right_edge_ratio = float(fg_mask[:, int(w * 0.95) :].mean())
        left_edge_ratio = float(fg_mask[:, : max(1, int(w * 0.05))].mean())

        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        edge_density = float(cv2.Canny(gray, 80, 180).mean() / 255.0)

        flags: List[str] = []
        if foreground_ratio > 0.34:
            flags.append("High visual density detected in rendered slide.")
        if lower_third_ratio > 0.38 and foreground_ratio > 0.24:
            flags.append("Crowded lower third detected in rendered slide.")
        if edge_density > 0.11 and foreground_ratio > 0.26:
            flags.append("Possible overlap or crowding detected from rendered edge density.")
        if max(bottom_edge_ratio, right_edge_ratio, left_edge_ratio) > 0.16:
            flags.append("Possible clipping near slide edge detected after render.")

        density_score = round(min(1.0, foreground_ratio * 1.8 + edge_density * 0.9), 3)
        return {
            "density_score": density_score,
            "foreground_ratio": round(foreground_ratio, 3),
            "edge_density": round(edge_density, 3),
            "flags": flags,
        }
