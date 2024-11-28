import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class CourseSerializer(ABC):
    keywords = [
        "Mastering",
        "Mastery",
        "The Ultimate",
        "Ultimate",
        "Complete",
        "Series",
        "Bundle",
        "Crash Course",
        "Course",
        "for Beginners",
    ]

    def __init__(self, slug: str):
        self.slug = slug
        self._data = self.get_data()
        self.name = self._data["course"]["name"]
        self.is_bundle = self._data["course"]["type"] == "bundle"

    @staticmethod
    def get_course(slug):
        course = Course(slug)
        return course if not course.is_bundle else CourseBundle(slug)

    @abstractmethod
    def get_videos(self, root):
        pass

    @staticmethod
    def get_token():
        url = "https://codewithmosh.com/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.select_one("#__NEXT_DATA__")
        if tag and tag.string:
            return json.loads(tag.string)["buildId"]
        raise ValueError("Cannot find the token")

    def get_data(self):
        url = (
            f"https://codewithmosh.com/_next/data/{self.get_token()}/p/{self.slug}.json"
        )
        return self.get_json(url)

    @staticmethod
    def get_json(url):
        response = requests.get(url)
        return json.loads(response.content)["pageProps"]

    def __str__(self):
        name = f"{self.name}"
        for keyword in self.keywords:
            name = name.replace(keyword, "")
        return name.strip()


class Lesson:
    def __init__(self, lesson_index: int, context: dict):
        self.index = lesson_index
        self.__data = context
        self.name = self.__data.get("name")
        self.is_video = self.__data["type"] == 1
        self.duration = self.__get_duration()
        self.url = f"https://codewithmosh.teachable.com/{self.__data.get("href")}"

    def __get_duration(self):
        if not self.is_video:
            return None
        time = self.__data["duration"]
        minutes, seconds = [int(unit.strip("ms")) for unit in time.split()]
        return (minutes * 60) + seconds

    def __str__(self):
        return f"{self.index:02}- {self.name}"

    def get_path(self, section, course, bundle, root):
        base = (
            f"{root}/{bundle}/{str(course).lstrip(bundle.get_common_part())}"
            if bundle
            else f"{root}/{course}"
        )

        return Path(f"{base}/{section}/{self}.mkv".replace(":", "-"))


class Section:
    def __init__(self, section_index, data):
        self.index = section_index
        self.__data = data
        self.name = self.__data.get("name")

    def get_lessons(self):
        return (
            Lesson(index, lesson_data)
            for index, lesson_data in enumerate(self.__data.get("lessons"), start=1)
        )

    def __str__(self):
        return f"{self.index:02}- {self.name}"

    def __iter__(self):
        return iter(self.get_lessons())


class Course(CourseSerializer):
    def get_sections(self):
        return (
            Section(index, section_data)
            for index, section_data in enumerate(self._data["course"]["curriculum"], start=1)
        )

    def get_videos(self, root, bundle=None):
        return (
            lesson.get_path(section, self, bundle, root)
            for section in self.get_sections()
            for lesson in section.get_lessons()
            if lesson.is_video
        )

    def __iter__(self):
        return iter(self.get_sections())


class CourseBundle(CourseSerializer):
    def __init__(self, slug: str):
        super().__init__(slug)
        self.courses = list(self.get_courses())

    def get_courses(self):
        url = f"https://codewithmosh.com/_next/data/{self.get_token()}/courses.json"
        courses = self.get_json(url)
        return (
            Course(course["slug"])
            for course in courses["courses"]
            if course["id"] in self._data["course"]["bundleContents"]
        )

    def get_common_part(self) -> str:
        course_names = [course.name for course in self.courses]
        prefix = os.path.commonprefix(course_names).strip()
        if prefix.endswith("Part"):
            prefix = prefix.rstrip("Part")
        return prefix

    def get_videos(self, root):
        for course in self.courses:
            yield from course.get_videos(root, self)
