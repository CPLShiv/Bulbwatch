import requests
import shutil


class Network:

    def __init__(self, url):
        self.r_get = requests.get(url, stream=True)

    def download_image(self, filename):
        self.r_get.raw.decode_content = True

        with open(filename, 'wb') as f:
            shutil.copyfileobj(self.r_get.raw, f)