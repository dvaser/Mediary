import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from ..config import *  # LOG_FOLDER burada tanımlı olmalı

# Opsiyonel kütüphaneler
try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

try:
    from rich.console import Console
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import coloredlogs
    COLOREDLOGS_AVAILABLE = True
except ImportError:
    COLOREDLOGS_AVAILABLE = False


class Logger:
    def __init__(self, log_dir=LOG_FOLDER, use_loguru=False, use_rich=False, use_coloredlogs=False):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup_old_logs()

        self.use_loguru = use_loguru and LOGURU_AVAILABLE
        self.use_rich = use_rich and RICH_AVAILABLE
        self.use_coloredlogs = use_coloredlogs and COLOREDLOGS_AVAILABLE

        self.logger = logging.getLogger("ProjectLogger")
        self.logger.setLevel(logging.DEBUG)
        log_file = self.log_dir / f"{datetime.today().strftime('%Y-%m-%d')}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', "%H:%M:%S")
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        if self.use_coloredlogs:
            coloredlogs.install(
                level='DEBUG',
                logger=self.logger,
                fmt='%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%H:%M:%S'
            )

        if self.use_loguru:
            loguru_logger.remove()
            loguru_logger.add(
                log_file,
                rotation="10 MB",
                encoding="utf-8",
                backtrace=False,
                diagnose=False,
                format="{time:HH:mm:ss} | {level} | {message}"
            )
            loguru_logger.add(
                lambda msg: print(msg, end=""),
                backtrace=False,
                diagnose=False,
                format="{time:HH:mm:ss} | {level} | {message}"
            )

    def log(self, text: str, type: str = "info"):
        emoji_map = {
            "info": "ℹ️ ",
            "debug": "🐞",
            "warning": "⚠️",
            "error": "❌",
            "header": "🚀",
            "note": "📝",
            "test": "🧪",
            "success": "✅",
            "critical": "🔥",
            "performance": "⏱️",
            "rate_limit": "📉",
            "banner": "🚀",
            "func": "📁"
        }

        prefix = emoji_map.get(type, "")
        msg = f"{prefix} {text}"

        if self.use_loguru:
            level_map = {
                "info": "INFO",
                "debug": "DEBUG",
                "warning": "WARNING",
                "error": "ERROR",
                "header": "INFO",
                "note": "INFO",
                "test": "DEBUG",
                "success": "SUCCESS",
                "critical": "CRITICAL",
                "performance": "DEBUG",
                "rate_limit": "WARNING",
                "banner": "INFO",
                "func": "DEBUG"
            }

            level = level_map.get(type, "INFO")

            if type == "header":
                line = "─" * 50
                loguru_logger.log(level, f"\n{line}\n{prefix} {text.capitalize()}\n{line}")

            elif type == "note":
                loguru_logger.log(level, f"{prefix} NOTE: {text}")

            elif type == "banner":
                line = "=" * 50
                loguru_logger.log(level, f"\n\n\n{line}\n==== {prefix} {text.upper()} ====\n{line}\n\n")

            elif type == "func":
                line = "─" * 50
                loguru_logger.log(level, f"\n{line}\n{prefix} {text} fonksiyonu çalıştı\n{line}")

            else:
                loguru_logger.log(level, msg)
            return

        if self.use_rich:
            if type == "header":
                line = "─" * 50
                console.log(f"\n[bold cyan]{line}\n{prefix} {text.capitalize()}\n{line}[/bold cyan]")

            elif type == "note":
                console.log(f"[bold yellow]{prefix} NOTE: {text}[/bold yellow]")

            elif type == "banner":
                line = "=" * 50
                console.log(f"\n\n\n[bold cyan]{line}\n==== {prefix} {text.upper()} ====\n{line}[/bold cyan]\n\n")

            elif type == "func":
                line = "─" * 50
                console.log(f"\n[bold cyan]{line}\n{prefix} {text} fonksiyonu çalıştı\n{line}[/bold cyan]")

            elif type in ("error", "critical"):
                console.log(f"[bold red]{msg}[/bold red]")

            elif type == "warning":
                console.log(f"[bold yellow]{msg}[/bold yellow]")

            elif type == "success":
                console.log(f"[bold green]{msg}[/bold green]")

            else:
                console.log(msg)
            return

        if type == "header":
            line = "─" * 50
            self.logger.info(f"\n{line}\n{prefix} {text.capitalize()}\n{line}")

        elif type == "note":
            self.logger.info(f"{prefix} NOTE: {text}")

        elif type == "banner":
            line = "=" * 50
            self.logger.info(f"\n\n\n{line}\n==== {prefix} {text.upper()} ====\n{line}\n\n")

        elif type == "func":
            line = "─" * 50
            self.logger.info(f"\n{line}\n{prefix} {text} fonksiyonu çalıştı\n{line}")

        elif type == "test":
            self.logger.debug(msg)

        elif type == "success":
            self.logger.info(msg)

        elif type == "critical":
            self.logger.critical(msg)

        elif type == "performance":
            self.logger.debug(msg)

        elif type == "rate_limit":
            self.logger.warning(msg)

        elif type == "debug":
            self.logger.debug(msg)

        elif type == "warning":
            self.logger.warning(msg)

        elif type == "error":
            self.logger.error(msg)

        else:
            self.logger.info(msg)

    def cleanup_old_logs(self):
        one_week_ago = datetime.now() - timedelta(days=7)
        for file in self.log_dir.glob("*.log"):
            if datetime.fromtimestamp(file.stat().st_ctime) < one_week_ago:
                file.unlink()


# --- Global hazır logger instance ve fonksiyon ---

logger = Logger(use_loguru=True, use_rich=True, use_coloredlogs=True)

def log(text: str, type: str = "info"):
    """
    Kolay kullanım için global log fonksiyonu.
    Örnek: log("Başladı", type="header")
           log("Ana embed fonksiyonu", type="func")
           log("Ana embed class", type="header")
           log("Proje Başladı", type="banner")
    """
    logger.log(text, type)
