"""
File System Utilities replacing PLP Delete File, Directory Watcher, and String Manipulators
"""
import os
import shutil
from pathlib import Path
from typing import List, Union


def cleanup_directory(target_dir: Union[str, Path]) -> int:
    """
    Safely purges contents of the staging directory.
    Replaces PLP 'Delete File' components (LocalID 56 & 55).
    """
    path = Path(target_dir)
    count = 0
    if not path.exists():
        return 0

    for item in path.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
            count += 1
        elif item.is_dir():
            shutil.rmtree(item)
            count += 1

    return count


def scan_download_directory(target_dir: Union[str, Path]) -> List[Path]:
    """
    Recursively scans directory for files.
    Replaces PLP 'Directory Watcher' component (LocalID 51).
    """
    path = Path(target_dir)
    if not path.exists():
        return []
    return [p for p in path.rglob("*") if p.is_file()]


def clean_section_title(raw_title: str) -> str:
    """
    Strips prefix before colon in SectionName.
    Replaces PLP PilotScript 'Custom Manipulator' (LocalID 28):
    @sectionName := Substring(SectionName, FindSubstring(SectionName, ':') + 2, StringLen(SectionName))
    """
    if not raw_title:
        return ""
    colon_idx = raw_title.find(":")
    if colon_idx != -1 and colon_idx + 2 <= len(raw_title):
        return raw_title[colon_idx + 2:].strip()
    return raw_title.strip()
