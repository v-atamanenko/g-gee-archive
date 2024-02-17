import json
import random
import os
from tqdm import tqdm

def load_json(input_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'.")
        return None

    return data

def save_json(output_file, data):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

def _find_by_id(data, id):
    idx = 0
    found = False
    for i in data:
        if i['id'] == id:
            found = True
            break
        idx += 1
    if not found:
        raise Exception("No item with id "+str(id)+" found in data")
    return idx

# gets dictionary key by index
def _dk(_dict, _idx):
    return list(_dict.keys())[_idx]

# gets dictionary val by index
def _dv(_dict, _idx):
    return list(_dict.values())[_idx]

# gets last dictionary key
def _dkl(_dict):
    return list(_dict.keys())[len(list(_dict.keys())) - 1]

# gets last dictionary val
def _dvl(_dict):
    if len(list(_dict.values())) == 0:
        return ""
    return list(_dict.values())[len(list(_dict.values())) - 1]

def _filter_strings(_dict):
    if len(_dict.keys()) == 0:
        return _dict;

    _dict_new = { _dk(_dict, 0): _dv(_dict, 0)}
    for key, val in _dict.items():
        if key in _dict_new.keys():
            continue
        if _dvl(_dict_new) == val:
            continue
        _dict_new[key] = val
        _dict_new = dict(sorted(_dict_new.items()))
    return _dict_new

def _filter_arrays(_dict):
    if len(_dict.keys()) == 0:
        return _dict;

    _dict_new = { _dk(_dict, 0): _dv(_dict, 0)}
    for key, val in _dict.items():
        if key in _dict_new.keys():
            continue
        if len(_dvl(_dict_new)) == len(val):
            i = 0
            m = True
            for item in _dvl(_dict_new):
                if item != val[i]:
                    m = False
                    break
                i += 1
            if m:
                continue
        _dict_new[key] = val
        _dict_new = dict(sorted(_dict_new.items()))
    return _dict_new

def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list

def restructure(data):
    out = []

    item_idx = -1
    print("Flattening data..")
    data = flatten_extend(data)
    print("Started restructure...")

    for item in tqdm(data):
        item_idx += 1

        # A hack for ゾンビシーズ̏ that never had an assigned id / detail view
        if item['id'] == 'apps':
            item['id'] = 9999

        if not any(i['id'] == item['id'] for i in out):
            out.append({
                        "id": item['id'],
                        'title': {},
                        'icon_url': {},
                        'publisher': {},
                        'category': {},
                        'price': {},
                        'description': {},
                        'description_short': {},
                        'screenshots': {},
                        'created_at': "",
                        'updated_at': ""
                       })

        idx = _find_by_id(out, item['id'])
        obj = out[idx]

        key = item['timestamp']
        if key in obj['title']:
            key += "_"+str(item_idx)

        obj['title'][key] = item['title']
        obj['icon_url'][key] = item['icon_url']
        obj['publisher'][key] = item['publisher']
        obj['category'][key] = item['category']
        obj['price'][key] = item['price'].replace("価格：","")
        # The following three fields can be not present due to listing/detail difference
        if len(item['description']) > 0:
            obj['description'][key] = item['description']
        if len(item['description_short']) > 0:
            obj['description_short'][key] = item['description_short']
        if len(item['screenshots']) > 0:
            obj['screenshots'][key] = item['screenshots']

        out[idx] = obj

    out_sorted = []
    for i in out:
        out_sorted.append({
                          "id": int(i['id']),
                          'title': dict(sorted(i['title'].items())),
                          'icon_url': dict(sorted(i['icon_url'].items())),
                          'publisher': dict(sorted(i['publisher'].items())),
                          'category': dict(sorted(i['category'].items())),
                          'price': dict(sorted(i['price'].items())),
                          'description': dict(sorted(i['description'].items())),
                          'description_short': dict(sorted(i['description_short'].items())),
                          'screenshots': dict(sorted(i['screenshots'].items())),
                          'created_at': "",
                          'updated_at': ""
                          })
    return sorted(out_sorted, key=lambda d: d['id'])

def filter_timestamps(data):
    out = []

    print("Started filter_timestamps...")
    for item in tqdm(data):
        i = item

        i['created_at'] = int(_dk(i['title'], 0))

        i['title'] = _filter_strings(i['title'])
        i['icon_url'] = _filter_strings(i['icon_url'])
        i['publisher'] = _filter_strings(i['publisher'])
        i['category'] = _filter_strings(i['category'])
        i['price'] = _filter_strings(i['price'])
        i['description'] = _filter_strings(i['description'])
        i['description_short'] = _filter_strings(i['description_short'])
        i['screenshots'] = _filter_arrays(i['screenshots'])

        latest_ts = i['created_at']
        for k, v in i.items():
            if not isinstance(v, dict):
                continue
            for kk, vv in v.items():
                if int(kk) > latest_ts:
                    latest_ts = int(kk)

        i['updated_at'] = latest_ts

        out.append(i)

    return out

def _url_to_path(url):
    url = url.replace("http://dl.gmo-game.com/app/1.0.0/images/", "")
    url = url.replace("/", "_")
    url = "assets/" + url
    return url

def filter_images(data):
    out = []

    existing_files = []
    dirls = os.listdir('assets')

    for d in dirls:
        existing_files.append('assets/' + d)

    print("Started filter_images...")
    for item in tqdm(data):
        i = item

        icon_url_new = {}
        for k, v in i['icon_url'].items():
            filepath = _url_to_path(v)
            if os.path.exists(filepath.replace("/", os.sep)):
                icon_url_new[k] = filepath
        i['icon_url'] = icon_url_new

        screenshots_new = {}
        for k, v in i['screenshots'].items():
            ls = []
            for x in v:
                filepath = _url_to_path(x)
                if filepath in existing_files:
                    ls.append(filepath)
            if len(ls) > 0:
                screenshots_new[k] = ls
        i['screenshots'] = screenshots_new

        out.append(i)

    return out

def _get_screenshot_id(p):
    parts = p.split("_")
    return "_".join(parts[-2:])

def minify(data):
    out = []

    print("Started minify...")
    for item in tqdm(data):
        i = item

        screenshots = i['screenshots']
        if len(list(i['screenshots'].values())) == 0:
            screenshots = []
        elif len(list(i['screenshots'].values())) == 1:
            screenshots = _dvl(i['screenshots'])
        else:
            known_screens = _dvl(i['screenshots'])
            idx = len(list(i['screenshots'].values())) - 1
            while idx >= 0:
                screens = _dv(i['screenshots'], idx)
                for screen in screens:
                    found = False
                    for kscreen in known_screens:
                        if kscreen.endswith(_get_screenshot_id(screen)):
                            found = True
                            break
                    if not found:
                        known_screens.append(screen)
                idx -= 1
            screenshots = known_screens

        price = _dvl(i['price']).replace('無料', '0')
        try:
            price = int(price)
        except:
            print("exception at id "+str(i['id']))

        out.append({
                   'id': i['id'],
                   'title': _dvl(i['title']),
                   'icon_url': _dvl(i['icon_url']),
                   'publisher': _dvl(i['publisher']),
                   'category': _dvl(i['category']),
                   'price': price,
                   'description': _dvl(i['description']),
                   'description_short': _dvl(i['description_short']),
                   'screenshots': screenshots,
                   'created_at': i['created_at'],
                   'updated_at': i['updated_at']
                   })

    return out

#'title': dict(sorted(i['title'].items())),
#                          'icon_url': dict(sorted(i['icon_url'].items())),
#                          'publisher': dict(sorted(i['publisher'].items())),
#                          'category': dict(sorted(i['category'].items())),
#                          'price': dict(sorted(i['price'].items())),
#                          'description': dict(sorted(i['description'].items())),
#                          'description_short': dict(sorted(i['description_short'].items())),
#                          'screenshots': dict(sorted(i['screenshots'].items())),

data = load_json('ggee-entries-raw.json')
if data:
    data = restructure(data)
    data = filter_timestamps(data)
    save_json('ggee-db-full.json', data)

    data = filter_images(data)
    data = minify(data)
    save_json('ggee-db-compact.json', data)
