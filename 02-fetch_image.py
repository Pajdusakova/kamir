import os
import shutil
import sqlite3
import requests
import numpy as np
from io import BytesIO
import cv2
import time

path_db_kamir = './data/db/kamir_cardpool.sqlite'
data_img_dir = './data/img/'
path_img_proxy = './resources/no_image.jpg'

def fetch_image():
    conn = sqlite3.connect(path_db_kamir)
    cur = conn.cursor()

    cur.execute(
        """
            SELECT
                name,
                expansion,
                number,
                mana_value,
                layout
            FROM cards
            WHERE
                layout == \"normal\" OR
                layout == \"adventure\" OR
                layout == \"transform\" OR
                layout == \"meld\" OR
                layout == \"modal_dfc\"
            AND mana_value >= 0
            ORDER BY mana_value, name
        """
        )

    cards = cur.fetchall()

    conn.close()

    for c in cards:
        card_name = c[0]
        set_code = str(c[1])
        number = str(c[2])
        mana_value = str(c[3])
        layout = c[4]
        print(card_name)

        try:
            save_path = data_img_dir + mana_value + '/' + card_name + ".jpg"
            if os.path.exists(save_path) :
                continue

            time.sleep(1) # 先方に負荷かけないようにウェイトを置く

            api_url = "https://api.scryfall.com/cards/{0}/{1}".format(set_code.lower(), number)
            # 画像DL
            if layout == "transform" or layout == "meld" or layout == "modal_dfc":
                # FIXME: meldの片方は必ずエラーになってしまう（15aとかの形をしているため）のであとで直す
                response = requests.get(api_url).json()["card_faces"]
                card_front_face = [i for i in response if i['name'] == card_name][0]
                card_url = card_front_face["image_uris"]["large"]
            else:
                card_url = requests.get(api_url).json()["image_uris"]["large"]
            img_bin = requests.get(card_url).content
            file_bytes = np.asarray(bytearray(BytesIO(img_bin).read()),
                                    dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            img_resized = cv2.resize(img, (223, 310))
            img_trim = img_resized[47:47+100, 26:26+171]
            cv2.imwrite(save_path, img_trim)
        except:
            print("error occured!!!!!!!!!!!!!!!!!!!!!!!!!")
            shutil.copyfile(path_img_proxy, save_path)

if __name__ == '__main__':
    fetch_image()