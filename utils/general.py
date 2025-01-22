import subprocess

from pyperclip import copy  # type: ignore

from utils.configs import ON_ANDROID


def copy_to_clipboard(text: str, label: str = "Text", quiet: bool = False) -> None:
    """
    Copies the given text to the clipboard.

    Parameters:
    text (str): The text to be copied to the clipboard.
    label (str, optional): A label to describe the text being copied. Defaults to "Text".
    quiet (bool, optional): If set to True, suppresses the print statement. Defaults to False.

    Returns:
    None
    """
    if ON_ANDROID:
        __termux_copy(text, label)
    else:
        copy(text)
    if not quiet:
        print(f"{label}: {text} copied...✔")


def __termux_copy(text: str, label: str):
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
