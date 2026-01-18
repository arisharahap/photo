import os
import platform

def print_photo(file_path):
    abs_path = os.path.abspath(file_path)
    if platform.system() == "Windows":
        os.system(f'mspaint /p "{abs_path}"')
    else:
        os.system(f'lp "{abs_path}"')