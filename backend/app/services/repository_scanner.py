import subprocess
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
}

EXCLUDED_DIRECTORIES = {
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
}

MAX_FILE_SIZE = 200_000
MAX_FILES = 500


@dataclass(frozen=True)
class SourceFile:
    path: str
    language: str
    content: str
    size_bytes: int


def scan_repository(repo_root: Path) -> list[SourceFile]:
    """Read supported, Git-tracked source files."""

    if repo_root.is_symlink() or not repo_root.is_dir():
        raise ValueError("Invalid repository directory")

    root = repo_root.resolve()

    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "-z",
                "--cached",
            ],
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as exc:
        raise ValueError("Cannot list Git-tracked files") from exc

    tracked_files = result.stdout.decode(
        "utf-8",
        errors="surrogateescape",
    ).split("\0")

    source_files = []

    for relative_path in sorted(filter(None, tracked_files)):
        relative = Path(relative_path)

        if any(
            part.startswith(".") or part in EXCLUDED_DIRECTORIES
            for part in relative.parts
        ):
            continue

        language = SUPPORTED_EXTENSIONS.get(relative.suffix)

        if language is None:
            continue

        file_path = root / relative

        if file_path.is_symlink() or not file_path.is_file():
            continue

        if not file_path.resolve().is_relative_to(root):
            continue

        try:
            size = file_path.stat().st_size

            if size > MAX_FILE_SIZE:
                continue

            content = file_path.read_text(encoding="utf-8")

        except (OSError, UnicodeError):
            continue

        if len(source_files) >= MAX_FILES:
            raise ValueError("Repository file limit exceeded")

        source_files.append(
            SourceFile(
                path=relative.as_posix(),
                language=language,
                content=content,
                size_bytes=size,
            )
        )

    return source_files