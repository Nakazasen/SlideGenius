"""PPTX Generator - Create PowerPoint presentations from outlines."""
from pathlib import Path
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import nsmap
from src.data.models import Outline, SlideItem, SlideType, Template


class PPTXGenerator:
    """Generate PowerPoint presentations from Outline objects."""
    
    # Default template settings
    DEFAULT_TEMPLATE = Template(
        name="modern_blue",
        display_name="Modern Blue",
        description="Clean modern design with blue accents",
        category="Business",
        primary_color="#3B82F6",
        secondary_color="#1E40AF",
        accent_color="#F97316",
        background_color="#FFFFFF",
        font_heading="Arial",
        font_body="Arial"
    )
    
    def __init__(self, template: Template = None):
        self.template = template or self.DEFAULT_TEMPLATE
        self.prs = None
        self._load_template_settings()
    
    def _load_template_settings(self):
        """Load font and template settings from config."""
        from src.data.config_manager import ConfigManager
        config = ConfigManager()
        
        # Get font settings from config
        heading_font = config.get("fonts.heading_font", "Arial")
        body_font = config.get("fonts.body_font", "Arial")
        
        # Update template with custom fonts
        self.template.font_heading = heading_font
        self.template.font_body = body_font
        
        # Get selected template and apply its colors
        selected_template = config.get("template.selected", "modern_blue")
        self._apply_template_colors(selected_template)
    
    def _apply_template_colors(self, template_id: str):
        """Apply colors based on selected template."""
        TEMPLATE_COLORS = {
            "modern_blue": ("#3B82F6", "#1E40AF", "#F97316"),
            "creative_orange": ("#F97316", "#EA580C", "#3B82F6"),
            "minimal_gray": ("#64748B", "#475569", "#8B5CF6"),
            "nature_green": ("#10B981", "#059669", "#F59E0B"),
            "purple_gradient": ("#8B5CF6", "#7C3AED", "#EC4899"),
        }
        
        colors = TEMPLATE_COLORS.get(template_id, TEMPLATE_COLORS["modern_blue"])
        self.template.primary_color = colors[0]
        self.template.secondary_color = colors[1]
        self.template.accent_color = colors[2]
    
    def generate(self, outline: Outline, output_path: Path = None) -> Path:
        """Generate PPTX file from outline."""
        # Create presentation
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)  # 16:9
        self.prs.slide_height = Inches(7.5)
        
        # Generate each slide
        for i, slide_item in enumerate(outline.slides):
            self._add_slide(slide_item, i)
        
        # Determine output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in outline.title if c.isalnum() or c in " -_")[:30]
            output_path = Path(f"{safe_title}_{timestamp}.pptx")
        
        # Save
        self.prs.save(str(output_path))
        return output_path
    
    def _add_slide(self, slide_item: SlideItem, index: int):
        """Add a slide to the presentation."""
        if slide_item.slide_type == SlideType.TITLE:
            self._add_title_slide(slide_item)
        elif slide_item.slide_type == SlideType.CLOSING:
            self._add_closing_slide(slide_item)
        elif slide_item.slide_type == SlideType.DIAGRAM:
            self._add_diagram_slide(slide_item)
        else:
            self._add_content_slide(slide_item)
    
    def _hex_to_rgb(self, hex_color: str):
        """Convert hex to RGB tuple for pptx."""
        from pptx.dml.color import RGBColor
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return RGBColor(r, g, b)
    
    def _add_title_slide(self, slide_item: SlideItem):
        """Add title slide."""
        slide_layout = self.prs.slide_layouts[6]  # Blank
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Background
        self._set_background(slide, self.template.primary_color)
        
        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(2.5), Inches(12.333), Inches(2)
        )
        tf = title_box.text_frame
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        p = tf.paragraphs[0]
        p.text = slide_item.title
        p.font.size = Pt(54)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb("#FFFFFF")
        p.font.name = self.template.font_heading
        
        # Subtitle
        if slide_item.content:
            subtitle_box = slide.shapes.add_textbox(
                Inches(1), Inches(4.5), Inches(11.333), Inches(1)
            )
            stf = subtitle_box.text_frame
            stf.paragraphs[0].alignment = PP_ALIGN.CENTER
            sp = stf.paragraphs[0]
            sp.text = slide_item.content[0] if slide_item.content else ""
            sp.font.size = Pt(24)
            sp.font.color.rgb = self._hex_to_rgb("#FFFFFF")
            sp.font.name = self.template.font_body
    
    def _add_content_slide(self, slide_item: SlideItem):
        """Add content/bullet slide."""
        slide_layout = self.prs.slide_layouts[6]  # Blank
        slide = self.prs.slides.add_slide(slide_layout)
        
        # White background
        self._set_background(slide, "#FFFFFF")
        
        # Accent bar at top
        accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15)
        )
        accent.fill.solid()
        accent.fill.fore_color.rgb = self._hex_to_rgb(self.template.primary_color)
        accent.line.fill.background()
        
        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.75), Inches(0.5), Inches(11.833), Inches(1)
        )
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_item.title
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(self.template.secondary_color)
        p.font.name = self.template.font_heading
        
        # Bullet points
        content_width = Inches(11.833)
        content_left = Inches(0.75)
        
        # === IMAGE HANDLING ===
        effective_image_path = None
        
        # 1. Check if we already have a path
        if slide_item.image_path and Path(slide_item.image_path).exists():
            effective_image_path = slide_item.image_path
            
        # 2. Try to generate if we have a prompt but no path
        elif slide_item.image_prompt:
            try:
                from src.core.image_generator import ImageGenerator
                img_gen = ImageGenerator()
                
                # Generate Image
                effective_image_path = img_gen.generate_image(slide_item.image_prompt)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to generate image: {e}")
        
        # 3. Insert Image if we found/generated one
        if effective_image_path and Path(effective_image_path).exists():
            # Layout: Left Content, Right Image
            content_width = Inches(6.5)
            
            # Insert Image
            slide.shapes.add_picture(
                str(effective_image_path), 
                Inches(7.5), Inches(1.8), 
                width=Inches(5.0), height=Inches(3.5)
            )

        if slide_item.content:
            content_box = slide.shapes.add_textbox(
                content_left, Inches(1.8), content_width, Inches(5)
            )
            ctf = content_box.text_frame
            ctf.word_wrap = True
            
            for i, point in enumerate(slide_item.content):
                if i == 0:
                    p = ctf.paragraphs[0]
                else:
                    p = ctf.add_paragraph()
                
                p.text = f"• {point}"
                p.font.size = Pt(22)
                p.font.color.rgb = self._hex_to_rgb("#1E293B")
                p.font.name = self.template.font_body
                p.space_after = Pt(16)
    
    def _add_closing_slide(self, slide_item: SlideItem):
        """Add closing slide."""
        slide_layout = self.prs.slide_layouts[6]  # Blank
        slide = self.prs.slides.add_slide(slide_layout)
        
        self._set_background(slide, self.template.primary_color)
        
        # Main text
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(2.5), Inches(12.333), Inches(2)
        )
        tf = title_box.text_frame
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        p = tf.paragraphs[0]
        p.text = slide_item.title
        p.font.size = Pt(48)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb("#FFFFFF")
        p.font.name = self.template.font_heading
        
        # Sub content
        if slide_item.content:
            sub_box = slide.shapes.add_textbox(
                Inches(1), Inches(4.5), Inches(11.333), Inches(2)
            )
            stf = sub_box.text_frame
            stf.paragraphs[0].alignment = PP_ALIGN.CENTER
            
            for i, point in enumerate(slide_item.content[:3]):
                if i == 0:
                    sp = stf.paragraphs[0]
                else:
                    sp = stf.add_paragraph()
                    sp.alignment = PP_ALIGN.CENTER
                
                sp.text = point
                sp.font.size = Pt(20)
                sp.font.color.rgb = self._hex_to_rgb("#FFFFFF")
                sp.font.name = self.template.font_body
    
    def _add_diagram_slide(self, slide_item: SlideItem):
        """Add a slide with a diagram."""
        from src.core.diagram_drawer import DiagramDrawer
        
        slide_layout = self.prs.slide_layouts[6]  # Blank
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Background
        self._set_background(slide, "#FFFFFF")
        
        # Title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.2), Inches(12.333), Inches(1.2)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide_item.title
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(self.template.secondary_color)
        p.font.name = self.template.font_heading
        p.alignment = PP_ALIGN.CENTER
        
        # Render Text Content (if any) - placed below title, above diagram
        if slide_item.content:
            content_box = slide.shapes.add_textbox(
                Inches(1.0), Inches(1.5), Inches(11.333), Inches(2.0)
            )
            ctf = content_box.text_frame
            ctf.word_wrap = True
            
            for i, point in enumerate(slide_item.content[:3]): # Limit to 3 lines to save space for diagram
                if i == 0:
                    p = ctf.paragraphs[0]
                else:
                    p = ctf.add_paragraph()
                p.text = f"• {point}"
                p.font.size = Pt(18)
                p.font.color.rgb = self._hex_to_rgb("#1E293B")
                p.font.name = self.template.font_body
                p.alignment = PP_ALIGN.LEFT
                p.space_after = Pt(10)

        # Draw Diagram (shifted down)
        
        # Draw Diagram
        if slide_item.diagram:
            drawer = DiagramDrawer(slide)
            
            diagram_type = slide_item.diagram.get("type", "process")
            
            if diagram_type == "comparison":
                drawer.draw_comparison(slide_item.diagram)
            else:
                # Default to process flow
                nodes = slide_item.diagram.get("nodes", [])
                if nodes:
                    drawer.draw_process_flow(nodes)

    def _set_background(self, slide, color: str):
        """Set slide background color."""
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self._hex_to_rgb(color)


# Built-in templates
TEMPLATES = {
    "modern_blue": Template(
        name="modern_blue",
        display_name="Modern Blue",
        description="Clean modern design with blue accents",
        category="Business",
        primary_color="#3B82F6",
        secondary_color="#1E40AF"
    ),
    "creative_orange": Template(
        name="creative_orange",
        display_name="Creative Orange",
        description="Vibrant and energetic design",
        category="Creative",
        primary_color="#F97316",
        secondary_color="#C2410C"
    ),
    "minimal_gray": Template(
        name="minimal_gray",
        display_name="Minimal Gray",
        description="Clean and professional",
        category="Minimal",
        primary_color="#64748B",
        secondary_color="#334155"
    ),
    "nature_green": Template(
        name="nature_green",
        display_name="Nature Green",
        description="Fresh and natural feel",
        category="Education",
        primary_color="#10B981",
        secondary_color="#047857"
    ),
    "purple_gradient": Template(
        name="purple_gradient",
        display_name="Purple Gradient",
        description="Modern and creative",
        category="Creative",
        primary_color="#8B5CF6",
        secondary_color="#6D28D9"
    ),
}
