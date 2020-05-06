from constants import db, time, datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    step_passage = db.Column(db.Integer, unique=False, nullable=False)
    step_room = db.Column(db.Integer, unique=False, nullable=False)
    thing_id = db.Column(db.Integer, unique=False, nullable=True)
    help_actions = db.Column(db.Boolean, unique=False, )

    def __repr__(self):
        return "<User {} {} {} {} {} {}>".format(self.id, self.user_id, self.step_passage, self.step_room,
                                                 self.thing_id, self.help_actions)


class TimeFlow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    thing_id = db.Column(db.Integer, unique=False, nullable=False)
    time_start = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<TimeFlow {} {} {}>".format(self.id, self.user_id, self.time_start)


class ThingTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String, unique=False, nullable=False)
    time = db.Column(db.Integer, unique=False, nullable=False)
    last_time = db.Column(db.Integer, unique=False, nullable=False)
    res_last_time = db.Column(db.Integer, unique=False, nullable=False)
    last_data = db.Column(db.DateTime, unique=False, nullable=False)

    def __repr__(self):
        return "<ThingTime {} {} {} {} {} {} {}>".format(self.id, self.user_id, self.name, self.time, self.res_last_time,
                                                       self.last_time, self.last_data)


def get_things_list(user_id):
    things_list = ThingTime.query.filter_by(user_id=user_id).order_by(ThingTime.last_data).all()[::-1]

    return things_list


def add_thing_flow(user_id, thing_id):
    thing = TimeFlow(user_id=user_id, thing_id=thing_id, time_start=time.time())
    db.session.add(thing)
    db.session.commit()


def refresh_last_time(thing,date_time):
    thing.last_data = date_time
    db.session.commit()


def add_new_thing(user_id, command):
    thing = ThingTime(user_id=user_id, name=command, time=0, last_time=0, res_last_time=0,
                      last_data=datetime.datetime.today())
    db.session.add(thing)
    db.session.commit()
    return thing


def add_new_user(user_id):
    user = User(user_id=user_id, step_passage=0, step_room=0, help_actions=True)
    db.session.add(user)
    db.session.commit()
    return user


if __name__ == '__main__':
    # add_new_thing(23231, "2122222222222222222222222222222222222")
    # print(get_things_list(23231))
    db.create_all()
