import requests
import xml.etree.ElementTree as xmlTree
from base64 import b64encode


def album_art_b64(img_url: str):
    res = requests.get(img_url, headers={}, cookies={})
    return b64encode(res.content).decode("ascii")


def get_podcast_description(feed_url):
    response = requests.get(feed_url)

    if response.status_code == 200:
        xml_data = response.content

        try:
            root = xmlTree.fromstring(xml_data)
            channel = root.find('channel')
            description = channel.find('description').text

            return description
        except xmlTree.ParseError:
            return None
    else:
        return None
