import json
import re
from dataclasses import dataclass, field
from pathlib import Path


PLUGIN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    description: str = ""
    entrypoint: Path | None = None
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True
    directory: Path | None = None


@dataclass(frozen=True)
class PluginDiscoveryError:
    path: Path
    message: str


@dataclass(frozen=True)
class PluginDiscoveryResult:
    plugins: tuple[PluginManifest, ...]
    errors: tuple[PluginDiscoveryError, ...]


def default_plugins_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "plugins"


def discover_plugins(root=None) -> PluginDiscoveryResult:
    root = Path(root) if root is not None else default_plugins_dir()
    if not root.exists():
        return PluginDiscoveryResult((), ())
    plugins = []
    errors = []
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        manifest_path = directory / "plugin.json"
        if not manifest_path.exists():
            continue
        try:
            plugins.append(load_plugin_manifest(manifest_path))
        except ValueError as exc:
            errors.append(PluginDiscoveryError(manifest_path, str(exc)))
        except OSError as exc:
            errors.append(PluginDiscoveryError(manifest_path, f"Failed to read plugin manifest: {exc}"))
    return PluginDiscoveryResult(tuple(plugins), tuple(errors))


def load_plugin_manifest(manifest_path) -> PluginManifest:
    manifest_path = Path(manifest_path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid plugin manifest JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("Plugin manifest must be a JSON object.")

    plugin_id = _required_text(data, "id")
    if not PLUGIN_ID_PATTERN.fullmatch(plugin_id):
        raise ValueError("Plugin id may only contain letters, numbers, dots, underscores, and hyphens.")
    name = _required_text(data, "name")
    version = _required_text(data, "version")
    description = _optional_text(data, "description")
    capabilities = _capabilities(data.get("capabilities", []))
    entrypoint = _entrypoint(manifest_path.parent, data.get("entrypoint"))
    enabled = bool(data.get("enabled", True))
    return PluginManifest(
        plugin_id=plugin_id,
        name=name,
        version=version,
        description=description,
        entrypoint=entrypoint,
        capabilities=capabilities,
        enabled=enabled,
        directory=manifest_path.parent,
    )


def _required_text(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Plugin manifest requires a non-empty '{key}' value.")
    return value.strip()


def _optional_text(data: dict, key: str) -> str:
    value = data.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Plugin manifest '{key}' value must be a string.")
    return value.strip()


def _capabilities(value) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError("Plugin manifest 'capabilities' value must be a list.")
    capabilities = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("Plugin capabilities must be non-empty strings.")
        capabilities.append(item.strip())
    return tuple(capabilities)


def _entrypoint(directory: Path, value) -> Path | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("Plugin manifest 'entrypoint' value must be a relative path string.")
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError("Plugin entrypoint must be relative to the plugin directory.")
    resolved_directory = directory.resolve()
    resolved_entrypoint = (directory / relative).resolve()
    if resolved_entrypoint != resolved_directory and resolved_directory not in resolved_entrypoint.parents:
        raise ValueError("Plugin entrypoint must stay inside the plugin directory.")
    if not resolved_entrypoint.exists():
        raise ValueError("Plugin entrypoint file does not exist.")
    return resolved_entrypoint
