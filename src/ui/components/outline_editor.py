"""Outline Editor Component - Display generated semantic slide specs."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.data.models import Outline, SlideItem


class SlideCard(QFrame):
    """Card representing a single slide in the outline."""

    edit_clicked = Signal(int)
    delete_clicked = Signal(int)

    def __init__(self, index: int, slide: SlideItem):
        super().__init__()
        self.index = index
        self.slide = slide
        self.setProperty("class", "card")
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(
            """
            SlideCard {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
            SlideCard:hover {
                border-color: #8B5CF6;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        num_label = QLabel(f"Slide {self.index + 1}")
        num_label.setStyleSheet("font-size: 12px; color: #8B5CF6; font-weight: 600;")
        header.addWidget(num_label)

        type_label = QLabel(f"[{self.slide.slide_type.value}]")
        type_label.setStyleSheet("font-size: 11px; color: #64748B;")
        header.addWidget(type_label)

        layout_label = QLabel(self.slide.layout_variant)
        layout_label.setStyleSheet("font-size: 11px; color: #38BDF8; font-weight: 600;")
        header.addWidget(layout_label)

        if self.slide.storyline_role:
            role_label = QLabel(self.slide.storyline_role)
            role_label.setStyleSheet("font-size: 11px; color: #A3E635; font-weight: 600;")
            role_label.setToolTip(self.slide.storyline_intent or self.slide.storyline_role)
            header.addWidget(role_label)

        if self.slide.density_level:
            density_label = QLabel(self.slide.density_level)
            density_color = "#F59E0B" if self.slide.density_level == "dense" else "#94A3B8"
            density_label.setStyleSheet(f"font-size: 11px; color: {density_color}; font-weight: 600;")
            density_label.setToolTip("Estimated visual density")
            header.addWidget(density_label)

        if self.slide.image_prompt or self.slide.image_path:
            img_indicator = QLabel("IMG")
            img_indicator.setStyleSheet("font-size: 11px; color: #F59E0B; font-weight: 600;")
            img_indicator.setToolTip("Slide có hình ảnh hoặc image prompt.")
            header.addWidget(img_indicator)

        header.addStretch()

        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("background: transparent; border: none; font-size: 16px;")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        header.addWidget(delete_btn)
        layout.addLayout(header)

        title = QLabel(self.slide.title)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        title.setWordWrap(True)
        layout.addWidget(title)

        preview_items = self.slide.semantic_preview[:4]
        for point in preview_items:
            bullet = QLabel(f"• {point}")
            bullet.setStyleSheet("font-size: 13px; color: #94A3B8; padding-left: 8px;")
            bullet.setWordWrap(True)
            layout.addWidget(bullet)

        if self.slide.rewritten:
            rewritten_label = QLabel("Rewritten for storyline clarity")
            rewritten_label.setStyleSheet("font-size: 12px; color: #60A5FA;")
            layout.addWidget(rewritten_label)

        if self.slide.self_critique_applied:
            self_critique_label = QLabel("AI self-critique applied")
            self_critique_label.setStyleSheet("font-size: 12px; color: #C084FC;")
            layout.addWidget(self_critique_label)

        if self.slide.stats:
            stats_label = QLabel(f"{len(self.slide.stats)} stat cards")
            stats_label.setStyleSheet("font-size: 12px; color: #A3E635;")
            layout.addWidget(stats_label)

        if self.slide.visual_treatment:
            visual_label = QLabel(f"Visual: {self.slide.visual_treatment}")
            visual_label.setStyleSheet("font-size: 12px; color: #38BDF8;")
            layout.addWidget(visual_label)

        if self.slide.micro_polish_applied:
            polish_label = QLabel("Micro-polish applied")
            polish_label.setStyleSheet("font-size: 12px; color: #F59E0B;")
            layout.addWidget(polish_label)

        if self.slide.preview_density_score:
            preview_label = QLabel(f"Preview density: {self.slide.preview_density_score:.2f}")
            preview_label.setStyleSheet("font-size: 12px; color: #FB7185;")
            layout.addWidget(preview_label)

        if self.slide.remediation_variant:
            variant_label = QLabel(f"Variant: {self.slide.remediation_variant}")
            variant_label.setStyleSheet("font-size: 12px; color: #FDE68A;")
            layout.addWidget(variant_label)

        if self.slide.sections and self.slide.layout_variant in {"comparison_before_after", "process_flow"}:
            sections_label = QLabel(f"{len(self.slide.sections)} semantic sections")
            sections_label.setStyleSheet("font-size: 12px; color: #F59E0B;")
            layout.addWidget(sections_label)

        for warning in self.slide.render_warnings[:2]:
            warn_label = QLabel(f"Warning: {warning}")
            warn_label.setStyleSheet("font-size: 12px; color: #FCA5A5;")
            warn_label.setWordWrap(True)
            layout.addWidget(warn_label)

        for critique in self.slide.critique_notes[:2]:
            critique_label = QLabel(f"Critique: {critique}")
            critique_label.setStyleSheet("font-size: 12px; color: #FBBF24;")
            critique_label.setWordWrap(True)
            layout.addWidget(critique_label)

        for qa_flag in self.slide.qa_flags[:2]:
            qa_label = QLabel(f"QA: {qa_flag}")
            qa_label.setStyleSheet("font-size: 12px; color: #FCA5A5;")
            qa_label.setWordWrap(True)
            layout.addWidget(qa_label)


class OutlineEditor(QWidget):
    """Editor for the generated presentation outline."""

    outline_changed = Signal()
    export_clicked = Signal()
    translate_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.outline = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header = QHBoxLayout()
        self.title_label = QLabel("Dàn ý")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)
        header.addStretch()
        self.slide_count = QLabel("")
        self.slide_count.setStyleSheet("color: #64748B;")
        header.addWidget(self.slide_count)
        layout.addLayout(header)

        self.quality_label = QLabel("")
        self.quality_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self.quality_label.setWordWrap(True)
        layout.addWidget(self.quality_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 8, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.translate_btn = QPushButton("Dịch slide")
        self.translate_btn.setObjectName("secondaryBtn")
        self.translate_btn.setMinimumHeight(44)
        self.translate_btn.clicked.connect(self.translate_clicked.emit)
        self.translate_btn.setVisible(False)
        btn_row.addWidget(self.translate_btn)

        self.export_btn = QPushButton("Xuất PowerPoint")
        self.export_btn.setObjectName("primaryBtn")
        self.export_btn.setMinimumHeight(44)
        self.export_btn.clicked.connect(self.export_clicked.emit)
        self.export_btn.setVisible(False)
        btn_row.addWidget(self.export_btn)

        layout.addLayout(btn_row)

    def set_outline(self, outline: Outline):
        self.outline = outline
        self._refresh_cards()

    def _refresh_cards(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.outline:
            return

        self.title_label.setText(self.outline.title)
        self.slide_count.setText(f"{self.outline.slide_count} slides · schema {self.outline.schema_version}")
        scores = self.outline.quality_scores or {}
        if scores:
            summary = self.outline.quality_summary or ""
            if self.outline.candidate_count_generated > 1:
                summary = (
                    f"Candidate {self.outline.selected_candidate_index + 1}/"
                    f"{self.outline.candidate_count_generated}. {summary}"
                )
            if self.outline.candidate_strategy:
                summary = f"{summary} Strategy: {self.outline.candidate_strategy}."
            if self.outline.quality_retry_count:
                summary = f"{summary} Retry rounds: {self.outline.quality_retry_count}."
            if self.outline.quality_flags:
                summary = f"{summary} Flags: {' | '.join(self.outline.quality_flags[:2])}"
            if self.outline.qa_summary:
                summary = f"{summary} {self.outline.qa_summary}"
            if self.outline.preview_qa_applied:
                summary = f"{summary} Preview QA applied."
            if self.outline.selected_candidate_rationale:
                summary = f"{summary} {self.outline.selected_candidate_rationale}"
            self.quality_label.setText(summary)
        else:
            self.quality_label.setText("")

        for index, slide in enumerate(self.outline.slides):
            card = SlideCard(index, slide)
            card.delete_clicked.connect(self._on_delete_slide)
            self.cards_layout.insertWidget(index, card)

        self.export_btn.setVisible(True)
        self.translate_btn.setVisible(True)

    def _on_delete_slide(self, index: int):
        if self.outline and 0 <= index < len(self.outline.slides):
            self.outline.remove_slide(index)
            self._refresh_cards()
            self.outline_changed.emit()

    def get_outline(self) -> Outline:
        return self.outline

    def clear(self):
        self.outline = None
        self.title_label.setText("Dàn ý")
        self.slide_count.setText("")
        self.quality_label.setText("")
        self.export_btn.setVisible(False)
        self.translate_btn.setVisible(False)

        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
