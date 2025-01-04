from pathlib import Path

from course import CourseSerializer
from configs import data
from utils import extract_non_videos, extract_videos


def main():
    slug = data["slug"]
    source = data["source"]
    course = CourseSerializer.get_course(slug)
    target = data["target"]
    target_list = course.get_videos(target)
    extract_videos(source, target_list, ffmpeg=True)
    extract_non_videos(source, target / str(course))


if __name__ == "__main__":
    main()
