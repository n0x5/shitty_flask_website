try:
    from __main__ import app
except:
    from app import app
from flask import jsonify

@app.route("/apiv2/moviegenres")
def movapi2(genres=None):
    genrelist = ["romance", "comedy", "animation", "mystery", "documentary", "crime", "family", "sport",
            "biography", "history", "western", "sci-fi", "horror", "adventure", "drama", "fantasy", "thriller", "action"]
    genres = [jsonify(genre=item.title()) for item in genrelist]
    return str(genres)