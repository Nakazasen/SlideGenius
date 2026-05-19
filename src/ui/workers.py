from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, Signal

from src.core.ai_service import AIService
from src.data.config_manager import ConfigManager


class ImageRunnableSignals(QObject):
    """Signals for parallel image generation."""

    finished = Signal(int, str)


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
        except Exception as exc:
            print(f"Parallel Image Error (Slide {self.index}): {exc}")


class GenerateWorker(QThread):
    """Worker thread for AI generation."""

    finished = Signal(object)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, ai_service: AIService, prompt: str, num_slides: int, context: dict = None):
        super().__init__()
        self.ai_service = ai_service
        self.prompt = prompt
        self.num_slides = num_slides
        self.context = context or {}
        self.context.setdefault("interactive_ui", True)
        self.context.setdefault("stable_mode", ConfigManager().get("generation.stable_mode", True))

    def run(self):
        try:
            self.progress.emit("Đang khởi tạo cấu trúc bài viết...")
            outline = self.ai_service.generate_outline(
                self.prompt,
                self.num_slides,
                context=self.context,
                progress_callback=self.progress.emit,
            )

            if not outline:
                self.error.emit("Không thể tạo dàn ý. Vui lòng thử lại.")
                return

            if outline.quality_retry_count:
                self.progress.emit(f"Đã chạy thêm {outline.quality_retry_count} vòng cải thiện chất lượng deck...")

            config = ConfigManager()
            should_generate_images = bool(config.get("generation.auto_generate_images", False)) and not self.context.get("stable_mode")
            if should_generate_images:
                from src.core.image_generator import ImageGenerator

                img_gen = ImageGenerator()
                self.progress.emit(f"Đang chuẩn bị vẽ {len(outline.slides)} ảnh...")

                pool = QThreadPool.globalInstance()
                signals = ImageRunnableSignals()

                completed_count = 0
                total_expected = sum(1 for slide in outline.slides if slide.image_prompt)

                def on_image_finished(index, path):
                    nonlocal completed_count
                    outline.slides[index].image_path = path
                    completed_count += 1
                    self.progress.emit(f"Đã vẽ xong {completed_count}/{total_expected} ảnh...")

                signals.finished.connect(on_image_finished)

                for index, slide in enumerate(outline.slides):
                    if slide.image_prompt:
                        runnable = ImageRunnable(index, slide.image_prompt, img_gen, signals)
                        pool.start(runnable)

                pool.waitForDone()
            else:
                self.progress.emit("Bỏ qua bước tạo ảnh để ưu tiên chế độ ổn định.")
            self.progress.emit("Hoàn tất!")
            self.finished.emit(outline)
        except Exception as exc:
            import traceback

            traceback.print_exc()
            self.error.emit(str(exc))
