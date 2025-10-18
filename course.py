import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator

import requests
from bs4 import BeautifulSoup

from utils.general import clean_path


class CourseSerializer(ABC):
    """
    CourseSerializer is an abstract base class for serializing course data from the Code with Mosh website.

    Attributes:
        keywords (List[str]): A list of keywords to be removed from course names.

    Args:
        slug (str): The slug identifier for the course.

    Methods:
        get_course(slug: str) -> "Course | CourseBundle":
            Retrieves a Course or CourseBundle object based on the slug.

        get_videos(root: Path, bundle: "CourseBundle | None" = None) -> Iterator[Path]:
            Abstract method to be implemented by subclasses to get video paths.

        get_token() -> str:
            Retrieves a token required for accessing course data.

        get_data() -> Dict[Any, Any]:
            Fetches course data from the Code with Mosh website.

        get_json(url: str) -> Dict[Any, Any]:
            Fetches and parses JSON data from the given URL.

        __str__() -> str:
            Returns the course name with specified keywords removed.
    """

    keywords = [
        "Mastering",
        "Mastery",
        "The Ultimate",
        "Ultimate",
        "The Complete",
        "Complete",
        "Series",
        "Bundle",
        "Crash Course",
        "Course",
        "for Beginners",
    ]

    def __init__(self, slug: str) -> None:
        self.slug = slug
        self._data = self.get_data()
        self.name: str = self._data["course"]["name"]
        self.is_bundle: bool = self._data["course"]["type"] == "bundle"

    @staticmethod
    def get_course(slug: str) -> "Course | CourseBundle":
        """
        Retrieve a course or course bundle based on the provided slug.

        Args:
            slug (str): The unique identifier for the course or course bundle.

        Returns:
            Course | CourseBundle: An instance of Course if the slug corresponds to a single course,
                                   or an instance of CourseBundle if the slug corresponds to a course bundle.
        """
        course = Course(slug)
        return course if not course.is_bundle else CourseBundle(slug)

    @abstractmethod
    def get_videos(
        self, root: Path, bundle: "CourseBundle | None" = None
    ) -> Iterator[Path]:
        pass

    @staticmethod
    def get_token() -> str:
        """
        Fetches a token from the specified URL.

        This function sends a GET request to the URL "https://codewithmosh.com/",
        parses the HTML content to find a specific tag with the id "__NEXT_DATA__",
        and extracts the "buildId" from the JSON content of that tag.

        Returns:
            str: The extracted token (buildId).

        Raises:
            ValueError: If the token cannot be found in the HTML content.
        """
        url = "https://codewithmosh.com/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.select_one("#__NEXT_DATA__")
        if tag and tag.string:
            return json.loads(tag.string)["buildId"]
        raise ValueError("Cannot find the token")

    def get_data(self) -> Dict[Any, Any]:
        """
        Fetches data from a dynamically constructed URL based on the token and slug.

        Returns:
            Dict[Any, Any]: The JSON response from the constructed URL.
        """
        url = (
            f"https://codewithmosh.com/_next/data/{self.get_token()}/p/{self.slug}.json"
        )
        return self.get_json(url)

    @staticmethod
    def get_json(url: str) -> Dict[Any, Any]:
        """
        Fetches JSON data from the given URL and returns the 'pageProps' content.

        Args:
            url (str): The URL to fetch the JSON data from.

        Returns:
            Dict[Any, Any]: The 'pageProps' content from the JSON response.

        Raises:
            requests.exceptions.RequestException: If there is an issue with the HTTP request.
            json.JSONDecodeError: If the response content is not valid JSON.
            KeyError: If 'pageProps' is not found in the JSON response.
        """
        response = requests.get(url)
        return json.loads(response.content)["pageProps"]

    def __str__(self) -> str:
        name = f"{self.name}"
        for keyword in self.keywords:
            name = name.replace(keyword, "")
        return name.strip()


class Lesson:
    def __init__(self, lesson_index: int, context: Dict[Any, Any]) -> None:
        self.index = lesson_index
        self.__data = context
        self.name = self.__data.get("name")
        self.is_video: bool = self.__data["type"] == 1
        self.duration = self.__get_duration()
        self.url = f"https://codewithmosh.teachable.com/{self.__data.get("href")}"

    def __get_duration(self) -> int | None:
        if not self.is_video:
            return None
        time = self.__data["duration"]
        minutes, seconds = [int(unit.strip("ms")) for unit in time.split()]
        return (minutes * 60) + seconds

    def __str__(self) -> str:
        return f"{self.index:02}- {self.name}"

    def get_path(
        self,
        section: "Section",
        course: "Course",
        bundle: "CourseBundle | None",
        root: Path,
    ) -> Path:
        """
        Generate the file path for a given section, course, and optional course bundle.

        Args:
            section (Section): The section for which the path is being generated.
            course (Course): The course for which the path is being generated.
            bundle (CourseBundle | None): The optional course bundle that the course belongs to.
            root (Path): The root directory path.

        Returns:
            Path: The generated file path for the given section, course, and optional course bundle.
        """
        base = (
            f"{root}/{bundle}/{str(course).lstrip(bundle.get_common_part())}"
            if bundle
            else f"{root}/{course}"
        )

        return clean_path(Path(f"{base}/{section}/{self}.mkv"))


class Section:
    def __init__(self, section_index: int, data: Dict[Any, Any]):
        self.index = section_index
        self.__data = data
        self.name = self.__data.get("name")

    def get_lessons(self) -> Iterator[Lesson]:
        """
        Retrieves an iterator of Lesson objects from the course data.

        Returns:
            Iterator[Lesson]: An iterator of Lesson objects, each representing a lesson in the course.
        """
        return (
            Lesson(index, lesson_data)
            for index, lesson_data in enumerate(self.__data.get("lessons", []), start=1)
        )

    def __str__(self):
        return f"{self.index:02}- {self.name}"

    def __iter__(self):
        return iter(self.get_lessons())


class Course(CourseSerializer):
    def get_sections(self) -> Iterator[Section]:
        """
        Retrieve the sections of the course.

        This method generates an iterator of Section objects, each representing a section
        of the course curriculum. The sections are indexed starting from 1.

        Returns:
            Iterator[Section]: An iterator of Section objects.
        """
        return (
            Section(index, section_data)
            for index, section_data in enumerate(
                self._data["course"]["curriculum"], start=1
            )
        )

    def get_videos(
        self, root: Path, bundle: "CourseBundle | None" = None
    ) -> Iterator[Path]:
        """
        Retrieve video file paths from the course sections and lessons.

        Args:
            root (Path): The root directory path where the course files are located.
            bundle (CourseBundle | None, optional): An optional course bundle to filter the videos. Defaults to None.

        Returns:
            Iterator[Path]: An iterator of Paths to the video files.
        """
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

    def get_courses(self) -> Iterator[Course]:
        """
        Fetches and returns an iterator of Course objects.

        This method constructs a URL using a token and retrieves a JSON response
        containing course data. It then filters and returns an iterator of Course
        objects for courses that are part of the bundle contents.

        Returns:
            Iterator[Course]: An iterator of Course objects.
        """
        url = f"https://codewithmosh.com/_next/data/{self.get_token()}/courses.json"
        courses = self.get_json(url)
        return (
            Course(course["slug"])
            for course in courses["courses"]
            if course["id"] in self._data["course"]["bundleContents"]
        )

    def get_common_part(self) -> str:
        """
        Extracts the common prefix from the names of the courses in the course list.

        Returns:
            str: The common prefix of the course names. If the common prefix ends with "Part",
                 it will be stripped from the result.
        """
        course_names = [course.name for course in self.courses]
        prefix = os.path.commonprefix(course_names).strip()
        if prefix.endswith("Part"):
            prefix = prefix.rstrip("Part")
        return prefix

    def get_videos(
        self, root: Path, bundle: "CourseBundle | None" = None
    ) -> Iterator[Path]:
        """
        Retrieve all video files from the courses.

        Args:
            root (Path): The root directory where the videos are stored.
            bundle (CourseBundle | None, optional): The course bundle to which the videos belong. Defaults to None.

        Yields:
            Iterator[Path]: An iterator over the paths of the video files.
        """
        for course in self.courses:
            yield from course.get_videos(root, self)
