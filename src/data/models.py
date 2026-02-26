"""Data Models for SlideGenius."""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import json


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


@dataclass
class SlideItem:
    """Represents a single slide in the presentation."""
    title: str
    content: List[str] = field(default_factory=list)
    slide_type: SlideType = SlideType.CONTENT
    speaker_notes: str = ""
    image_prompt: Optional[str] = None
    image_path: Optional[str] = None
    diagram: Optional[dict] = None  # Logic diagram data (nodes, links)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "slide_type": self.slide_type.value,
            "speaker_notes": self.speaker_notes,
            "image_prompt": self.image_prompt,
            "image_path": self.image_path,
            "diagram": self.diagram
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SlideItem':
        """Create SlideItem from dictionary."""
        slide_type_str = data.get("slide_type", "content").lower()
        
        # Robust handling for AI hallucinations or diagram types
        try:
            slide_type_enum = SlideType(slide_type_str)
        except ValueError:
            # Map known diagram types to DIAGRAM
            if slide_type_str in ["process", "hierarchy", "cycle", "timeline", "mindmap", "structure"]:
                slide_type_enum = SlideType.DIAGRAM
            else:
                # Log warning in real app? Fallback to CONTENT
                slide_type_enum = SlideType.CONTENT

        return cls(
            title=data.get("title", ""),
            content=data.get("content", []),
            slide_type=slide_type_enum,
            speaker_notes=data.get("speaker_notes", ""),
            image_prompt=data.get("image_prompt"),
            image_path=data.get("image_path"),
            diagram=data.get("diagram")
        )


@dataclass
class Outline:
    """Represents a complete presentation outline."""
    title: str
    slides: List[SlideItem] = field(default_factory=list)
    language: str = "vi"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "language": self.language,
            "slides": [s.to_dict() for s in self.slides]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Outline':
        """Create Outline from dictionary."""
        slides = [SlideItem.from_dict(s) for s in data.get("slides", [])]
        return cls(
            title=data.get("title", "Untitled"),
            slides=slides,
            language=data.get("language", "vi")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Outline':
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
    """Represents a presentation template."""
    name: str
    display_name: str
    description: str
    category: str  # Business, Education, Creative, Minimal
    primary_color: str = "#3B82F6"
    secondary_color: str = "#8B5CF6"
    accent_color: str = "#F97316"
    background_color: str = "#FFFFFF"
    font_heading: str = "Arial"
    font_body: str = "Arial"
    
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
            "font_heading": self.font_heading,
            "font_body": self.font_body
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
            "body_font": self.body_font
        }


# 10 Pre-defined font presets
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
    return FONT_PRESETS[0]  # Default to Modern
