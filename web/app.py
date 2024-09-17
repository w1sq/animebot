import os
import logging
from dotenv import load_dotenv

from waitress import serve
from flask import Flask, render_template

from db_data import db_session
from db_data.__all_models import Anime


load_dotenv(dotenv_path=".env")
app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
logging.basicConfig(level=logging.INFO, filename="applogs.log")
db_session.global_init()


@app.route("/id/<id>")
def main(id):
    db_sess = db_session.create_session()
    anime = db_sess.query(Anime).filter(Anime.kodik_id == id).first()
    anime.views += 1
    db_sess.commit()
    link = anime.iframe_link
    title = anime.title
    img_link = anime.poster_link
    page_link = f"https://bot.animepoint.cc/id/{id}"
    return render_template(
        "main.html",
        link=link,
        title=title,
        views=anime.views,
        id=id,
        img_link=img_link,
        page_link=page_link,
    )


@app.errorhandler(404)
def pageNotFound(error):
    return render_template("error404.html")


if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5000)
