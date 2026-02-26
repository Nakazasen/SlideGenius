"""Diagram Drawer - Smart Shape Generation."""
from dataclasses import dataclass
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE

HEX_COLOR_MAP = {
    "primary": "#3B82F6",    # Blue
    "secondary": "#1E40AF",  # Dark Blue
    "accent": "#F97316",     # Orange
    "success": "#10B981",    # Green
    "danger": "#EF4444",     # Red
    "warning": "#F59E0B",    # Yellow
    "neutral": "#94A3B8"     # Gray
}

@dataclass
class NodeStyle:
    """Style for a diagram node."""
    fill_color: str = HEX_COLOR_MAP["primary"]
    text_color: str = "#FFFFFF"
    shape_type: MSO_SHAPE = MSO_SHAPE.ROUNDED_RECTANGLE
    width: float = 2.0
    height: float = 1.0


class DiagramDrawer:
    """Draws smart diagrams on PowerPoint slides."""

    def __init__(self, slide):
        """Initialize with a pptx slide object."""
        self.slide = slide
        self.shapes = slide.shapes

    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """Convert hex string to RGBColor."""
        hex_color = hex_color.lstrip('#')
        try:
            return RGBColor(
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )
        except ValueError:
            return RGBColor(128, 128, 128)  # Fallback gray

    def draw_node(self, x_inch: float, y_inch: float, text: str, style: NodeStyle = None):
        """Draw a single node (shape with text)."""
        if style is None:
            style = NodeStyle()

        # Add shape
        shape = self.shapes.add_shape(
            style.shape_type,
            Inches(x_inch), Inches(y_inch),
            Inches(style.width), Inches(style.height)
        )

        # Style shape
        fill = shape.fill
        fill.solid()
        fill.fore_color.rgb = self._hex_to_rgb(style.fill_color)
        
        line = shape.line
        line.color.rgb = self._hex_to_rgb(style.text_color)
        line.width = Pt(1.5)

        # Add text
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(style.text_color)
        p.font.name = "Arial"

        return shape

    def draw_connector(self, shape_from, shape_to, label: str = ""):
        """Draw an arrow connecting two shapes."""
        # Simple center-to-center connection for MVP
        # Ideally, pptx allows 'connectors' that attach to connection points, 
        # but creating them programmatically via simple connectors is easier and safer.
        
        connector = self.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, 
            0, 0, 0, 0 # Dummy pos, will connect
        )
        
        # Connect start/end
        connector.begin_connect(shape_from, 3) # 3 = bottom (usually) - let's try auto or specific index
        connector.end_connect(shape_to, 1)     # 1 = top
        
        # Style
        line = connector.line
        line.width = Pt(2)
        line.color.rgb = self._hex_to_rgb("#64748B")
        line.dash_style = MSO_LINE.SOLID
        
        # TODO: Add label text if needed (requires a separate textbox near the line)
        return connector

    def draw_process_flow(self, nodes_data: List[Dict[str, Any]]):
        """Draw a linear process flow automatically layouted."""
        # Simple layout: Horizontal centered
        start_x = 1.0
        y = 4.5  # Shifted down from 3.5 to avoid text overlap
        gap = 0.5
        box_width = 2.5
        
        previous_shape = None
        
        for i, node_data in enumerate(nodes_data):
            text = node_data.get("text", "Step")
            color_key = "primary"
            if node_data.get("highlight"): color_key = "accent"
            
            style = NodeStyle(fill_color=HEX_COLOR_MAP.get(color_key, HEX_COLOR_MAP["neutral"]))
            
            x = start_x + i * (box_width + gap)
            shape = self.draw_node(x, y, text, style)
            
            if previous_shape:
                 # Connect to previous
                 # Note: pptx connector logic is tricky. For MVP, we might just draw lines manually if connectors fail.
                 # But let's try the proper Connector objects first.
                 try:
                     from pptx.enum.shapes import MSO_CONNECTOR
                     connector = self.shapes.add_connector(
                        MSO_CONNECTOR.ELBOW,
                        Inches(1), Inches(1), Inches(2), Inches(2) # Initial placement
                     )
                     connector.begin_connect(previous_shape, 3) # Right side? No, indices map to connection points.
                     # Usually: 0=Top, 1=Right, 2=Bottom, 3=Left. Let's verify standard shapes.
                     # Actually: automatic routing is best if we can set it.
                     
                     # Force manual connection points:
                     # Connect Right of Prev to Left of Curr
                     connector.begin_connect(previous_shape, 1) # Right
                     connector.end_connect(shape, 3)            # Left
                     
                     line = connector.line
                     line.width = Pt(2)
                     line.color.rgb = self._hex_to_rgb("#94A3B8")
                     line.end_arrowhead = MSO_LINE.ARROW # This might need correct enum for arrow
                     
                 except Exception:
                     pass # Fail silently for connector in alpha
            
            previous_shape = shape

    def draw_comparison(self, diagram_data: Dict[str, Any]):
        """Draw a Before/After comparison diagram with center arrow."""
        before_data = diagram_data.get("before", {})
        after_data = diagram_data.get("after", {})
        benefits = diagram_data.get("benefits", [])
        
        # Layout: Two columns
        col_width = 5.0
        left_start = 0.5
        right_start = 7.8
        arrow_x = 6.0
        
        # --- Before Column (Left, Gray/Red) ---
        before_title = before_data.get("title", "Trước Cải Tiến")
        before_nodes = before_data.get("nodes", [])
        
        # Column Header (Shifted Y+1.0)
        header_style = NodeStyle(
            fill_color=HEX_COLOR_MAP["neutral"],
            width=col_width,
            height=0.6
        )
        self.draw_node(left_start, 2.8, before_title, header_style)
        
        # Before Nodes (Vertical)
        y = 3.6
        max_nodes = max(len(before_nodes), len(after_data.get("nodes", [])))
        # Calculate dynamic height based on number of nodes
        node_height = min(1.0, 3.5 / max(max_nodes, 1))
        gap = 0.2
        prev_shape = None
        
        for node in before_nodes:
            color = HEX_COLOR_MAP["danger"] if node.get("highlight") else HEX_COLOR_MAP["neutral"]
            style = NodeStyle(fill_color=color, width=col_width - 0.3, height=node_height)
            shape = self.draw_node(left_start + 0.15, y, node.get("text", ""), style)
            
            if prev_shape:
                try:
                    c = self.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0), Inches(0), Inches(0), Inches(0))
                    c.begin_connect(prev_shape, 2)  # Bottom
                    c.end_connect(shape, 0)         # Top
                    c.line.color.rgb = self._hex_to_rgb("#64748B")
                    c.line.width = Pt(1.5)
                except Exception:
                    pass
            prev_shape = shape
            y += node_height + gap
        
        # --- Center Arrow (Visual Separator) ---
        arrow_style = NodeStyle(
            fill_color=HEX_COLOR_MAP["accent"],
            text_color="#FFFFFF",
            width=1.3,
            height=0.8,
            shape_type=MSO_SHAPE.RIGHT_ARROW
        )
        self.draw_node(arrow_x, 3.5, "➡️", arrow_style)
        
        # --- After Column (Right, Green/Blue) ---
        after_title = after_data.get("title", "Sau Cải Tiến")
        after_nodes = after_data.get("nodes", [])
        
        # Column Header
        header_style_after = NodeStyle(
            fill_color=HEX_COLOR_MAP["success"],
            width=col_width,
            height=0.6
        )
        self.draw_node(right_start, 1.8, after_title, header_style_after)
        
        # After Nodes (Vertical)
        y = 2.6
        prev_shape = None
        for node in after_nodes:
            color = HEX_COLOR_MAP["primary"] if node.get("highlight") else HEX_COLOR_MAP["success"]
            style = NodeStyle(fill_color=color, width=col_width - 0.3, height=node_height)
            shape = self.draw_node(right_start + 0.15, y, node.get("text", ""), style)
            
            if prev_shape:
                try:
                    c = self.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0), Inches(0), Inches(0), Inches(0))
                    c.begin_connect(prev_shape, 2)
                    c.end_connect(shape, 0)
                    c.line.color.rgb = self._hex_to_rgb("#10B981")
                    c.line.width = Pt(1.5)
                except Exception:
                    pass
            prev_shape = shape
            y += node_height + gap
        
        # --- Benefits Section (Bottom) ---
        if benefits:
            benefits_text = "⭐ Lợi ích: " + " • ".join(benefits)
            benefits_style = NodeStyle(
                fill_color="#FEF3C7",
                text_color="#92400E",
                width=12.3,
                height=0.6,
                shape_type=MSO_SHAPE.ROUNDED_RECTANGLE
            )
            self.draw_node(0.5, 6.3, benefits_text, benefits_style)
