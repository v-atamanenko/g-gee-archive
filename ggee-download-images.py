import subprocess
from concurrent.futures import ThreadPoolExecutor

def download_with_wayback_machine(url):
    command = f"wayback_machine_downloader -d ./images/ -s -t 20170308235959 -e -p 500 {url}"
    subprocess.run(command, shell=True)

input_file = "ggee-image-urls.txt"

with open(input_file, "r") as file:
    strings = [line.strip() for line in file.readlines()]

with ThreadPoolExecutor(max_workers=1) as executor:
    executor.map(download_with_wayback_machine, strings)
