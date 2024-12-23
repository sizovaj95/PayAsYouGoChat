from PIL import Image
from datetime import datetime as dt
from pathlib import Path


def save_image(image, save_path):
    pil_image = Image.fromarray(image)
    pil_image.save(save_path)

def create_unique_file_name() -> str:
    now = dt.now()
    day, month, year = now.day, now.month, now.year
    hour, minute, second = now.hour, now.minute, now.second
    file_name = f"{day}{month}{str(year)[-2:]}_{hour}{minute}{second}"
    return file_name


def return_test_image():
    return Path(__file__).parent.parent.resolve() / "test_image.jpg"



if __name__ == "__main__":
    create_unique_file_name()