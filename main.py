import argparse
import json
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, List

from course import CourseSerializer
from utils.archive import extract_non_videos, extract_videos, merge_zips
from utils.configs import DOWNLOADS, HOME
from utils.download import download_archive, download_magnet
from utils.general import copy_to_clipboard


def list_configs(courses: Dict[str, Any]) -> None:
    """
    Prints a list of available configurations from the given courses dictionary.

    Args:
        courses (Dict[str, Any]): A dictionary where keys are course names and values are course configurations.

    Returns:
        None
    """
    print("Available configurations:")
    for i, course in enumerate(sorted(courses.keys()), 1):
        print(f"{i:02}. {course}")


def main() -> None:
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
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Disable manual interactions",
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

    course_data = courses[args.config]

    slug, template_id, *others = course_data.values()
    intro, others = data["templates"][template_id]

    hook_module = f"hooks.{args.config}"
    if find_spec(hook_module):
        hook = import_module(hook_module).main
    else:
        hook = merge_zips

    source = (
        hook(*[Path(x) for x in args.input_archive])
        if args.input_archive
        else hook(DOWNLOADS / f"{args.config}.zip")
    )
    if not source.exists():
        magnets = course_data["magnets"]
        files: List[Path] = []
        for magnet in magnets:
            if args.quiet:
                files.append(download_magnet(magnet))
                continue
            copy_to_clipboard(magnet, quiet=True)
            files.append(download_archive(input("Download Link: ")))

        source = hook(*files)

    course = CourseSerializer.get_course(slug)
    target = HOME / "Programming Videos"
    target_list = course.get_videos(target)
    extract_videos(source, target_list, ffmpeg=True, intro=intro, others=others)
    extract_non_videos(source, target / str(course))


if __name__ == "__main__":
    main()
