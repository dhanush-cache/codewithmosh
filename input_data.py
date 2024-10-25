from pathlib import Path

cpp = {
    "source": "c++.zip",
    "slug": "ultimate-c-plus-plus-series",
    "intro": 3,
    "others": 2,
}

dsa = {
    "source": "dsa.zip",
    "slug": "data-structures-algorithms",
    "intro": 2,
    "others": 1,
}

git = {
    "source": "git.zip",
    "slug": "the-ultimate-git-course",
    "intro": 3,
    "others": 1,
}

html = {
    "source": "html.zip",
    "slug": "the-ultimate-html-css",
    "intro": 10,
    "others": 2,
}

sql = {
    "source": "sql.zip",
    "slug": "complete-sql-mastery",
    "intro": 2,
    "others": 2,
}

django = {
    "source": "django.zip",
    "slug": "the-ultimate-django-series",
    "intro": 4,
    "others": 2,
}

react16 = {
    "source": "react16.zip",
    "slug": "mastering-react",
    "intro": 2,
    "others": 2,
}

react18 = {
    "source": "react18.zip",
    "slug": "ultimate-react-part1",
    "intro": 2,
    "others": 2,
}


data = {}  # Replace with a pre-defined config. eg data = sql
source_dir = ""  # Directory to scan for the zip files. Note that zip file should be named same as mentioned in its config.
data["source"] = source_dir + data["source"]
data["target"] = Path.home() / "Programming Videos"
