import requests
import logging
import xml.etree.ElementTree as xmlTree

from base64 import b64encode
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from src.podcast import Podcast

logging.basicConfig(level=logging.INFO)

APPLE_ICON = "https://www.freepnglogos.com/uploads/apple-logo-png/apple-logo-png-transparent-svg-vector-bie-supply-29.png"
ITUNES_ENDPOINT = f"https://itunes.apple.com/search?media=podcast&term="


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


def get_podcast_details(podcast_title):
    url = ITUNES_ENDPOINT + podcast_title

    response = requests.get(url)
    response = response.json()

    if response.get("results"):
        result = response["results"][0]
        artist_name = result.get("artistName", "")
        track_name = result.get("trackName", "")
        artwork_url = result.get("artworkUrl600", "")
        feed_url = result.get("feedUrl", "")
        return Podcast(artist_name, track_name, artwork_url, feed_url)


def get_podcast_card(podcast_title, card):
    podcast = get_podcast_details(podcast_title)
    apple_icon = album_art_b64(APPLE_ICON)
    artwork_url = album_art_b64(podcast.artwork_url)

    track_name = podcast.track_name
    artist_name = podcast.artist_name

    podcast_description = "Unreachable"

    if card == "simple":
        card_template = "podcast_simple.html.j2"
    elif card == "detailed":
        card_template = "podcast_detailed.html.j2"
        podcast_description = get_podcast_description(podcast.feed_url)
        podcast_description = (podcast_description[:110] + "...") if len(podcast_description) > 114 else podcast_description
    else:
        track_name = (track_name[:20] + "...") if len(track_name) > 22 else track_name
        card_template = "podcast.html.j2"

    svg = render_template(
        card_template,
        artwork_url=artwork_url,
        track_name=track_name,
        artist_name=artist_name,
        apple_icon=apple_icon,
        podcast_description=podcast_description,
    )

    return svg


class PodcastCard:
    def __init__(self):
        load_dotenv()


app = Flask(__name__, template_folder="templates")
rc = PodcastCard()


@app.route("/", methods=["GET"])
def handle_all():
    if request.args.get("podcast"):
        podcast = request.args.get("podcast")
    else:
        podcast = "the-daily"

    if request.args.get("design"):
        card = request.args.get("design")
    else:
        card = "default"

    svg = get_podcast_card(podcast, card)

    resp = Response(svg, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp


if __name__ == "__main__":
    app.run(debug=True, port=5050)
