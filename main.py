import random
from rooms import UsersThing, Menu, CreateThing
from database import User, TimeFlow, ThingTime, add_new_user


class Main():
    def __init__(self, res, req, db):
        self.res = res
        self.db = db
        self.req = req
        self.user_id = req['session']['user_id']
        self.payload = False
        self.markup = self.req["request"].get("markup")
        if self.markup:
            self.dangerous = self.markup.get("dangerous_context")
        else:
            self.dangerous = False
        self.res['response']['buttons'] = []
        self.res['response']['text'] = ''
        self.res['response']['tts'] = ''

    def get_user(self):
        user = self.db.session.query(User).filter_by(user_id=self.user_id).first()
        return user

    def get_timeflow(self):
        timeflow = self.db.session.query(TimeFlow).filter_by(user_id=self.user_id).first()
        return timeflow

    def create_user(self):
        add_new_user(self.user_id)
        user = self.db.session.query(User).filter_by(user_id=self.user_id).first()
        return user

    def start(self):
        user = self.get_user()
        timeflow = self.get_timeflow()
        if not user:
            user = self.create_user()
        if self.req['session']['new']:

            menu = Menu(self.res, self.req, self.db, user,timeflow, True)
            menu.start()
            self.res = menu.get_res()
        else:
            menu = Menu(self.res, self.req, self.db, user,timeflow, False)
            menu.tree()
            self.res = menu.get_res()

    def get_response(self):
        return self.res
