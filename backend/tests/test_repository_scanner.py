import pytest

from app.services.repository_scanner import scan_repository


def test_scans_supported_files(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "Chat.tsx").write_text("export const Chat = () => null")

    files = scan_repository(tmp_path)

    assert len(files) == 2
    assert files[0].path == "Chat.tsx"
    assert files[1].language == "python"


def test_ignores_dependencies(tmp_path):
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()

    (node_modules / "index.js").write_text("ignored")
    (tmp_path / "app.py").write_text("print('included')")

    files = scan_repository(tmp_path)

    assert len(files) == 1
    assert files[0].path == "app.py"


def test_skips_oversized_files(tmp_path):
    (tmp_path / "large.py").write_text("x" * 300_000)

    files = scan_repository(tmp_path)

    assert files == []


def test_rejects_invalid_directory(tmp_path):
    with pytest.raises(ValueError):
        scan_repository(tmp_path / "missing")


def test_preserves_relative_paths(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    (src / "utils.ts").write_text("export const x = 1")

    files = scan_repository(tmp_path)

    assert files[0].path == "src/utils.ts"