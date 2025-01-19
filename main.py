import json
import os
from pathlib import Path
import sys

from course import CourseSerializer
from utils import extract_non_videos, extract_videos


def main():
    config_file = Path("configs.json")
    courses = json.loads(config_file.read_text())

    home = Path("/sdcard") if "ANDROID_STORAGE" in os.environ else Path.home()

    if len(sys.argv) != 2:
        print("Usage: python configs.py <config>")
        print("Available configs:")
        for course in sorted(courses.keys()):
            print(f"- {course}")
        sys.exit(1)

    data = courses[sys.argv[1]]
    source_dir = next(home.glob("Download*"))
    data["source"] = source_dir / data["source"]
    data["target"] = home / "Programming Videos"

    slug = data["slug"]
    source = data["source"]
    course = CourseSerializer.get_course(slug)
    target = data["target"]
    intro = data["intro"]
    others = data["others"]
    target_list = course.get_videos(target)
    extract_videos(source, target_list, ffmpeg=True, intro=intro, others=others)
    extract_non_videos(source, target / str(course))


if __name__ == "__main__":
    main()
