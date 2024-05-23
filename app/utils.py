import os
import requests
from typing import Dict
import hashlib
from app.constants import IMG_FOLDER_PATH, STATIC_TOKEN
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


def load_config():
    return {
        "auth_token": STATIC_TOKEN
    }

def download_image(url: str) -> str:
    response = requests.get(url, stream=True)
    content_type = response.headers.get('content-type')
    if content_type.startswith('image/'):
        content_type = content_type.split('/')[1]
    if not os.path.exists(IMG_FOLDER_PATH):
        os.makedirs(IMG_FOLDER_PATH)
    save_path = f"{IMG_FOLDER_PATH}/{hashlib.md5(url.encode('utf-8')).hexdigest()}.{content_type}"
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return save_path


def make_request_with_proxy(url: str, proxy: Dict, retry_time: int, retries: int):
    # Define the retry decorator
    @retry(
        stop=stop_after_attempt(retries),
        wait=wait_fixed(retry_time),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ProxyError))
    )
    def fetch():
        response = requests.get(url)
        # response = requests.get(url=url, proxies=proxy) # Intensionally turned off due to unavailability of proxy
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response

    try:
        response = fetch()
        return response  # or response.json() if the response is JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None