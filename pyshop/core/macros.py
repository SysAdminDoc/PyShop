import json
from pathlib import Path


MACRO_FILE_SUFFIX = ".pyshopmacro"
ALLOWED_MACRO_COMMANDS = frozenset(
    {
        "set_tool",
        "set_show_grid",
        "set_show_guides",
        "set_show_rulers",
        "set_snap_enabled",
    }
)


class MacroFormatError(RuntimeError):
    pass


def macro_steps_to_records(steps) -> list:
    records = []
    for command, args in steps or []:
        if command not in ALLOWED_MACRO_COMMANDS:
            raise MacroFormatError(f"Unsupported macro command: {command}")
        records.append({"command": str(command), "args": list(args)})
    return records


def macro_steps_from_records(records, allowed_commands=ALLOWED_MACRO_COMMANDS) -> list:
    if not isinstance(records, list):
        raise MacroFormatError("Macro file must contain a list of steps.")
    steps = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise MacroFormatError(f"Macro step {index + 1} must be an object.")
        command = record.get("command")
        args = record.get("args", [])
        if command not in allowed_commands:
            raise MacroFormatError(f"Unsupported macro command: {command}")
        if not isinstance(args, list):
            raise MacroFormatError(f"Macro step {index + 1} args must be a list.")
        steps.append((command, tuple(args)))
    return steps


def save_macro_file(path, steps):
    path = Path(path)
    if path.suffix.lower() != MACRO_FILE_SUFFIX:
        path = path.with_suffix(MACRO_FILE_SUFFIX)
    path.write_text(json.dumps(macro_steps_to_records(steps), indent=2), encoding="utf-8")
    return path


def load_macro_file(path):
    try:
        records = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise MacroFormatError(f"Failed to read macro file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MacroFormatError(f"Invalid macro JSON: {exc}") from exc
    return macro_steps_from_records(records)
