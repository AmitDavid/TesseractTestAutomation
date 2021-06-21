import csv
import os
import subprocess
import sys

DEFAULT_FILENAME = "input.csv"
TEMP_FILENAME = "output_file.txt"


def get_font_name_and_size(file_name: str) -> (str, str):
    # Filename will be in format: "{font_name}_{font_size}pt.jpg"
    return file_name.split('_')[0], ''.join(filter(str.isdigit, file_name))


def read_csv(file_path: str) -> (set, dict):
    configs = []
    fonts_dict = {}

    with open(file_path) as csv_file:
        reader = csv.reader(csv_file)

        # Skip header
        next(reader)

        for i, row in enumerate(reader):
            configs += [row]
            font_name, font_size = get_font_name_and_size(row[1])

            if font_name not in fonts_dict:
                fonts_dict[font_name] = []

            fonts_dict[font_name] += [(int(font_size), i)]

    return configs, fonts_dict


def run_tesseract(command: str, output_file: str, expected: str) -> bool:
    # Run Tesseract. Mute stderr
    proc = subprocess.Popen(command, stderr=subprocess.PIPE)
    # Wait for Tesseract
    proc.communicate()

    with open(output_file, 'r') as file:
        return file.read().strip() == expected


def test_font(configs: list, font_sizes: dict) -> int:
    min_size = ""
    # We check fonts in decreasing order. When a test fail,
    # return the previous size since it was the smallest test that passed
    for font_size, row_index in sorted(font_sizes, reverse=True):
        row = configs[row_index]
        backslash = '\\' if row[0] else ''
        command = f'tesseract {row[0]}{backslash}{row[1]} output_file'
        for j in range(3, len(row)):
            if row[j] != "":
                command += f' -c {row[j]}'

        if run_tesseract(command, TEMP_FILENAME, row[2]):
            min_size = font_size
        else:
            return min_size

    return min_size


def test_all(configs: list, fonts_dict: dict) -> dict:
    success_dict = {}

    for font_type, font_sizes in fonts_dict.items():
        success_dict[font_type] = test_font(configs, font_sizes)

    return success_dict


def print_results(results: dict) -> None:
    for font_name, font_size in sorted(results.items()):
        print(f'{font_name},{font_size}')


if __name__ == '__main__':
    file_path = DEFAULT_FILENAME
    if len(sys.argv) == 2:
        file_path = sys.argv[1]

    configs, fonts_dict = read_csv(file_path)
    results = test_all(configs, fonts_dict)
    print_results(results)

    # Delete temporary help file
    os.remove(TEMP_FILENAME)
