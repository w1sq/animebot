import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    conn_str = 'postgresql+psycopg2://bot:Iamgood2005@127.0.0.1/bot'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()