from sqlalchemy import create_engine, Column, Integer, String,ForeignKey
from sqlalchemy.orm import sessionmaker , declarative_base, relationship
import uuid

DB_URL = "sqlite:///./shortner.db"

Engine = create_engine(DB_URL, connect_args = {'check_same_thread': False})

SessionLocal = sessionmaker(bind=Engine, autocommit = False, autoflush = False)

Base = declarative_base()

class UserAuth(Base):
    __tablename__ = 'Users'
    id =  Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique = True)
    password = Column(String, nullable = False)
    urlShorner = relationship("urlShorner", back_populates="user", cascade="all, delete")
    qrs = relationship("UsersQr", back_populates="user", cascade="all, delete")


class urlShorner(Base):
    __tablename__ = 'Urls'
    id = Column(Integer, primary_key = True, index = True)
    originalUrl = Column(String, nullable = False)
    shortenUrl = Column(String, unique = True)
    clicks = Column(Integer, default=0)
    user_id = Column(String, ForeignKey("Users.id"))
    user = relationship("UserAuth", back_populates="urlShorner")

class UsersQr(Base):
    __tablename__ = "users_qr"

    id = Column(Integer, primary_key=True, index=True)
    qr_url = Column(String, nullable=False)
    logo_name = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("Users.id")) 
    user = relationship("UserAuth", back_populates="qrs")

Base.metadata.create_all(bind=Engine)
