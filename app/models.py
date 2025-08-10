from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from db import Base

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False, index=True)
    marks = Column(Float, nullable=False)
    year = Column(Integer, nullable=False, index=True)
    subject_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Question(id={self.id}, topic='{self.topic}', marks={self.marks}, year={self.year}, subject_id={self.subject_id})>"
