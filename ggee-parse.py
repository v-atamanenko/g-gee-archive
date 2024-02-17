import os
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def get_id_from_path(file_path):
    sep = '/'
    if '\\' in file_path:
        sep = '\\'
    parts = file_path.split(sep)

    try:
        part = parts[-2]
    except Exception as e:
        print("get_id_from_path: exception for path " + file_path)
        return "#"

    if '_' in part:
        part = parts[-3]

    return part.replace(',', '')

def get_ts_from_path(file_path):
    sep = '/'
    if '\\' in file_path:
        sep = '\\'
    parts = file_path.split(sep)
    for part in parts:
      if len(part) == 14:
        return part

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        txt = file.read()
        if "指定のページは存在しないか、エラーのため表示できません。" in txt:
            print("Skipped internal 404/500 by path " + file_path)
            return None

    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        title = soup.title
        if not title:
            print("Skipped no title for path " + file_path)
            return None

        if soup.title.get_text() == "404 Not Found":
            print("Skipped 404 for path " + file_path)
            return None

        ttl_major_box = soup.find('div', class_='ttl_major_box')
        app_detail_text_container = soup.find('div', class_='app_detail_text')

        # Listing pages
        if ttl_major_box:
            print("Processing index by path " + file_path)
            res = []
            i = 0
            for box in soup.findAll('div', class_='ttl_major_box'):
                i += 1
                app_title = box.find('h3')
                app_id = get_id_from_path(app_title.find('a')['href'])
                app_icon = box.find('img')['src']

                paragraphs = box.find('div', class_='ttl_major_box_r').findAll('p')
                app_cpname = paragraphs[0]
                app_price = paragraphs[1]
                app_category = paragraphs[2]

                try:
                    app_description = box.find('p', class_='app_description').text.strip().replace('続きを読む','')
                except Exception as e:
                    print("Exception for path " + file_path + ", could not find app_description at box #"+str(i))
                    continue

                res.append({
                    'id': app_id,
                    'title': app_title.text.strip(),
                    'icon_url': app_icon,
                    'publisher': app_cpname.text.strip(),
                    'category': app_category.text.strip().replace("カテゴリ：", ""),
                    'price': app_price.text.strip().replace("円",""),
                    'description': '',
                    'description_short': app_description,
                    'screenshots': [],
                    'timestamp': get_ts_from_path(file_path)
                })

            return res
        # Detail pages
        elif app_detail_text_container:
            print("Processing single app by path " + file_path)
            app_icon_container = soup.find('p', class_='app_icon')
            app_icon = app_icon_container.find('img')
            app_icon_src = app_icon['src']


            app_title = soup.find('h2', class_='app_title')
            app_cpname = soup.find('p', class_='app_cpname').find('span')
            if not app_cpname:
                app_cpname = soup.find('p', class_='app_cpname')
            app_price = soup.find('p', class_='app_price')
            app_category = soup.find('p', class_='app_category')

            app_detail_text_arr = []
            app_detail_text_container = soup.find('div', class_='app_detail_text') # use all nested Ps
            for p in app_detail_text_container.findAll('p', recursive=False):
                app_detail_text_arr.append(p.text.strip())
            app_detail_text = '\n\n'.join(app_detail_text_arr)

            app_detail_text_container_gallery = app_detail_text_container.find('div', class_='gallery')
            if not app_detail_text_container_gallery:
                app_detail_text_container_gallery = app_detail_text_container.find('div', class_='gallery2')
            app_detail_text_container_gallery_jCarouselLite = app_detail_text_container_gallery.find('div', class_='jCarouselLite')
            app_detail_text_container_gallery_jCarouselLite_ul = app_detail_text_container_gallery_jCarouselLite.find('ul')
            screenshots = []
            for li in app_detail_text_container_gallery_jCarouselLite_ul.findAll('li'):
                screenshots.append(li.find('img')['src'])

            return [{
                'id': get_id_from_path(file_path),
                'title': app_title.text.strip(),
                'icon_url': app_icon_src,
                'publisher': app_cpname.text.strip(),
                'category': app_category.text.strip().replace("カテゴリ：", ""),
                'price': app_price.text.strip().replace("円",""),
                'description': app_detail_text,
                'description_short': '',
                'screenshots': screenshots,
                'timestamp': get_ts_from_path(file_path)
            }]
        else:
            print("Warning: no shit found in path " + file_path)

        return None

def process_directory(directory):
    result_array = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower() == 'index.html':
                file_path = os.path.join(root, file)
                parsed_data = parse_html(file_path)
                if parsed_data:
                    result_array.append(parsed_data)
    return result_array

def scan_directories(parent_directory):
    result_array = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        directories = [os.path.join(parent_directory, directory) for directory in os.listdir(parent_directory) if os.path.isdir(os.path.join(parent_directory, directory))]
        futures = [executor.submit(process_directory, directory) for directory in directories]
        for future in futures:
            result_array.extend(future.result())

    return result_array

def export_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

if __name__ == "__main__":
    input_directory = "gmo-game.com"
    output_file = "ggee-entries-raw.json"

    parsed_data_array = scan_directories(input_directory)
    export_to_json(parsed_data_array, output_file)
