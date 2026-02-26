from PySide6.QtCore import QThread, Signal, QRunnable, QThreadPool, QObject
from src.core.ai_service import AIService
from src.data.models import Outline

class ImageRunnableSignals(QObject):
    """Signals for Parallel Image Generation."""
    finished = Signal(int, str) # index, path

class ImageRunnable(QRunnable):
    """Runnable for parallel image generation."""
    def __init__(self, index, prompt, img_gen, signals):
        super().__init__()
        self.index = index
        self.prompt = prompt
        self.img_gen = img_gen
        self.signals = signals

    def run(self):
        try:
            path = self.img_gen.generate_image(self.prompt)
            if path:
                self.signals.finished.emit(self.index, str(path))
        except Exception as e:
            print(f"Parallel Image Error (Slide {self.index}): {e}")

class GenerateWorker(QThread):
    """Worker thread for AI generation."""
    finished = Signal(object)  # Outline or None
    progress = Signal(str)     # Progress message
    error = Signal(str)
    
    def __init__(self, ai_service: AIService, prompt: str, num_slides: int, context: dict = None):
        super().__init__()
        self.ai_service = ai_service
        self.prompt = prompt
        self.num_slides = num_slides
        self.context = context or {}
    
    def run(self):
        try:
            self.progress.emit("Đang khởi tạo linh hồn bài viết...")
            outline = self.ai_service.generate_outline(self.prompt, self.num_slides, context=self.context)
            
            if not outline:
                self.error.emit("Không thể tạo dàn ý. Vui lòng thử lại.")
                return

            # Parallel Image Generation
            from src.core.image_generator import ImageGenerator
            img_gen = ImageGenerator()
            
            self.progress.emit(f"Đang chuẩn bị vẽ {len(outline.slides)} tranh...")
            
            pool = QThreadPool.globalInstance()
            signals = ImageRunnableSignals()
            
            completed_count = 0
            total_expected = sum(1 for s in outline.slides if s.image_prompt)
            
            def on_image_finished(index, path):
                nonlocal completed_count
                outline.slides[index].image_path = path
                completed_count += 1
                self.progress.emit(f"Đã vẽ xong {completed_count}/{total_expected} tranh...")

            signals.finished.connect(on_image_finished)

            for i, slide in enumerate(outline.slides):
                if slide.image_prompt:
                    runnable = ImageRunnable(i, slide.image_prompt, img_gen, signals)
                    pool.start(runnable)
            
            # Wait for all image tasks to finish
            pool.waitForDone()
            
            self.progress.emit("Hoàn tất!")
            self.finished.emit(outline)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
