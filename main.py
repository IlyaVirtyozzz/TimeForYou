from rooms import UsersThing, Menu, CreateThing
from database import User, TimeFlow, ThingTime, add_new_user
from constants import sessionSettings


class Main():
    def __init__(self, res, req, db):
        self.res = res
        self.db = db
        self.req = req
        self.user_id = req['session']['user_id']
        self.payload = False
        if sessionSettings.get(self.user_id):
            self.sessionSettings = sessionSettings
        else:
            self.sessionSettings = sessionSettings
            self.sessionSettings[self.user_id] = {"buttons": [], "text": '', "tts": ''}

        self.res['response']['buttons'] = []
        self.res['response']['text'] = ''
        self.res['response']['tts'] = ''

    def get_user(self):
        user = self.db.session.query(User).filter_by(user_id=self.user_id).first()
        return user

    def get_timeflow(self, user):
        timeflow = self.db.session.query(TimeFlow).filter_by(user_id=user.id).first()

        return timeflow

    def create_user(self):
        add_new_user(self.user_id)
        user = self.db.session.query(User).filter_by(user_id=self.user_id).first()

        return user

    def start(self):
        user = self.get_user()
        new_user = False
        if not user:
            user = self.create_user()
            new_user = True
        timeflow = self.get_timeflow(user)
        if self.req['session']['new']:
            menu = Menu(self.res, self.req, self.db, user, timeflow, True, new_user, user.help_actions)
            menu.start()
            self.res = menu.get_res()
        else:
            menu = Menu(self.res, self.req, self.db, user, timeflow, False, new_user, user.help_actions)
            menu.tree()
            self.res = menu.get_res()

        self.sessionSettings[self.user_id]["buttons"] = self.res['response']['buttons']
        self.sessionSettings[self.user_id]["text"] = self.res['response']['text']
        self.sessionSettings[self.user_id]["tts"] = self.res['response']['tts']

    def get_response(self):

        return self.res
