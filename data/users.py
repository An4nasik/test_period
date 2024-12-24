import sqlalchemy
from .db_session import SqlAlchemyBase



class Meet(SqlAlchemyBase):

    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    meeting_name = sqlalchemy.Column(sqlalchemy.String)
    meeting_code = sqlalchemy.Column(sqlalchemy.String)
    meet_url = sqlalchemy.Column(sqlalchemy.String)



    def __repr__(self):
        return f"<Messages> {self.id}, {self.meet_url}"


