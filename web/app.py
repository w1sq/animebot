from flask import Flask, render_template, request, flash, redirect, abort
import requests
import logging
from random import randint
import sqlite3

app = Flask(__name__,template_folder='templates')
app.config["SECRET_KEY"] = "anime"
logging.basicConfig(level=logging.INFO, filename='applogs.log')
con = sqlite3.connect("static/views.db",check_same_thread=False)
cur = con.cursor()


@app.route('/<id>')
def main(id):
    try:
        views = cur.execute("""SELECT views FROM views WHERE kodik_id = ?""",(id,)).fetchone()[0]
        views +=1
        cur.execute("""UPDATE views SET views = ? WHERE kodik_id = ?""",(views,id,))
    except Exception:
        views = 1 
        cur.execute("""INSERT INTO views VALUES (?,?)""",(id,views,))
    result = requests.get(f'https://kodikapi.com/search?token=7f129085d2f372833fcc5e2116e4d0a4&id={id}').json()
    link = result['results'][0]['link']
    title = result['results'][0]['title']
    return render_template("main.html",link = link,title = title, views = views)
if __name__ == "__main__":
    app.run()
