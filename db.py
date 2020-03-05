from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

engine = create_engine('sqlite:///currencies.db')
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(80))
    username = Column(String(80))
    currency = relationship('Currency', backref='currency')


class Currency(Base):
    __tablename__ = 'currencies'

    id = Column(Integer, primary_key=True)
    currencies = Column(String(1000), nullable=False)
    chat_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

