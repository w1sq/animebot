import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin 

favorites_table = sqlalchemy.Table('user_anime', SqlAlchemyBase.metadata,
    sqlalchemy.Column('left_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('right_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('anime.id'))
)
class Users(SqlAlchemyBase):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    notifications = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    favorites = orm.relationship("Anime",
                    secondary=favorites_table,back_populates='user')

    def __str__(self):
        return str(self.id)
    
    def __repr__(self):
        return str(self.id)
class Anime(SqlAlchemyBase,SerializerMixin):
    __tablename__ = "anime"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    kodik_id = sqlalchemy.Column(sqlalchemy.String,nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String,nullable=False)
    title_orig = sqlalchemy.Column(sqlalchemy.String)
    iframe_link = sqlalchemy.Column(sqlalchemy.String,nullable=False)
    views = sqlalchemy.Column(sqlalchemy.Integer,default=0)
    status = sqlalchemy.Column(sqlalchemy.String,nullable=False)
    poster_link = sqlalchemy.Column(sqlalchemy.String,default=None)
    imdb_rating = sqlalchemy.Column(sqlalchemy.String)
    kinopoisk_rating = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.String)
    genres = sqlalchemy.Column(sqlalchemy.String)
    actors = sqlalchemy.Column(sqlalchemy.String)
    directors = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relationship("Users",
                    secondary=favorites_table,back_populates='favorites')
    

    def __str__(self):
        return self.status
    
    def __repr__(self):
        return self.status


    def to_message(self):
                return f'''
{self.title}
{self.title_orig}
<u>{self.imdb_rating} {self.kinopoisk_rating} </u>

{self.year}{self.genres}{self.actors}{self.directors}

{self.description}
'''