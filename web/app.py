from flask import Flask, render_template, request, flash, redirect, abort
import requests
import logging
from random import randint

app = Flask(__name__,template_folder='templates')
app.config["SECRET_KEY"] = "anime"
logging.basicConfig(level=logging.INFO, filename='applogs.log')

@app.route('/<id>')
def main(id):
    result = requests.get(f'https://kodikapi.com/search?token=7f129085d2f372833fcc5e2116e4d0a4&id={id}').json()
    link = result['results'][0]['link']
    title = result['results'][0]['title']
    views = randint(100,1000)
    return render_template("main.html",link = link,title = title, views = views)


if __name__ == "__main__":
    app.run()
