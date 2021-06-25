from db_data import db_session
from db_data.__all_models import Users, Anime

db_session.global_init()

db_sess = db_session.create_session()
print(db_sess.query(Anime).all())