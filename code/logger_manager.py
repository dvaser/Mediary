import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import * 

class Logger:
    def __init__(self, log_dir=LOG_FOLDER):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.cleanup_old_logs()

        self.logger = logging.getLogger("ProjectLogger")
        self.logger.setLevel(logging.DEBUG)

        log_file = self.log_dir / f"{datetime.today().strftime('%Y-%m-%d')}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', "%H:%M:%S")
        handler.setFormatter(formatter)

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

    def log(self, text, type="info"):
        emoji_map = {
            "info": "ℹ️",
            "debug": "🐞",
            "warning": "⚠️",
            "error": "❌",
            "header": "🚀",
        }

        prefix = emoji_map.get(type, "")
        if type == "header":
            # Büyük harfle ve çerçeve ile yaz
            header_text = f"==== {prefix} {text.upper()} ===="
            self.logger.info(header_text)
        else:
            full_text = f"{prefix} {text}"
            if type == "info":
                self.logger.info(full_text)
            elif type == "debug":
                self.logger.debug(full_text)
            elif type == "warning":
                self.logger.warning(full_text)
            elif type == "error":
                self.logger.error(full_text)
            else:
                self.logger.info(full_text)

    def cleanup_old_logs(self):
        one_week_ago = datetime.now() - timedelta(days=7)
        for file in self.log_dir.glob("*.log"):
            if datetime.fromtimestamp(file.stat().st_ctime) < one_week_ago:
                file.unlink()


"""
log("Gemini Embedder Başlıyor", type="header")
log("Embed işlemi başladı...", type="info")
log("Embed işlemi tamamlandı.", type="info")

log("Gemini Answer Başlıyor", type="header")
log("Cevap oluşturuluyor...", type="info")
"""