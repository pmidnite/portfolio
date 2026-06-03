from app.models.base import BaseModel
from app.utilities.database import db
from app.models.about import About


class Skills(BaseModel):
    '''
    Skill DB Structure Model
    '''
    __tablename__ = "skill"

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(120), unique=True, nullable=False)
    skill_logo = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Skill {self.skill_name}>"

    def to_dict(self):
        return {
            "Skill Name": self.skill_name,
            "Skill Logo": self.skill_logo
        }


class MappedSkills(BaseModel):
    '''
    Mapped Skill DB Structure Model
    '''
    __tablename__ = "mapped_skill"

    id = db.Column(db.Integer, primary_key=True)
    about_id = db.Column(db.ForeignKey(About.id))
    skill_id = db.Column(db.ForeignKey(Skills.id))
    __table_args__ = (db.UniqueConstraint(about_id, skill_id, name="about_skill_uk"),)

    def __repr__(self):
        return f"<MappedSkills about_id={self.about_id}, skill_id={self.skill_id}>"

    def to_dict(self):
        return {
            "about_id": self.about_id,
            "skill_id": self.skill_id
        }
