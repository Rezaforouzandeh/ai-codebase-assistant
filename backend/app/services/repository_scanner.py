import os
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".next",
}

MAX_FILE_BYTES = 200_000
MAX_FILES = 500


@dataclass
class SourceFile:
    path: str
    language: str
    content: str


def scan_repository(root: Path) -> list[SourceFile]:
    """Scan a trusted local repository for supported source files."""

    if root.is_symlink() or not root.is_dir():
        raise ValueError("Repository must be an existing directory")

    root = root.resolve()
    results = []

    for current_dir, directories, filenames in os.walk(
        root,
        followlinks=False,
    ):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
            and not directory.startswith(".")
            and not (Path(current_dir) / directory).is_symlink()
        )

        for filename in sorted(filenames):
            if filename.startswith("."):
                continue

            file_path = Path(current_dir) / filename

            if file_path.is_symlink():
                continue

            language = SUPPORTED_EXTENSIONS.get(file_path.suffix)

            if language is None:
                continue

            if file_path.stat().st_size > MAX_FILE_BYTES:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeError, OSError):
                continue

            if len(results) >= MAX_FILES:
                raise ValueError("Repository exceeds the file limit")

            results.append(
                SourceFile(
                    path=file_path.relative_to(root).as_posix(),
                    language=language,
                    content=content,
                )
            )

    return sorted(results, key=lambda file: file.path)