import os
import sys
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw

sys.path.append(os.getcwd())

from src.core.presentation_spec import fit_slide_content, normalize_outline
from src.core.pptx_generator import PPTXGenerator
from src.core.model_cascade import ModelCascade, ModelConfig
from src.core.ai_service import AIService
from src.core.preview_qa import PreviewQAGate
from src.core.storyline_engine import StorylineEngine
from src.data.models import Outline, SlideItem, SlideType


def test_slide_item_from_legacy_schema_infers_layout():
    slide = SlideItem.from_dict(
        {
            "title": "Legacy Content",
            "content": ["Point 1", "Point 2"],
            "slide_type": "content",
        }
    )
    assert slide.layout_variant == "content_2col"
    assert slide.bullets == ["Point 1", "Point 2"]


def test_slide_item_from_v2_schema_preserves_semantic_fields():
    slide = SlideItem.from_dict(
        {
            "title": "Metrics",
            "slide_type": "content",
            "layout_variant": "stats_highlight",
            "summary": "Quarterly KPI snapshot",
            "stats": [
                {"label": "Revenue", "value": "+18%", "insight": "QoQ acceleration"},
                {"label": "CAC", "value": "-9%", "insight": "More efficient acquisition"},
            ],
        }
    )
    assert slide.layout_variant == "stats_highlight"
    assert len(slide.stats) == 2
    assert slide.summary == "Quarterly KPI snapshot"


def test_slide_item_from_table_schema_infers_table_layout():
    slide = SlideItem.from_dict(
        {
            "title": "Decision table",
            "table_spec": {"headers": ["Area", "Decision"], "rows": [["Sales", "Invest"], ["Ops", "Automate"]]},
        }
    )
    assert slide.layout_variant == "table_summary"
    assert slide.table_spec["headers"][0] == "Area"


def test_normalize_outline_upgrades_schema_and_legacy_content():
    outline = Outline(
        title="Upgrade",
        schema_version="1.0",
        slides=[SlideItem(title="Agenda", slide_type=SlideType.CONTENT, content=["One", "Two"])],
    )
    normalize_outline(outline)
    assert outline.schema_version == "2.0"
    assert outline.slides[0].bullets == ["One", "Two"]


def test_fit_slide_content_preserves_excess_bullets_and_flags_manual_review():
    slide = SlideItem(
        title="Long content",
        layout_variant="content_2col",
        bullets=["One", "Two", "Three", "Four", "Five"],
        speaker_notes="Existing note",
    )
    slide, fit = fit_slide_content(slide)
    assert len(slide.bullets) == 5
    assert fit.visible_bullets == ["One", "Two", "Three", "Four"]
    assert fit.trim_applied is True
    assert fit.requires_manual_review is True
    assert "Additional points:" in slide.speaker_notes


def test_fit_slide_content_preserves_process_data_and_marks_overflow():
    slide = SlideItem(
        title="Process",
        layout_variant="process_flow",
        sections=[{"title": "Steps", "items": ["A", "B", "C", "D", "E", "F"]}],
    )
    slide, fit = fit_slide_content(slide)
    assert len(slide.sections[0]["items"]) == 6
    assert fit.visible_sections[0]["items"] == ["A", "B", "C", "D", "E"]
    assert fit.trim_applied is True


def test_fit_slide_content_preserves_table_rows_and_marks_overflow():
    slide = SlideItem(
        title="Table summary",
        layout_variant="table_summary",
        table_spec={
            "headers": ["Area", "Decision"],
            "rows": [["A", "1"], ["B", "2"], ["C", "3"], ["D", "4"], ["E", "5"], ["F", "6"]],
        },
    )
    slide, fit = fit_slide_content(slide)
    assert len(slide.table_spec["rows"]) == 6
    assert len(fit.visible_table_rows) == 5
    assert fit.trim_applied is True


def test_fit_slide_content_preserves_chart_points_and_marks_overflow():
    slide = SlideItem(
        title="Chart focus",
        layout_variant="chart_focus",
        chart_spec={
            "type": "bar",
            "series": [
                {"label": "Jan", "value": 10},
                {"label": "Feb", "value": 12},
                {"label": "Mar", "value": 15},
                {"label": "Apr", "value": 14},
                {"label": "May", "value": 18},
                {"label": "Jun", "value": 20},
                {"label": "Jul", "value": 22},
            ],
        },
    )
    slide, fit = fit_slide_content(slide)
    assert len(slide.chart_spec["series"]) == 7
    assert len(fit.visible_chart_spec["series"]) == 6
    assert fit.trim_applied is True


def test_pptx_generator_supports_multiple_new_layouts(tmp_path: Path):
    outline = Outline(
        title="Gamma Upgrade",
        slides=[
            SlideItem(title="Gamma Upgrade", slide_type=SlideType.TITLE, subtitle="Semantic export"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["Context", "Scope", "Plan"]),
            SlideItem(
                title="Metrics",
                layout_variant="stats_highlight",
                stats=[
                    {"label": "Revenue", "value": "+18%", "insight": "Healthy growth"},
                    {"label": "Margin", "value": "+3pt", "insight": "Operating leverage"},
                ],
            ),
            SlideItem(
                title="Before vs After",
                layout_variant="comparison_before_after",
                sections=[
                    {"title": "Before", "items": ["Slow", "Manual", "Fragmented"]},
                    {"title": "After", "items": ["Fast", "Automated", "Aligned"]},
                ],
            ),
            SlideItem(
                title="Process",
                layout_variant="process_flow",
                sections=[{"title": "Steps", "items": ["Intake", "Assess", "Prioritize", "Execute"]}],
            ),
            SlideItem(
                title="KPI grid",
                layout_variant="kpi_grid",
                stats=[
                    {"label": "Pipeline", "value": "+14%", "insight": "Coverage improved"},
                    {"label": "Win rate", "value": "+3pt", "insight": "Higher close quality"},
                    {"label": "Cycle", "value": "-9%", "insight": "Faster conversion"},
                    {"label": "NPS", "value": "62", "insight": "Better customer sentiment"},
                ],
            ),
            SlideItem(
                title="Trend chart",
                layout_variant="chart_focus",
                chart_spec={
                    "type": "line",
                    "series": [
                        {"label": "Q1", "value": 20},
                        {"label": "Q2", "value": 28},
                        {"label": "Q3", "value": 31},
                        {"label": "Q4", "value": 37},
                    ],
                    "insight": "Momentum improved each quarter.",
                },
                bullets=["Demand accelerated after pricing changes."],
            ),
            SlideItem(
                title="Decision matrix",
                layout_variant="decision_matrix",
                sections=[
                    {"title": "Quick Wins", "items": ["Standardize templates", "Automate reporting"]},
                    {"title": "Strategic Bets", "items": ["Rebuild onboarding", "New pricing model"]},
                    {"title": "Low Priority", "items": ["Minor copy refresh"]},
                    {"title": "Watchlist", "items": ["Experimental channel"]},
                ],
            ),
            SlideItem(
                title="Table summary",
                layout_variant="table_summary",
                table_spec={
                    "headers": ["Workstream", "Decision"],
                    "rows": [["Sales", "Invest"], ["Ops", "Automate"], ["Support", "Consolidate"]],
                },
            ),
            SlideItem(
                title="Closing",
                slide_type=SlideType.CLOSING,
                key_message="Approve the phase-one scope this week.",
                bullets=["Decision required"],
            ),
        ],
    )
    output_path = tmp_path / "gamma_upgrade.pptx"
    result = PPTXGenerator().generate(outline, output_path)
    assert result.exists()
    assert result.stat().st_size > 0
    assert outline.slides[2].micro_polish_applied is True
    assert outline.slides[5].micro_polish_applied is True
    assert outline.slides[6].micro_polish_applied is True
    assert outline.slides[8].micro_polish_applied is True


def test_pptx_generator_renders_native_donut_chart(tmp_path: Path):
    outline = Outline(
        title="Chart deck",
        slides=[
            SlideItem(
                title="Channel mix",
                layout_variant="chart_focus",
                chart_spec={
                    "type": "donut",
                    "series": [
                        {"label": "Direct", "value": 42},
                        {"label": "Partner", "value": 33},
                        {"label": "Inbound", "value": 25},
                    ],
                    "insight": "Direct remains the largest growth engine.",
                },
                key_message="Protect direct momentum while improving partner productivity.",
            )
        ],
    )
    output_path = tmp_path / "chart_focus.pptx"
    PPTXGenerator().generate(outline, output_path)
    assert output_path.exists()


def test_preview_qa_flags_dense_edge_content(tmp_path: Path):
    image_path = tmp_path / "dense.png"
    image = Image.new("RGB", (1600, 900), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    draw.rectangle((120, 120, 1500, 780), fill="#111827")
    draw.rectangle((1450, 0, 1599, 899), fill="#0F172A")
    image.save(image_path)

    report = PreviewQAGate(_DummyConfig()).analyze_image(image_path)
    assert report["flags"]
    assert any("density" in flag.lower() or "clipping" in flag.lower() for flag in report["flags"])


def test_preview_qa_auto_remediation_simplifies_dense_data_slides():
    outline = Outline(
        title="Dense preview",
        slides=[
            SlideItem(
                title="Dense KPIs",
                layout_variant="kpi_grid",
                stats=[
                    {"label": "Revenue Growth", "value": "+18%", "insight": "Healthy growth momentum across enterprise accounts"},
                    {"label": "Gross Margin", "value": "-3pt", "insight": "Pressure persists in custom delivery work"},
                    {"label": "NPS", "value": "62", "insight": "Customers responded well to the service fixes"},
                    {"label": "Cycle Time", "value": "-2 days", "insight": "Approvals and handoffs are moving faster"},
                ],
                key_message="Performance is strong, but margin quality needs a tighter operating response.",
                qa_flags=["High visual density detected in rendered slide."],
                preview_density_score=0.33,
            ),
            SlideItem(
                title="Dense Table",
                layout_variant="table_summary",
                table_spec={
                    "headers": ["Priority", "Owner", "Action", "Target"],
                    "rows": [
                        ["Margin recovery", "Finance", "Tighten discount guardrails across custom work", "2 weeks"],
                        ["Retention", "CS", "Launch the at-risk playbook for large accounts", "3 weeks"],
                        ["Velocity", "Ops", "Reduce approval steps and remove redundant reviews", "30 days"],
                        ["Expansion", "Sales", "Upsell the top 20 accounts with better packaging", "30 days"],
                        ["Enablement", "RevOps", "Refresh partner materials and reporting cadence", "30 days"],
                    ],
                },
                qa_flags=["Crowded lower third detected in rendered slide."],
                preview_density_score=0.31,
            ),
        ],
    )
    gate = PreviewQAGate(_DummyConfig())
    remediated, applied = gate.auto_remediate_outline(outline)
    assert applied is True
    assert remediated.slides[0].layout_variant == "stats_highlight"
    assert len(remediated.slides[1].table_spec["rows"]) == 4
    assert remediated.slides[0].critique_notes


def test_preview_qa_selects_best_remediation_variant():
    class _VariantGate(PreviewQAGate):
        def _render_variant_report(self, outline, template_id, slide_index):
            candidate = Outline.from_dict(outline.to_dict())
            slide = candidate.slides[slide_index]
            slide.qa_flags = []
            if slide.layout_variant == "stats_highlight":
                slide.preview_density_score = 0.12
            else:
                slide.preview_density_score = 0.29
                slide.qa_flags = ["High visual density detected in rendered slide."]
            candidate.qa_findings = []
            return candidate

    outline = Outline(
        title="Variant selection",
        slides=[
            SlideItem(
                title="Dense KPIs",
                layout_variant="kpi_grid",
                stats=[
                    {"label": "Revenue Growth", "value": "+18%", "insight": "Healthy growth momentum across enterprise accounts"},
                    {"label": "Gross Margin", "value": "-3pt", "insight": "Pressure persists in custom delivery work"},
                    {"label": "NPS", "value": "62", "insight": "Customers responded well to the service fixes"},
                    {"label": "Cycle Time", "value": "-2 days", "insight": "Approvals and handoffs are moving faster"},
                ],
                qa_flags=["High visual density detected in rendered slide."],
                preview_density_score=0.33,
            )
        ],
    )
    gate = _VariantGate(_DummyConfig())
    selected, applied = gate.choose_best_remediation_variant(outline, template_id="executive_blue")
    assert applied is True
    assert selected.slides[0].layout_variant == "stats_highlight"
    assert selected.slides[0].critique_notes


def test_preview_qa_can_select_decision_summary_family():
    class _DecisionVariantGate(PreviewQAGate):
        def _render_variant_report(self, outline, template_id, slide_index):
            candidate = Outline.from_dict(outline.to_dict())
            slide = candidate.slides[slide_index]
            slide.qa_flags = []
            if slide.remediation_variant == "decision_summary":
                slide.preview_density_score = 0.09
            elif slide.remediation_variant == "compact":
                slide.preview_density_score = 0.15
            else:
                slide.preview_density_score = 0.27
                slide.qa_flags = ["Crowded lower third detected in rendered slide."]
            candidate.qa_findings = []
            return candidate

    outline = Outline(
        title="Decision family",
        slides=[
            SlideItem(
                title="Dense Table",
                layout_variant="table_summary",
                storyline_role="insight",
                table_spec={
                    "headers": ["Priority", "Owner", "Action", "Target"],
                    "rows": [
                        ["Margin recovery", "Finance", "Tighten discount guardrails across custom work", "2 weeks"],
                        ["Retention", "CS", "Launch the at-risk playbook for large accounts", "3 weeks"],
                        ["Velocity", "Ops", "Reduce approval steps and remove redundant reviews", "30 days"],
                        ["Expansion", "Sales", "Upsell the top 20 accounts with better packaging", "30 days"],
                    ],
                },
                qa_flags=["Crowded lower third detected in rendered slide."],
                preview_density_score=0.31,
            )
        ],
    )
    gate = _DecisionVariantGate(_DummyConfig())
    selected, applied = gate.choose_best_remediation_variant(outline, template_id="executive_blue")
    assert applied is True
    assert selected.slides[0].remediation_variant == "decision_summary"
    assert selected.slides[0].layout_variant == "content_2col"
    assert selected.slides[0].bullets


def test_pptx_generator_falls_back_when_comparison_data_is_incomplete(tmp_path: Path):
    outline = Outline(
        title="Fallback",
        slides=[
            SlideItem(
                title="Comparison fallback",
                layout_variant="comparison_before_after",
                sections=[{"title": "Before", "items": ["Only one side"]}],
                bullets=["Fallback point 1", "Fallback point 2"],
            )
        ],
    )
    output_path = tmp_path / "fallback.pptx"
    PPTXGenerator().generate(outline, output_path)
    assert output_path.exists()


def test_pptx_generator_creates_output_directory(tmp_path: Path):
    outline = Outline(
        title="Nested Output",
        slides=[SlideItem(title="Nested Output", layout_variant="content_2col", bullets=["One", "Two"])],
    )
    output_path = tmp_path / "nested" / "exports" / "deck.pptx"
    PPTXGenerator().generate(outline, output_path)
    assert output_path.exists()


def test_pptx_generator_preserves_vietnamese_unicode(tmp_path: Path):
    outline = Outline(
        title="Tiếng Việt",
        slides=[
            SlideItem(
                title="Mục tiêu Workshop",
                layout_variant="content_2col",
                summary="Tạo môi trường an toàn để lên tiếng, học hỏi và hợp tác tốt hơn.",
                bullets=["Nhận biết dấu hiệu thiếu an toàn tâm lý"],
            )
        ],
    )
    output_path = tmp_path / "unicode_vi.pptx"
    PPTXGenerator().generate(outline, output_path)
    with zipfile.ZipFile(output_path) as archive:
        slide_xml = archive.read("ppt/slides/slide1.xml").decode("utf-8")
    assert "Mục tiêu Workshop" in slide_xml
    assert "Tạo môi trường an toàn để lên tiếng" in slide_xml


class _DummyConfig:
    def get(self, key, default=None):
        return default


class _NoopCascade:
    def generate_content(self, prompt, generation_config=None):
        raise RuntimeError("skip remote rewrite in unit tests")


class _SelfCritiqueCascade:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def generate_content(self, prompt, generation_config=None):
        self.calls += 1

        class _Response:
            def __init__(self, text):
                self.text = text

        return _Response(self.payload)


def test_storyline_engine_assigns_roles_and_marks_rewritten():
    outline = Outline(
        title="Workshop Psychological Safety",
        slides=[
            SlideItem(title="Workshop Psychological Safety", slide_type=SlideType.TITLE, subtitle="A very long subtitle that should stay readable in the deck"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["Context", "Practice", "Commitment"]),
            SlideItem(title="Discussion mechanics", layout_variant="process_flow", sections=[{"title": "Steps", "items": ["Listen", "Reflect", "Share", "Commit"]}]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Start tomorrow with one concrete action"]),
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Build a workshop deck", {})
    roles = [slide.storyline_role for slide in result.slides]
    assert roles == ["opener", "roadmap", "mechanism", "call_to_action"]
    assert all(slide.rewritten for slide in result.slides)
    assert result.slides[1].key_message != ""


def test_storyline_engine_compresses_long_lines():
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    long_text = "Đây là một câu rất dài, có nhiều vế, nhằm kiểm tra xem engine có thể rút gọn ý chính và giữ cho tiêu đề hoặc bullet gọn hơn khi đưa lên slide hay không."
    compressed = engine._compress_line(long_text, max_len=70)
    assert len(compressed) <= 70
    assert compressed


def test_storyline_engine_visual_refinement_rebalances_layouts():
    outline = Outline(
        title="Visual refinement",
        slides=[
            SlideItem(
                title="Metrics",
                layout_variant="stats_highlight",
                stats=[
                    {"label": "Revenue", "value": "+18%", "insight": "Good"},
                    {"label": "Margin", "value": "+2pt", "insight": "Better"},
                    {"label": "NPS", "value": "62", "insight": "Up"},
                ],
            ),
            SlideItem(
                title="Illustration pending",
                layout_variant="content_image_right",
                bullets=["One point", "Second point"],
            ),
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Build a business update", {"candidate_strategy": "data_storytelling"})
    assert result.slides[0].layout_variant == "kpi_grid"
    assert result.slides[0].visual_treatment == "insight_first_data"
    assert result.slides[1].layout_variant == "content_2col"


def test_storyline_engine_builds_qa_report_for_dense_and_invalid_slides():
    outline = Outline(
        title="QA check",
        slides=[
            SlideItem(
                title="This title is intentionally very long so the QA pass should flag hierarchy risk on the slide",
                layout_variant="content_image_right",
                summary="This summary is intentionally long and verbose so the QA layer can flag that the slide is visually dense and likely needs more whitespace or tighter wording before export to PowerPoint.",
                bullets=["Point 1", "Point 2", "Point 3", "Point 4"],
            )
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Build a business update", {})
    assert result.qa_findings
    assert "QA found" in result.qa_summary
    assert result.slides[0].qa_flags


def test_ai_service_candidate_strategies_are_named():
    service = AIService()
    strategies = [service._candidate_strategy_hint(i, 4, {})[0] for i in range(4)]
    assert strategies == ["executive", "workshop", "persuasive", "data_storytelling"]


def test_ai_service_stable_mode_uses_single_candidate_and_stable_strategy():
    service = AIService()
    assert service._resolve_candidate_count(8, {"stable_mode": True}) == 1
    assert service._candidate_strategy_hint(0, 1, {"stable_mode": True})[0] == "stable"


def test_ai_service_stabilize_outline_downgrades_fragile_layouts():
    service = AIService()
    outline = Outline(
        title="Fragile deck",
        slides=[
            SlideItem(title="Image slide", layout_variant="content_image_right", bullets=["One", "Two"]),
            SlideItem(title="Chart slide", layout_variant="chart_focus", stats=[{"label": "Revenue", "value": 10, "insight": ""}]),
            SlideItem(
                title="Table slide",
                layout_variant="table_summary",
                table_spec={"headers": ["Area", "Decision"], "rows": [["Ops", "Automate"], ["Sales", "Invest"]]},
            ),
        ],
    )
    result = service._stabilize_outline(outline)
    assert result.slides[0].layout_variant == "content_2col"
    assert result.slides[1].layout_variant == "stats_highlight"
    assert result.slides[2].layout_variant == "content_2col"
    assert result.slides[2].bullets


def test_ai_service_uses_fast_interactive_path_for_single_key():
    service = AIService()
    service.cascade.api_keys = ["one-key"]
    assert service._use_fast_interactive_path({"interactive_ui": True}) is True
    assert service._resolve_candidate_count(8, {"fast_interactive_path": True}) == 1


def test_storyline_engine_fast_path_skips_model_passes():
    class _CountingCascade:
        def __init__(self):
            self.calls = 0

        def generate_content(self, prompt, generation_config=None):
            self.calls += 1
            raise RuntimeError("should not be called in fast path")

    cascade = _CountingCascade()
    engine = StorylineEngine(cascade, _DummyConfig())
    outline = Outline(
        title="Fast path",
        slides=[
            SlideItem(title="Fast path", slide_type=SlideType.TITLE, subtitle="Opener"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["One", "Two", "Three"]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Act now"]),
        ],
    )
    result = engine.rewrite_outline(outline, "Create a deck", {"fast_interactive_path": True})
    assert cascade.calls == 0
    assert result.quality_summary


def test_storyline_engine_repairs_generic_roadmap_and_strengthens_cta():
    outline = Outline(
        title="Operational Excellence",
        slides=[
            SlideItem(title="Operational Excellence", slide_type=SlideType.TITLE, subtitle="Build a stronger operating rhythm"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["Context", "Plan", "Summary"]),
            SlideItem(title="Root causes", layout_variant="content_2col", bullets=["Manual handoffs create delay", "Ownership is fragmented"]),
            SlideItem(title="Future process", layout_variant="process_flow", sections=[{"title": "Steps", "items": ["Intake", "Triage", "Execute", "Review"]}]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Do it"]),
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Create an ops deck", {})
    roadmap = result.slides[1]
    closing = result.slides[-1]
    assert roadmap.bullets[0] != "Context"
    assert roadmap.critique_notes
    assert "cụ thể" in closing.bullets[0].lower()
    assert closing.critique_notes


def test_storyline_engine_flags_and_differentiates_duplicate_ideas():
    outline = Outline(
        title="Duplicate deck",
        slides=[
            SlideItem(title="Title", slide_type=SlideType.TITLE, subtitle="Deck opener"),
            SlideItem(title="Problem statement", layout_variant="content_2col", bullets=["Slow approvals", "Manual follow-up"]),
            SlideItem(title="Problem statement", layout_variant="content_2col", bullets=["Slow approvals", "Manual follow-up"]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Start tomorrow with one clear action"]),
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Find duplicate ideas", {})
    duplicate_slide = result.slides[2]
    assert duplicate_slide.critique_notes
    assert duplicate_slide.title != "Problem statement"


def test_storyline_engine_applies_self_critique_merge():
    payload = """
    {
      "title": "Operational Excellence",
      "language": "en",
      "schema_version": "2.0",
      "slides": [
        {
          "title": "Operational Excellence",
          "slide_type": "title",
          "layout_variant": "title_hero",
          "subtitle": "Sharper opener",
          "summary": "",
          "bullets": [],
          "key_message": ""
        },
        {
          "title": "Agenda",
          "slide_type": "content",
          "layout_variant": "agenda",
          "subtitle": "",
          "summary": "A clearer roadmap for the audience.",
          "bullets": ["Why this matters", "What changes", "What to do next"],
          "key_message": "Make the flow explicit from the start."
        },
        {
          "title": "Close: Hành động tiếp theo",
          "slide_type": "closing",
          "layout_variant": "closing_cta",
          "subtitle": "",
          "summary": "End with a specific commitment.",
          "bullets": ["Choose one concrete action and start tomorrow."],
          "key_message": "Turn insight into a measurable next step."
        }
      ]
    }
    """
    outline = Outline(
        title="Operational Excellence",
        slides=[
            SlideItem(title="Operational Excellence", slide_type=SlideType.TITLE, subtitle="Build a stronger operating rhythm"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["Context", "Plan", "Summary"]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Do it"]),
        ],
    )
    engine = StorylineEngine(_SelfCritiqueCascade(payload), _DummyConfig())
    result = engine.rewrite_outline(outline, "Create an ops deck", {})
    assert all(slide.self_critique_applied for slide in result.slides)
    assert result.slides[1].summary == "A clearer roadmap for the audience."
    assert result.slides[-1].key_message == "Turn insight into a measurable next step."


def test_storyline_engine_self_critique_falls_back_on_invalid_output():
    class _BadCascade:
        def __init__(self):
            self.calls = 0

        def generate_content(self, prompt, generation_config=None):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("skip rewrite")

            class _Response:
                text = '{"title":"Bad","slides":[{"title":"Only one slide"}]}'

            return _Response()

    outline = Outline(
        title="Fallback self critique",
        slides=[
            SlideItem(title="Fallback self critique", slide_type=SlideType.TITLE, subtitle="Open"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["Context", "Plan", "Summary"]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Do it"]),
        ],
    )
    engine = StorylineEngine(_BadCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Create a deck", {})
    assert not any(slide.self_critique_applied for slide in result.slides)
    assert result.slides[-1].bullets


def test_storyline_engine_scores_outline_and_sets_summary():
    outline = Outline(
        title="Operational Excellence",
        slides=[
            SlideItem(title="Operational Excellence", slide_type=SlideType.TITLE, subtitle="Build a stronger operating rhythm"),
            SlideItem(title="Agenda", layout_variant="agenda", bullets=["Context", "Plan", "Summary"]),
            SlideItem(title="Root causes", layout_variant="content_2col", bullets=["Manual handoffs create delay", "Ownership is fragmented"]),
            SlideItem(title="Future process", layout_variant="process_flow", sections=[{"title": "Steps", "items": ["Intake", "Triage", "Execute", "Review"]}]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Choose one concrete action and start tomorrow"]),
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Create an ops deck", {})
    assert result.quality_scores["overall"] > 0
    assert "clarity" in result.quality_scores
    assert result.quality_summary
    assert isinstance(result.should_rewrite_again, bool)


def test_storyline_engine_flags_weak_deck_for_rewrite():
    outline = Outline(
        title="Weak deck",
        slides=[
            SlideItem(title="Weak deck", slide_type=SlideType.TITLE),
            SlideItem(title="Topic", layout_variant="content_2col", bullets=["Thing", "Thing"]),
            SlideItem(title="Topic", layout_variant="content_2col", bullets=["Thing", "Thing"]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Do it"]),
        ],
    )
    engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    result = engine.rewrite_outline(outline, "Make a weak deck", {})
    assert result.quality_flags
    assert result.should_rewrite_again is True


def test_storyline_engine_improves_if_needed_uses_retry_round():
    payload = """
    {
      "title": "Weak deck",
      "language": "en",
      "schema_version": "2.0",
      "slides": [
        {"title": "Weak deck", "slide_type": "title", "layout_variant": "title_hero", "subtitle": "Sharper opener", "summary": "", "bullets": [], "key_message": ""},
        {"title": "Agenda", "slide_type": "content", "layout_variant": "agenda", "summary": "Clear roadmap.", "bullets": ["Why this matters", "What changes", "What to do next"], "key_message": "Follow the story in order."},
        {"title": "Point of view", "slide_type": "content", "layout_variant": "content_2col", "summary": "Distinct angle.", "bullets": ["Specific point one", "Specific point two"], "key_message": "Show one clear insight."},
        {"title": "Close: Hành động tiếp theo", "slide_type": "closing", "layout_variant": "closing_cta", "summary": "Commit clearly.", "bullets": ["Choose one concrete action and start tomorrow."], "key_message": "Turn insight into action."}
      ]
    }
    """
    outline = Outline(
        title="Weak deck",
        slides=[
            SlideItem(title="Weak deck", slide_type=SlideType.TITLE),
            SlideItem(title="Topic", layout_variant="content_2col", bullets=["Thing", "Thing"]),
            SlideItem(title="Topic", layout_variant="content_2col", bullets=["Thing", "Thing"]),
            SlideItem(title="Close", slide_type=SlideType.CLOSING, bullets=["Do it"]),
        ],
    )
    scoring_engine = StorylineEngine(_NoopCascade(), _DummyConfig())
    scored = scoring_engine.rewrite_outline(outline, "Make a weak deck", {})
    retry_engine = StorylineEngine(_SelfCritiqueCascade(payload), _DummyConfig())
    result = retry_engine.improve_if_needed(scored, "Make a weak deck", {}, max_rounds=1)
    assert result.quality_retry_count == 1
    assert result.slides[1].summary == "Clear roadmap."


def test_model_cascade_sanitizes_non_text_models():
    cascade = object.__new__(ModelCascade)
    models = [
        ModelConfig("gemini-3-flash-preview"),
        ModelConfig("gemini-2.5-flash-preview-tts"),
        ModelConfig("imagen-4.0-ultra-generate-001"),
        ModelConfig("veo-3.1-generate-preview"),
        ModelConfig("gemma-3-4b-it"),
    ]
    sanitized = ModelCascade._sanitize_models(cascade, models)
    ids = [model.model_id for model in sanitized]
    assert "gemini-3-flash-preview" in ids
    assert "gemma-3-4b-it" in ids
    assert "gemini-2.5-flash-preview-tts" not in ids
    assert "imagen-4.0-ultra-generate-001" not in ids
    assert "veo-3.1-generate-preview" not in ids


def test_ai_service_selects_best_candidate_by_quality():
    service = object.__new__(AIService)
    candidate_a = Outline(title="Candidate A")
    candidate_a.quality_scores = {"clarity": 70, "flow": 72, "distinctness": 68, "cta_strength": 80, "overall": 72}
    candidate_a.quality_flags = ["needs work"]
    candidate_a.quality_retry_count = 1

    candidate_b = Outline(title="Candidate B")
    candidate_b.quality_scores = {"clarity": 86, "flow": 84, "distinctness": 82, "cta_strength": 90, "overall": 86}
    candidate_b.quality_flags = []
    candidate_b.quality_retry_count = 0

    selected = AIService._select_best_outline(service, [candidate_a, candidate_b])
    assert selected.title == "Candidate B"
    assert selected.candidate_count_generated == 2
    assert selected.selected_candidate_index == 1
    assert len(selected.candidate_scores) == 2
    assert selected.selected_candidate_rationale
