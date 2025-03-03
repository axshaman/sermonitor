from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



subs = db.Table('subs',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('words_id', db.Integer, db.ForeignKey('keywords.id')),
)


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    patronymic = db.Column(db.String(50), nullable=True)
    date_of_birth = db.Column(db.Date(), nullable=True)
    telegram_id = db.Column(db.Numeric(), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.Numeric(), unique=True, nullable=False)
    phone2 = db.Column(db.String(11), nullable=True, unique=True)
    city = db.Column(db.String(30), nullable=False)
    city2 = db.Column(db.String(30), nullable=True)
    city3 = db.Column(db.String(30), nullable=True)
    link = db.Column(db.String(100), nullable=True)
    link2 = db.Column(db.String(100), nullable=True)
    link3 = db.Column(db.String(100), nullable=True)
    link4 = db.Column(db.String(100), nullable=True)
    link5 = db.Column(db.String(100), nullable=True)

    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def find_by_telegram_id(cls, telegram_id):
        user = cls.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            return None
        return user

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class KeyWords(db.Model):
    __tablename__ = 'keywords'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    users = db.relationship('Users', secondary='subs', backref=db.backref('word_user', lazy='dynamic'))


    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get_word_by_name(cls, name:str):
        word = cls.query.filter_by(name=name).first()
        if not word:
            return None
        return word


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

# class Subs(db.Model):
#     __tablename__ = 'subs'
#     __table_args__ = {'extend_existing': True}

#     id = db.Column(db.Integer, primary_key=True)
#     users_id=db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
#     words_id=db.Column('words_id', db.Integer, db.ForeignKey('keywords.id'))
#     user = db.relationship(Users, backref=db.backref("subs", cascade="all, delete-orphan"))
#     product = db.relationship(KeyWords, backref=db.backref("subs", cascade="all, delete-orphan"))

    # def __init__(self):
        
