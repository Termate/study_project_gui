import os
import shutil
import re
from datetime import datetime


def copy_file(path: str) -> str:

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

    new_name = f"copy_{os.path.basename(path)}"
    dest_path = os.path.join(os.path.dirname(path), new_name)

    shutil.copy2(path, dest_path)
    return dest_path


def delete_path(path: str) -> bool:

    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь не найден: {path}")

    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    else:
        shutil.rmtree(path)

    return True


def count_files(directory: str) -> int:

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Это не папка: {directory}")

    total = 0
    for _, _, files in os.walk(directory):
        total += len(files)
    return total


def find_files(directory: str, pattern: str) -> list[str]:

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Это не папка: {directory}")

    regex = re.compile(pattern)
    result: list[str] = []

    for root, _, files in os.walk(directory):
        for file in files:
            if regex.search(file):
                result.append(os.path.join(root, file))

    return result


def add_creation_date(path: str, recursive: bool = False) -> list[str]:

    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь не найден: {path}")

    def rename_file(file_path: str) -> str:
        timestamp = os.path.getctime(file_path)
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

        directory = os.path.dirname(file_path)
        name = os.path.basename(file_path)

        # чтобы не добавлять дату повторно
        if name.startswith(date_str + "_"):
            return file_path

        new_name = f"{date_str}_{name}"
        new_path = os.path.join(directory, new_name)

        os.rename(file_path, new_path)
        return new_path

    renamed: list[str] = []

    if os.path.isfile(path):
        renamed.append(rename_file(path))
        return renamed

    # path — папка
    if recursive:
        for root, _, files in os.walk(path):
            for file in files:
                renamed.append(rename_file(os.path.join(root, file)))
    else:
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                renamed.append(rename_file(full_path))

    return renamed


def analyse(directory: str) -> tuple[int, dict[str, int]]:

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Это не папка: {directory}")

    summary: dict[str, int] = {}
    total_size = 0

    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)

        if os.path.isfile(full_path):
            size = os.path.getsize(full_path)
        else:
            size = 0
            for root, _, files in os.walk(full_path):
                for f in files:
                    size += os.path.getsize(os.path.join(root, f))

        summary[item] = size
        total_size += size

    return total_size, summary
