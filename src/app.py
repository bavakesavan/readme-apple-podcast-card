import logging
from dotenv import load_dotenv
from flask import Flask, Response, request
from podcast_card import get_podcast_card

logging.basicConfig(level=logging.INFO)


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
