from flask import Flask, render_template
from waitress import serve
app = Flask(__name__,template_folder='templates')


@app.route('/')
def main():
    return render_template("main.html",link = 'https://aniqit.com/serial/35594/ff4cd725c2bc6eb0ff28e8f387319950/720p',title = 'Для тебя, Бессмертный', views = 1,id=1,img_link='https://st.kp.yandex.net/images/film_big/1448465.jpg',page_link = 'https://bot.animepoint.cc/id/serial-35594')


if __name__ == "__main__":
    serve(app,host = '127.0.0.1',port=5000)