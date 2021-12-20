import requests
import os

BASE_IMAGE_CACHE_BASE_PATH = "cache/images"

def check_path():
    os.makedirs(BASE_IMAGE_CACHE_BASE_PATH, exist_ok=True)

def load_image(url):
    check_path()
    file_name = url.split('/')[-1]
    local_path = os.path.join(BASE_IMAGE_CACHE_BASE_PATH, file_name)
    if os.path.exists(local_path) and not os.path.isdir(local_path):
        return local_path
    else:
        with open(local_path, "wb") as f:
            f.write(requests.get(url).content)
        return local_path

if __name__ == '__main__':
    url = "https://upload-bbs.mihoyo.com/game_record/genshin/character_side_icon/UI_AvatarIcon_Side_Sara.png"
    load_image(url)
    check_path()