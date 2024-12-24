from PIL import Image
from datetime import datetime as dt
from pathlib import Path
import os
import json


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

def save_chat_history(history: list[dict], model_name: str):
    if history:
        folder = Path(__file__).parent.parent.resolve() / 'history' / model_name
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_name = create_unique_file_name()
        with open(folder / f"{file_name}.json", "w") as f:
            json.dump(history, f)


if __name__ == "__main__":
    create_unique_file_name()