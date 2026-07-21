#!/usr/bin/env python3
"""
images/ 폴더를 훑어서 gallery.json 을 자동으로 만듭니다.
- images/<캐릭터이름>/ 아래의 이미지 파일들을 모읍니다.
- 캐릭터(폴더) 순서는 이름 가나다순입니다.
- 각 이미지에 Git 커밋 시각(ts, 유닉스초)을 붙입니다. 커밋 기록이 없으면 0.
- 직접 실행할 필요 없음: 깃허브에 올리면 자동으로 돌아갑니다.
"""

import json
import os
import subprocess
from datetime import datetime, timezone

IMAGES_DIR = "images"
OUTPUT = "gallery.json"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}


def git_commit_ts(path):
    """해당 파일이 마지막으로 커밋된 시각(유닉스초)을 반환. 기록이 없으면 0."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", path],
            capture_output=True,
            text=True,
            check=False,
        )
        out = result.stdout.strip()
        return int(out) if out else 0
    except Exception:
        return 0


def main():
    characters = []

    if os.path.isdir(IMAGES_DIR):
        for folder in sorted(os.listdir(IMAGES_DIR), key=lambda s: s.lower()):
            path = os.path.join(IMAGES_DIR, folder)
            if not os.path.isdir(path):
                continue
            if folder.startswith("."):
                continue

            files = [
                f for f in sorted(os.listdir(path), key=lambda s: s.lower())
                if os.path.splitext(f)[1].lower() in EXTS
            ]
            if not files:
                continue

            images = []
            for f in files:
                rel = os.path.join(IMAGES_DIR, folder, f)
                images.append({
                    "file": f,
                    "ts": git_commit_ts(rel),
                })

            characters.append({
                "name": folder,
                "folder": folder,
                "images": images,
            })

    data = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "characters": characters,
    }

    with open(OUTPUT, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

    total = sum(len(c["images"]) for c in characters)
    print(f"gallery.json 생성 완료 · 캐릭터 {len(characters)}명 · 이미지 {total}장")


if __name__ == "__main__":
    main()
