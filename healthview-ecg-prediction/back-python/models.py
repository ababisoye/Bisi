from sqlalchemy import Column, Integer
from database import Base

class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, nullable=False)
