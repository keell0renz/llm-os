"""Little goofy utils for my simple chat <3"""

import base64


def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to a base64 encoded string.

    Args:
    - image_path (str): The path to the image file.

    Returns:
    - str: The base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
