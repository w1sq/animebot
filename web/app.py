from flask import Flask, render_template
import requests
import logging
from db_data import db_session
from db_data.__all_models import Anime

app = Flask(__name__,template_folder='templates')
app.config["SECRET_KEY"] = "anime"
logging.basicConfig(level=logging.INFO, filename='applogs.log')
db_session.global_init()


@app.route('/id/<id>')
def main(id):
    db_sess = db_session.create_session()
    anime = db_sess.query(Anime).filter(Anime.kodik_id == id).first()
    anime.views += 1
    db_sess.commit()
    link = anime.iframe_link
    title = anime.title
    img_link = anime.poster_link
    page_link = f'http://animepoints.cc/{id}'
    return render_template("main.html",link = link,title = title, views = anime.views,id=id,img_link=img_link,page_link = page_link)

if __name__ == "__main__":
    app.run()
