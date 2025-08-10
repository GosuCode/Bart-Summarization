from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Question
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/learnmate")

# Create engine for PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Sample data: list of questions with topic, marks, year, subject_id
    questions = [
        # Subject 1 - Computer Science
        {"topic": "Networking", "marks": 10, "year": 2024, "subject_id": 1},
        {"topic": "Networking", "marks": 15, "year": 2023, "subject_id": 1},
        {"topic": "DB Normalization", "marks": 12, "year": 2024, "subject_id": 1},
        {"topic": "DB Normalization", "marks": 8, "year": 2022, "subject_id": 1},
        {"topic": "Image Compression", "marks": 20, "year": 2021, "subject_id": 1},
        {"topic": "Image Compression", "marks": 10, "year": 2024, "subject_id": 1},
        {"topic": "Algorithms", "marks": 5, "year": 2024, "subject_id": 1},
        
        # Subject 2 - Mathematics
        {"topic": "Calculus", "marks": 25, "year": 2024, "subject_id": 2},
        {"topic": "Calculus", "marks": 20, "year": 2023, "subject_id": 2},
        {"topic": "Linear Algebra", "marks": 15, "year": 2024, "subject_id": 2},
        {"topic": "Linear Algebra", "marks": 18, "year": 2022, "subject_id": 2},
        
        # Subject 5 - Physics
        {"topic": "Mechanics", "marks": 30, "year": 2024, "subject_id": 5},
        {"topic": "Mechanics", "marks": 25, "year": 2023, "subject_id": 5},
        {"topic": "Thermodynamics", "marks": 22, "year": 2024, "subject_id": 5},
    ]

    for q in questions:
        question = Question(
            topic=q["topic"],
            marks=q["marks"],
            year=q["year"],
            subject_id=q["subject_id"],
        )
        session.add(question)

    session.commit()
    session.close()
    print("Database seeded with sample questions for multiple subjects.")

if __name__ == "__main__":
    seed_data()
