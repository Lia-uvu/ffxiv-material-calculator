from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.request import urlopen


def read_text_from_dir(input_dir: Path, filename: str) -> str:
    file_path = input_dir / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required CSV: {file_path}")
    return file_path.read_text(encoding="utf-8-sig")


def read_text_from_dir_or_remote(
    input_dir: Path | None, filename: str, base_url: str | None = None
) -> str:
    if input_dir is not None:
        return read_text_from_dir(input_dir, filename)
    if not base_url:
        raise FileNotFoundError(f"Missing required CSV: {filename}")
    url = f"{base_url.rstrip('/')}/{filename}"
    with urlopen(url) as response:
        return response.read().decode("utf-8-sig")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_files_exist(input_dir: Path, filenames: Iterable[str]) -> None:
    missing = [str(input_dir / name) for name in filenames if not (input_dir / name).exists()]
    if missing:
        raise FileNotFoundError("Missing required files:\n" + "\n".join(missing))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def try_git_rev_parse(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    sha = result.stdout.strip()
    return sha or None
