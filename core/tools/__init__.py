from .web_search import WebSearchTool
from .file_tool import FileTool
from .app_tool import AppTool
from .screenshot_tool import ScreenshotTool
from .code_tool import CodeTool
from .mouse_tool import MouseTool
from .clipboard_tool import ClipboardTool
from .ocr_tool import OCRTool
from .notification_tool import NotificationTool
from .code_writer_tool import CodeWriterTool
from .volume_tool import VolumeTool
from .notes_tool import NotesTool
from .pdf_reader_tool import PDFReaderTool
from .youtube_tool import YouTubeTool

ALL_TOOLS = [
    WebSearchTool(),
    FileTool(),
    AppTool(),
    ScreenshotTool(),
    CodeTool(),
    MouseTool(),
    ClipboardTool(),
    OCRTool(),
    NotificationTool(),
    CodeWriterTool(),
    VolumeTool(),
    NotesTool(),
    PDFReaderTool(),
    YouTubeTool(),
]