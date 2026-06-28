import os
import traceback
from datetime import datetime
from pathlib import Path


def app_data_dir() -> Path:
    return Path(os.environ.get("PYSHOP_DATA_DIR", Path.home() / ".pyshop"))


def recovery_project_path() -> Path:
    return app_data_dir() / "recovery" / "autosave.pyshop"


def clear_recovery_project():
    path = recovery_project_path()
    if path.exists():
        path.unlink()


def write_error_log(context: str, exc: BaseException) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_context = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in context).strip("_") or "error"
    log_dir = app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{timestamp}-{safe_context}.log"
    path.write_text(
        "\n".join(
            [
                f"Context: {context}",
                f"Error: {type(exc).__name__}: {exc}",
                "",
                "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            ]
        ),
        encoding="utf-8",
    )
    return path
