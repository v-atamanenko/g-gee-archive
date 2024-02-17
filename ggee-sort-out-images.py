import os
import shutil

def copy_images(src_dir, dest_dir):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # Extract parts of the directory structure
            relative_path = os.path.relpath(file_path, src_dir)
            parts = relative_path.split(os.sep)

            # Create the new file name
            new_name = '_'.join(parts[4:])
            new_path = os.path.join(dest_dir, new_name)

            # Copy the file to the new location
            shutil.copy(file_path, new_path)

source_directory = "images"
destination_directory = "assets"

if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

copy_images(source_directory, destination_directory)

print("Images copied successfully.")
