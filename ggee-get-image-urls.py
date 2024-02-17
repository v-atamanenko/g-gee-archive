import json

def process_json(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'.")
        return

    icon_urls = set()
    screenshots = set()

    for d in data:
        for item in d:
            if 'icon_url' in item:
                icon_urls.add(item['icon_url'])

            if 'screenshots' in item and isinstance(item['screenshots'], list):
                screenshots.update(item['screenshots'])

    unique_values = list(icon_urls.union(screenshots))

    with open(output_file, 'w') as f:
        for value in unique_values:
            f.write(value + '\n')

    print(f"Unique values exported to '{output_file}'.")

input_json_file = 'ggee-entries-raw.json'
output_txt_file = 'ggee-image-urls.txt'
process_json(input_json_file, output_txt_file)
