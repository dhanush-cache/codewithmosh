import os
from pathlib import Path
import sys

courses = {
    "cpp": {
        "source": "c++.zip",
        "slug": "ultimate-c-plus-plus-series",
        "intro": 3,
        "others": 2,
    },
    "dsa": {
        "source": "dsa.zip",
        "slug": "data-structures-algorithms",
        "intro": 2,
        "others": 1,
    },
    "git": {
        "source": "git.zip",
        "slug": "the-ultimate-git-course",
        "intro": 3,
        "others": 1,
    },
    "html": {
        "source": "html.zip",
        "slug": "the-ultimate-html-css",
        "intro": 10,
        "others": 2,
    },
    "sql": {
        "source": "sql.zip",
        "slug": "complete-sql-mastery",
        "intro": 2,
        "others": 2,
    },
    "python": {
        "source": "python.zip",
        "slug": "python-programming-course-beginners",
        "intro": 2,
        "others": 2,
    },
    "django": {
        "source": "django.zip",
        "slug": "the-ultimate-django-series",
        "intro": 4,
        "others": 2,
    },
    "react16": {
        "source": "react16.zip",
        "slug": "mastering-react",
        "intro": 2,
        "others": 2,
    },
    "react18": {
        "source": "react18.zip",
        "slug": "ultimate-react-part1",
        "intro": 2,
        "others": 2,
    },
    "javascript": {
        "source": "javascript.zip",
        "slug": "ultimate-javascript-series",
        "intro": 1,
        "others": 1,
    },
    "docker": {
        "source": "docker.zip",
        "slug": "the-ultimate-docker-course",
        "intro": 4,
        "others": 2,
    },
    "nodejs": {
        "source": "nodejs.zip",
        "slug": "the-complete-node-js-course",
        "intro": 1,
        "others": 1,
    },
    "typescript": {
        "source": "typescript.zip",
        "slug": "the-ultimate-typescript",
        "intro": 2,
        "others": 2,
    },
}

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
