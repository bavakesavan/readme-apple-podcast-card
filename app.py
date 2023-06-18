import requests
import logging

from base64 import b64encode
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from podcast import Podcast

logging.basicConfig(level=logging.INFO)

APPLE_ICON = "https://www.apple.com/ac/structured-data/images/knowledge_graph_logo.png"
ITUNES_ENDPOINT = f"https://itunes.apple.com/search?media=podcast&term="


def album_art_b64(img_url: str):
    res = requests.get(img_url, headers={}, cookies={})
    return b64encode(res.content).decode("ascii")


def get_podcast_details(podcast_name):
    url = ITUNES_ENDPOINT + podcast_name

    response = requests.get(url)
    response = response.json()

    if response.get("results"):
        result = response["results"][0]
        artist_name = result.get("artistName", "")
        track_name = result.get("trackName", "")
        artwork_url = result.get("artworkUrl600", "")
        return Podcast(artist_name, track_name, artwork_url)


def get_podcast_card(podcast_name):
    podcast = get_podcast_details(podcast_name)
    apple_icon = album_art_b64(APPLE_ICON)
    artwork_url = album_art_b64(podcast.artwork_url)

    track_name = podcast.track_name
    artist_name = podcast.artist_name

    track_name = (track_name[:20] + "...") if len(track_name) > 22 else track_name

    svg = render_template(
        "podcast.html.j2",
        artwork_url=artwork_url,
        track_name=track_name,
        artist_name=artist_name,
        apple_icon=apple_icon,
    )

    return svg


class PodcastCard:
    def __init__(self):
        load_dotenv()


app = Flask(__name__, template_folder="templates")
rc = PodcastCard()


@app.route("/", methods=["GET"])
def handle_all():
    if request.args:
        podcast_name = request.args.get("podcast_name")
    else:
        podcast_name = "the-daily"
    svg = get_podcast_card(podcast_name)

    resp = Response(svg, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp


if __name__ == "__main__":
    app.run(debug=True, port=5050)
