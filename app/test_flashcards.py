#!/usr/bin/env python3
"""
Test script for flashcards and MCQ service
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/flashcards"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    print("\n🔍 Testing supported formats...")
    try:
        response = requests.get(f"{BASE_URL}/supported-formats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Supported formats failed: {e}")
        return False

def test_flashcards_generation():
    """Test flashcards generation"""
    print("\n🔍 Testing flashcards generation...")
    
    sample_text = """
    Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. 
    Some of the activities computers with artificial intelligence are designed for include speech recognition, learning, planning, and problem solving.
    
    Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. 
    It focuses on the development of computer programs that can access data and use it to learn for themselves.
    
    Deep Learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns. 
    It has been particularly successful in areas like image recognition, natural language processing, and speech recognition.
    
    Natural Language Processing (NLP) is a field of AI that gives machines the ability to read, understand, and derive meaning from human languages. 
    It combines computational linguistics with statistical, machine learning, and deep learning models.
    """
    
    payload = {
        "text": sample_text,
        "questions_per_chunk": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/flashcards", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated {result['total_flashcards']} flashcards")
            print(f"📊 Text length: {result['text_length']} characters")
            print(f"🔢 Chunks processed: {result['chunks_processed']}")
            print(f"⏱️ Processing time: {result['processing_time']}s")
            
            # Show first flashcard
            if result['flashcards']:
                first_card = result['flashcards'][0]
                print(f"\n📝 Sample flashcard:")
                print(f"   Q: {first_card['question']}")
                print(f"   A: {first_card['answer'][:100]}...")
            
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Flashcards generation failed: {e}")
        return False

def test_mcq_generation():
    """Test MCQ generation"""
    print("\n🔍 Testing MCQ generation...")
    
    sample_text = """
    Climate change refers to long-term shifts in global weather patterns and average temperatures. 
    The Earth's climate has changed throughout history, but the current warming trend is of particular significance because it is proceeding at an unprecedented rate.
    
    Greenhouse gases, such as carbon dioxide, methane, and water vapor, trap heat in the Earth's atmosphere. 
    Human activities, particularly the burning of fossil fuels, have increased the concentration of these gases, leading to enhanced greenhouse effect.
    
    The consequences of climate change include rising sea levels, more frequent and severe weather events, shifts in precipitation patterns, and impacts on ecosystems and biodiversity.
    """
    
    payload = {
        "text": sample_text,
        "questions_per_chunk": 2
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mcqs", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated {result['total_mcqs']} MCQs")
            print(f"📊 Text length: {result['text_length']} characters")
            print(f"🔢 Chunks processed: {result['chunks_processed']}")
            print(f"⏱️ Processing time: {result['processing_time']}s")
            
            # Show first MCQ
            if result['mcqs']:
                first_mcq = result['mcqs'][0]
                print(f"\n📝 Sample MCQ:")
                print(f"   Q: {first_mcq['question']}")
                print(f"   Options:")
                for i, option in enumerate(first_mcq['options']):
                    marker = "✅" if i == first_mcq['correct_answer_index'] else "  "
                    print(f"     {marker} {option}")
                print(f"   Correct: {first_mcq['correct_answer']}")
            
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MCQ generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Flashcards and MCQ Service Tests\n")
    
    tests = [
        test_health_check,
        test_supported_formats,
        test_flashcards_generation,
        test_mcq_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 50)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Service is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the service logs.")

if __name__ == "__main__":
    main()
