import json
import os
from pathlib import Path
import argparse

from course import CourseSerializer
from utils import extract_non_videos, extract_videos


def list_configs(courses):
    print("Available configurations:")
    for i, course in enumerate(sorted(courses.keys()), 1):
        print(f"{i:02}. {course}")


def main():
    config_file = Path("configs.json")
    courses = json.loads(config_file.read_text())

    parser = argparse.ArgumentParser(
        prog="Code With Mosh",
        description="Organizes courses from codewithmosh.com",
        epilog="Checkout https://codewithmosh.com",
    )

    parser.add_argument("config", type=str, nargs="?", help="The configuration to use")
    parser.add_argument(
        "-l",
        "--list-configs",
        action="store_true",
        help="List all available configurations",
    )
    parser.add_argument(
        "-i",
        "--input-archive",
        help="Path to the input file",
    )

    args = parser.parse_args()

    if args.list_configs:
        list_configs(courses)
        parser.exit()

    if not args.config:
        parser.error("The following arguments are required: config")

    HOME = Path("/sdcard") if "ANDROID_STORAGE" in os.environ else Path.home()
    downloads = next(HOME.glob("Download*"))

    data = courses[args.config]

    slug = data["slug"]
    source = (
        Path(args.input_archive)
        if args.input_archive
        else (downloads / f"{args.config}.zip")
    )
    course = CourseSerializer.get_course(slug)
    target = HOME / "Programming Videos"
    intro = data["intro"]
    others = data["others"]
    target_list = course.get_videos(target)
    extract_videos(source, target_list, ffmpeg=True, intro=intro, others=others)
    extract_non_videos(source, target / str(course))


if __name__ == "__main__":
    main()
