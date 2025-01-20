import argparse
import json
import os
from pathlib import Path

from pyperclip import copy

import hooks
from course import CourseSerializer
from utils import extract_non_videos, extract_videos

HOME = Path("/sdcard") if "ANDROID_STORAGE" in os.environ else Path.home()


def list_configs(courses):
    print("Available configurations:")
    for i, course in enumerate(sorted(courses.keys()), 1):
        print(f"{i:02}. {course}")


def main():
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
        "-i", "--input-archive", nargs="+", help="Path to the input file"
    )
    args = parser.parse_args()

    config_file = Path("data.json")
    data = json.loads(config_file.read_text())
    courses = data["configs"]

    if args.list_configs:
        list_configs(courses)
        parser.exit()

    if not args.config:
        parser.error("The following arguments are required: config")

    downloads = next(HOME.glob("Download*"))

    course_data = courses[args.config]

    slug, template_id, *others = course_data.values()
    intro, others = data["templates"][template_id]
    if args.config in dir(hooks):
        hook = getattr(hooks, args.config)
    elif args.input_archive and len(args.input_archive) == 1:
        hook = lambda *x: x[0]
    else:
        hook = hooks.merge_zips

    source = (
        hook(*args.input_archive)
        if args.input_archive
        else (downloads / f"{args.config}.zip")
    )
    if not source.exists():
        magnets = course_data["magnets"]
        if len(magnets) == 1:
            hook = lambda *x: x[0]
        files = []
        for magnet in magnets:
            copy(magnet)
            print("Magnet copied to your clipboard! Paste the download link.")
            files.append(hooks.download_archive(input("Download Link: ")))

        source = hook(*files)

    course = CourseSerializer.get_course(slug)
    target = HOME / "Programming Videos"
    target_list = course.get_videos(target)
    extract_videos(source, target_list, ffmpeg=True, intro=intro, others=others)
    extract_non_videos(source, target / str(course))


if __name__ == "__main__":
    main()
