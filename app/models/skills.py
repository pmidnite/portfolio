from app.utilities.database import db
from app.models.about import About


class Skills(db.Model):
    '''
    Skill DB Structure Model
    '''
    __tablename__ = "skill"

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(120), unique=True, nullable=False)
    skill_logo = db.Column(db.String(300), nullable=False)


class MappedSkills(db.Model):
    '''
    Skill DB Structure Model
    '''
    __tablename__ = "mapped_skill"

    id = db.Column(db.Integer, primary_key=True)
    about_id = db.Column(db.ForeignKey(About.id))
    skill_id = db.Column(db.ForeignKey(Skills.id))
    __table_args__ = (db.UniqueConstraint(about_id, skill_id, name="about_skill_uk"),)
