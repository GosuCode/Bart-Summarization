from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Question

# Replace with your actual database URL
DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Sample data: list of questions with topic, marks, year, subject_id
    questions = [
        {"topic": "Networking", "marks": 10, "year": 2024, "subject_id": 1},
        {"topic": "Networking", "marks": 15, "year": 2023, "subject_id": 1},
        {"topic": "DB Normalization", "marks": 12, "year": 2024, "subject_id": 1},
        {"topic": "DB Normalization", "marks": 8, "year": 2022, "subject_id": 1},
        {"topic": "Image Compression", "marks": 20, "year": 2021, "subject_id": 1},
        {"topic": "Image Compression", "marks": 10, "year": 2024, "subject_id": 1},
        {"topic": "Algorithms", "marks": 5, "year": 2024, "subject_id": 1},
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
    print("Database seeded with sample questions.")

if __name__ == "__main__":
    seed_data()
