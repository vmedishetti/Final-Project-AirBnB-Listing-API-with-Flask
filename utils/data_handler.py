import json

def read_data(file_path: str) -> list:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_data(file_path: str, data: list) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)