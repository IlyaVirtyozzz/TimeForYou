from constants import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    step_passage = db.Column(db.Integer, unique=False, nullable=False)
    step_room = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<User {} {} {} {} >".format(self.id, self.user_id, self.step_passage, self.step_room)


class TimeFlow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    time_start = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<TimeFlow {} {} {}>".format(self.id, self.user_id, self.time_start)


class ThingTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String, unique=False, nullable=False)
    time = db.Column(db.Integer, unique=False, nullable=False)
    last_time = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<ThingTime {} {} {} {} {} >".format(self.id, self.user_id, self.name, self.time, self.last_time)


def get_things_list(user_id):
    things_list = ThingTime.query.filter_by(user_id=user_id).all()
    return things_list


def add_new_thing(user_id, command):
    thing = ThingTime(user_id=user_id, name=command, time=0)
    db.session.add(thing)
    db.session.commit()


def add_new_user(user_id):
    user = User(user_id=user_id, step_passage=0, step_room=0)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    db.create_all()
