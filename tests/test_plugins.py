import json

from pyshop.plugins import discover_plugins, load_plugin_manifest


def test_discover_plugins_returns_empty_result_for_missing_directory(tmp_path):
    result = discover_plugins(tmp_path / "missing")

    assert result.plugins == ()
    assert result.errors == ()


def test_discover_plugins_loads_valid_manifest_with_entrypoint(tmp_path):
    plugin_dir = tmp_path / "plugins" / "sample"
    plugin_dir.mkdir(parents=True)
    entrypoint = plugin_dir / "plugin.py"
    entrypoint.write_text("PLUGIN = True\n", encoding="utf-8")
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "id": "sample.plugin",
                "name": "Sample Plugin",
                "version": "1.0.0",
                "description": "Adds a sample capability.",
                "entrypoint": "plugin.py",
                "capabilities": ["filter", "export"],
            }
        ),
        encoding="utf-8",
    )

    result = discover_plugins(tmp_path / "plugins")

    assert result.errors == ()
    assert len(result.plugins) == 1
    manifest = result.plugins[0]
    assert manifest.plugin_id == "sample.plugin"
    assert manifest.name == "Sample Plugin"
    assert manifest.entrypoint == entrypoint.resolve()
    assert manifest.capabilities == ("filter", "export")


def test_invalid_plugin_manifest_reports_error_without_stopping_discovery(tmp_path):
    good_dir = tmp_path / "plugins" / "good"
    bad_dir = tmp_path / "plugins" / "bad"
    good_dir.mkdir(parents=True)
    bad_dir.mkdir(parents=True)
    (good_dir / "plugin.json").write_text(
        json.dumps({"id": "good", "name": "Good", "version": "1.0.0"}),
        encoding="utf-8",
    )
    (bad_dir / "plugin.json").write_text(
        json.dumps({"id": "bad/plugin", "name": "Bad", "version": "1.0.0"}),
        encoding="utf-8",
    )

    result = discover_plugins(tmp_path / "plugins")

    assert [plugin.plugin_id for plugin in result.plugins] == ["good"]
    assert len(result.errors) == 1
    assert "Plugin id" in result.errors[0].message


def test_plugin_entrypoint_must_stay_inside_plugin_directory(tmp_path):
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    manifest = plugin_dir / "plugin.json"
    manifest.write_text(
        json.dumps({"id": "bad", "name": "Bad", "version": "1.0.0", "entrypoint": "../outside.py"}),
        encoding="utf-8",
    )

    try:
        load_plugin_manifest(manifest)
    except ValueError as exc:
        assert "inside the plugin directory" in str(exc)
    else:
        raise AssertionError("Expected traversal entrypoint to fail validation.")
