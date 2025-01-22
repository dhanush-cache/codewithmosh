import subprocess

from pyperclip import copy

from utils.configs import ON_ANDROID


def copy_to_clipboard(text: str, label: str = "Text", quiet=False) -> None:
    if ON_ANDROID:
        __termux_copy(text, label)
    else:
        copy(text)
    if not quiet:
        print(f"{label}: {text} copied...✔")


def __termux_copy(text, label):
    try:
        subprocess.run(
            ["termux-clipboard-set"],
            input=text.encode(),
            check=True,
            timeout=5,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        print(f"{label}: {text}")
