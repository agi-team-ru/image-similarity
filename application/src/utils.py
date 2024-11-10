import os
from typing import List


def read_file(path: str):
    with open(path, "r") as f:
        return f.read()


def read_dir_files(path: str):
    ret: List[str] = []
    for entry in os.scandir(path):
        if entry.is_file():
            ret.append(entry.name)
    return ret
