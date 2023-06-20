import requests

from flask import render_template
from src.utils.utils import album_art_b64, get_podcast_description
from src.podcast import Podcast

APPLE_ICON = "https://www.freepnglogos.com/uploads/apple-logo-png/apple-logo-png-transparent-svg-vector-bie-supply-29.png"
ITUNES_ENDPOINT = f"https://itunes.apple.com/search?media=podcast&term="


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
        podcast_description = (podcast_description[:100] + "...") if len(
            podcast_description) > 100 else podcast_description
    else:
        track_name = (track_name[:18] + "...") if len(track_name) > 18 else track_name
        card_template = "podcast.html.j2"

    svg = render_template(
        card_template,
        artwork_url=artwork_url,
        track_name=track_name,
        artist_name=artist_name,
        apple_icon=apple_icon,
        podcast_description=podcast_description,
        background_color="black",
    )

    return svg
