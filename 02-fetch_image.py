import sqlite3
import requests
import numpy as np
from io import BytesIO
import cv2
import time

path_db_kamir = './data/db/kamir_cardpool.sqlite'
data_img_dir = './data/img/'
path_img_proxy = './no_image.jpg'

# 人種差別的とされてイラストが削除されたカード
ban_list = ['Crusade', 'Pradesh Gypsies', 'Stone-Throwing Devils']

def fetch_image():
    conn = sqlite3.connect(path_db_kamir)
    cur = conn.cursor()
    
    cur.execute("SELECT name, multiverse_id, mana_value, layout FROM cards WHERE layout == \"normal\" OR layout == \"adventure\" OR layout == \"transform\" OR layout == \"meld\" OR layout == \"modal_dfc\" ORDER BY mana_value, name")
    
    cards = cur.fetchall()
    
    conn.close()
    
    for c in cards:
        time.sleep(1) # 先方に負荷かけないようにウェイトを置く
        
        card_name = c[0]
        multiverse_id = str(c[1])
        mana_value = str(c[2])
        print(card_name)
        
        # 上記に挙げたカードは代替の画像を差し込む
        if card_name in ban_list:
            save_path = data_img_dir + mana_value + '/' + card_name + ".jpg"
            img = cv2.imread(path_img_proxy, cv2.IMREAD_GRAYSCALE)
            cv2.imwrite(save_path, img)
            continue
        
        save_path = data_img_dir + mana_value + '/' + card_name + ".jpg"
        card_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseId=' + \
            multiverse_id + '&type=card'
        # 画像DL
        img_bin = requests.get(card_url).content
        file_bytes = np.asarray(bytearray(BytesIO(img_bin).read()),
                                dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        img_resized = cv2.resize(img, (223, 310))
        img_trim = img_resized[47:47+100, 26:26+171]
        cv2.imwrite(save_path, img_trim)

if __name__ == '__main__':
    fetch_image()