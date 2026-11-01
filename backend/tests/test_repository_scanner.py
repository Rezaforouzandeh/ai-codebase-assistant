import subprocess

import pytest

from app.services.repository_scanner import scan_repository


def git(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, "init", "-q")
    return tmp_path


def test_scans_tracked_source_files(repository):
    (repository / "main.py").write_text("print('hello')")
    (repository / "App.tsx").write_text(
        "export const App = () => null"
    )

    git(repository, "add", "main.py", "App.tsx")

    files = scan_repository(repository)

    assert len(files) == 2
    assert {f.language for f in files} == {
        "python",
        "typescript",
    }


def test_ignores_untracked_files(repository):
    (repository / "tracked.py").write_text("x = 1")
    (repository / "untracked.py").write_text("secret = 123")

    git(repository, "add", "tracked.py")

    files = scan_repository(repository)

    assert len(files) == 1
    assert files[0].path == "tracked.py"


def test_ignores_dependency_directories(repository):
    directory = repository / "node_modules"
    directory.mkdir()

    (directory / "index.js").write_text("ignored")

    git(repository, "add", "-f", "node_modules/index.js")

    files = scan_repository(repository)

    assert files == []


def test_skips_large_files(repository):
    (repository / "large.py").write_text("x" * 300_000)

    git(repository, "add", "large.py")

    files = scan_repository(repository)

    assert files == []


def test_invalid_repository(tmp_path):
    with pytest.raises(ValueError):
        scan_repository(tmp_path / "missing")