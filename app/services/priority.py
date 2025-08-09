from typing import List, Dict
from collections import defaultdict

# Mock dataset
MOCK_DATA = [
    {"topic": "Networking", "marks": 10, "year": 2024},
    {"topic": "Networking", "marks": 15, "year": 2023},
    {"topic": "DB Normalization", "marks": 12, "year": 2024},
    {"topic": "DB Normalization", "marks": 8, "year": 2022},
    {"topic": "Image Compression", "marks": 20, "year": 2021},
    {"topic": "Image Compression", "marks": 10, "year": 2024},
    {"topic": "Algorithms", "marks": 5, "year": 2024}
]

def calculate_priority_scores() -> List[Dict]:
    """
    Calculate priority scores for topics using weighted formula:
    priority_score = (frequency * 0.6) + (avg_marks_per_year * 0.4)
    """
    # Group by topic
    topic_data = defaultdict(list)
    for item in MOCK_DATA:
        topic_data[item["topic"]].append({"marks": item["marks"], "year": item["year"]})
    
    results = []
    
    for topic, data in topic_data.items():
        # Calculate frequency (number of occurrences)
        frequency = len(data)
        
        # Calculate average marks per year
        total_marks = sum(item["marks"] for item in data)
        avg_marks_per_year = total_marks / frequency
        
        # Calculate priority score using weighted formula
        priority_score = (frequency * 0.6) + (avg_marks_per_year * 0.4)
        
        results.append({
            "topic": topic,
            "frequency": frequency,
            "avg_marks_per_year": round(avg_marks_per_year, 2),
            "priority_score": round(priority_score, 3)
        })
    
    # Sort by priority_score (descending)
    results.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return results
