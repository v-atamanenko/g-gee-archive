# g-gee-archive

A copy of G-Gee (Gゲー) Japanese Android store (http://gmo-game.com, down since 2017) metadata and images for preservation purposes.

Fetched from web.archive.org using the scripts provided in the repository and [wayback-machine-downloader](https://github.com/hartator/wayback-machine-downloader/).

## ggee-db-full.json

Contains all changes to all items with timestamp, original image URLs preserved.

## ggee-db-compact.json

Contains latest known state for each item and only the images that could be found on web.archive.org, paths adjusted to the generated `assets` folder.

## How to fetch data yourself

To fetch the data yourself and reproduce the provided `ggee-db-compact.json` and `ggee-db-full.json`, do the following:

1. Install python 3.7+
2. Install ruby and wayback-machine-downloader. I recommend using [my fork](https://github.com/v-atamanenko/wayback-machine-downloader/blob/master/README.md) to avoid rate-limiting issues.
3. Fetch HTML from web.archive.org using: `wayback_machine_downloader http://gmo-game.com -d gmo-game.com -f 20110201114413 -t 20170308084621 -a -c 10 -p 500`. You should have a `gmo-game.com` folder as a result.
4. Parse the fetched html using `python ggee-parse.py`. You should have a `ggee-entries-raw.json` file as a result.
5. Acquire a list of unique image urls with `python ggee-get-image-urls.py`. You should have a `ggee-image-urls.txt` file as a result.
6. Fetch images from web.archive.org using `python ggee-download-images.py`. You should have an `images` folder as a result.
7. Create assets folder using `python ggee-sort-out-images.py`. You should have an `assets` folder as a result.
8. Finally, run `python ggee-compile-database.py` to create `ggee-db-compact.json` and `ggee-db-full.json`.
