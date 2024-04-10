from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', backref='hero', cascade='all, delete-orphan')

    # add serialization rules
    serialize_rules = ('-hero_powers.hero',)
    #serialize_only = ()

    def serialize(self):
        return {"id": self.id, "name": self.name, "super_name": self.super_name}

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', backref='power', cascade='all, delete-orphan')

    # add serialization rules
    serialize_rules = ('-hero_powers.power',)

    def serialize(self):
        return {"description": self.description, "id": self.id, "name": self.name}


    # add validation
    @validates('description')
    def validate_power(self, key, string):
        if not string:
            raise ValueError("Description must be present")
        elif len(string) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return string

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))


    # add serialization rules
    serialize_rules = ('-power.hero_powers', '-hero.hero_powers',)


    def serialize(self):
        return {"strength": self.strength, "power_id": self.power_id, "hero_id": self.hero_id}



    # add validation
    @validates('strength')
    def validate_strength(self, key, strength):
        #if strength != 'Strong' or strength != 'Weak' or strength != 'Average':
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength myst be Strong, Weak or Average")
        return strength 


    def __repr__(self):
        return f'<HeroPower {self.id}>'