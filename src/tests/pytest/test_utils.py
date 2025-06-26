import json
import os


def read_urls(file_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(dir, file_path)
    
    with open(full_file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def write_json(file_path, data):
    dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(dir, file_path)

    with open(full_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)