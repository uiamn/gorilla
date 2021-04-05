import datetime
import glob
import os
import shutil
import sqlite3
import uuid
from typing import List

import cv2
import dotenv
import numpy as np
import requests
import tweepy

dotenv_path = '.env'
dotenv.load_dotenv(dotenv_path)
CONSUMER_KEY = os.environ.get("CK")
CONSUMER_SECRET = os.environ.get("CSK")
ACCESS_TOKEN = os.environ.get("AT")
ACCESS_TOKEN_SECRET = os.environ.get("ATS")

DB_PATH = 'db.sqlite3'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

def is_result_image(filepath: str) -> bool:
    img = cv2.imread(filepath)

    # The width of result images is 640 and the height of them is 480
    height, width = img.shape[:2]
    if height != 480 or width != 640:
        return False

    # Determine if an image is an result picture or not using pixel values.
    # If 5 of the 6 pixels have the specified pixel value, determine a result picture.
    a = [
        img[3, 0] == [111, 77, 28],
        img[3, width-1] == [111, 77, 28],
        img[3, width//2] == [255, 200, 82],
        img[height-3, 0] == [131, 91, 35],
        img[height-3, width-1] == [131, 91, 35],
        img[height-3, width//2] == [131, 91, 35]
    ]

    if len(list(filter(lambda x: x, map(all, a)))) >= 5:
        return True
    else:
        return False


def download_image(url: str) -> str:
    resp = requests.get(url)
    filename = url.split('/')[-1]

    with open(f'temp/{filename}', 'wb') as f:
        f.write(resp.content)

    return filename


def get_tweets() -> List[tweepy.Status]:
    with open('LATEST_TWEET_ID.txt') as f:
        since_id = int(f.read())

    query = 'from:_yosotsu filter:images -filter:retweets'

    results = api.search(
        q=query, count=100, result_type='recent', since_id=since_id
    )

    # save the latest tweet id
    if len(results) != 0:
        with open('LATEST_TWEET_ID.txt', 'w') as f:
            f.write(str(results[0].id))

    return results


def add_tweet(status: tweepy.Status, temp_filename: str) -> None:
    filename = f'{uuid.uuid4().hex}.png'
    shutil.move(f'temp/{temp_filename}', f'images/{filename}')
    created_at = datetime.datetime.strftime(status.created_at, '%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO tweets (tweet, filename, created_at) VALUES (?, ?, ?)',
        (status.text, filename, created_at)
    )

    conn.commit()
    conn.close()


def remove_temp_files() -> None:
    temp_files = glob.glob('temp/*')
    for filepath in temp_files:
        os.remove(filepath)


def main() -> None:
    tweets = get_tweets()

    for status in tweets:
        image_url = status.extended_entities['media'][0]['media_url']
        filename = download_image(image_url)
        if is_result_image(f'temp/{filename}'):
            add_tweet(status, filename)

    remove_temp_files()

if __name__ == '__main__':
    main()
