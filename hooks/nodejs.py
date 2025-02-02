from pathlib import Path

from utils.archive import merge_zips

mappings = {
    "1. Getting Started/Welcome.mp4": 1,
    "1. Getting Started/What is Node.mp4": 2,
    "1. Getting Started/Node Architecture.mp4": 3,
    "1. Getting Started/How Node Works.mp4": 4,
    "1. Getting Started/Installing Node.mp4": 5,
    "1. Getting Started/Your First Node Program.mp4": 6,
    "1. Getting Started/Course Structure.mp4": 7,
    "1. Getting Started/Getting Started Recap.pdf": 8,
    "2. Node Module System/Introduction.mp4": 1,
    "2. Node Module System/Global Object.mp4": 2,
    "2. Node Module System/Modules.mp4": 3,
    "2. Node Module System/Creating a Module.mp4": 4,
    "2. Node Module System/Loading a Module.mp4": 5,
    "2. Node Module System/Module Wrapper Function.mp4": 6,
    "2. Node Module System/Path Module.mp4": 7,
    "2. Node Module System/OS Module.mp4": 8,
    "2. Node Module System/File System Module.mp4": 9,
    "2. Node Module System/Events Module.mp4": 10,
    "2. Node Module System/Event Arguments.mp4": 11,
    "2. Node Module System/Extending EventEmitter.mp4": 12,
    "2. Node Module System/HTTP Module.mp4": 13,
    "2. Node Module System/Node Core Recap.pdf": 14,
    "3. Node Package Manager/Introduction.mp4": 1,
    "3. Node Package Manager/Package.json.mp4": 2,
    "3. Node Package Manager/Installing a Node Package.mp4": 3,
    "3. Node Package Manager/Using a Package.mp4": 4,
    "3. Node Package Manager/Package Dependencies.mp4": 5,
    "3. Node Package Manager/NPM Packages and Source Control.mp4": 6,
    "3. Node Package Manager/Semantic Versioning.mp4": 7,
    "3. Node Package Manager/Listing the Installed Packages.mp4": 8,
    "3. Node Package Manager/Viewing Registry Info for a Package.mp4": 9,
    "3. Node Package Manager/Installing a Specific Version of a Package.mp4": 10,
    "3. Node Package Manager/Updating Local Packages.mp4": 11,
    "3. Node Package Manager/DevDependencies.mp4": 12,
    "3. Node Package Manager/Uninstalling a Package.mp4": 13,
    "3. Node Package Manager/Working with Global Packages.mp4": 14,
    "3. Node Package Manager/Publishing a Package.mp4": 15,
    "3. Node Package Manager/Updating a Published Package.mp4": 16,
    "3. Node Package Manager/NPM Recap.pdf": 17,
    "4. Building RESTful API_s Using Express/Introduction.mp4": 1,
    "4. Building RESTful API_s Using Express/RESTful Services.mp4": 2,
    "4. Building RESTful API_s Using Express/Introducing Express.mp4": 3,
    "4. Building RESTful API_s Using Express/Building Your First Web Server.mp4": 4,
    "4. Building RESTful API_s Using Express/Nodemon.mp4": 5,
    "4. Building RESTful API_s Using Express/Environment Variables.mp4": 6,
    "4. Building RESTful API_s Using Express/Route Parameters.mp4": 7,
    "4. Building RESTful API_s Using Express/Handling HTTP GET Requests.mp4": 8,
    "4. Building RESTful API_s Using Express/Handling HTTP POST Requests.mp4": 9,
    "4. Building RESTful API_s Using Express/Calling Endpoints Using Postman.mp4": 10,
    "4. Building RESTful API_s Using Express/Input Validation.mp4": 11,
    "4. Building RESTful API_s Using Express/Handling HTTP PUT Requests.mp4": 12,
    "4. Building RESTful API_s Using Express/Handling HTTP Delete Requests.mp4": 13,
    "4. Building RESTful API_s Using Express/Project- Build the Genres API.mp4": 14,
    "4. Building RESTful API_s Using Express/Building RESTful APIs with Express Recap.pdf": 15,
}


def fix_names(path: Path) -> Path:
    root = next(next(path.rglob("*")).rglob("*"))
    for filename, index in mappings.items():
        file = root / filename
        file.rename(file.with_stem(f"{index}- {file.stem}"))
    return path


def main(*archives: Path) -> Path:
    merged = merge_zips(*archives, post_process=fix_names)
    return merged
