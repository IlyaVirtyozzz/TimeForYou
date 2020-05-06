# from flask import Flask, request
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqldatabase22.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'key?'
# db = SQLAlchemy(app)
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, unique=False, nullable=False)
#
#
# def add_new_user(user_id):
#     user = User(user_id=user_id)
#     db.session.add(user)
#
#     return user
#
#
# if __name__ == '__main__':
#     # db.create_all()
#     user = add_new_user(22)
#     print(user.user_id)
#     db.session.commit()

print(int("000"))