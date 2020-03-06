from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json, logging


def read_json():
    with open("mysite/info.json", "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    return data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqldatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key?'
db = SQLAlchemy(app)
if __name__ == '__main__':
    info = read_json()
