import os
import google.generativeai as genai
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini API client initialized")
    
    def generate_flashcards(self, text: str, total_questions: int = 3) -> Dict[str, Any]:
        """Generate flashcards using Gemini API"""
        if not self.client:
            raise Exception("Gemini API client not available. Check GEMINI_API_KEY environment variable.")
        
        try:
            prompt = f"""
            You are an expert educator creating flashcards. Generate exactly {total_questions} high-quality flashcards from this text.
            
            Requirements:
            - Questions should test understanding, not just recall
            - Answers should be concise but complete
            - Vary question types (what, why, how, compare, etc.)
            - Focus on key concepts and important details
            - Generate EXACTLY {total_questions} flashcards, no more, no less
            
            Text: {text[:3000]}  # Limit text length for better focus
            
            Return ONLY valid JSON in this exact format:
            {{
                "flashcards": [
                    {{"question": "What is the main concept discussed in the first paragraph?", "answer": "The main concept is..."}},
                    {{"question": "Why is this important?", "answer": "This is important because..."}}
                ]
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]  # Remove markdown code blocks
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            try:
                import json
                result = json.loads(response_text)
                flashcards = result.get("flashcards", [])
                
                # Validate response quality
                if not flashcards or len(flashcards) < total_questions:
                    raise Exception(f"Gemini returned insufficient flashcards. Expected {total_questions}, got {len(flashcards)}")
                
                return {
                    "flashcards": flashcards,
                    "total_flashcards": len(flashcards),
                    "text_length": len(text),
                    "processing_method": "gemini_api"
                }
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse Gemini response as JSON: {e}. Response: {response_text[:200]}")
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise Exception(f"Gemini API failed: {str(e)}")
    
    def generate_mcqs(self, text: str, total_questions: int = 3) -> Dict[str, Any]:
        """Generate MCQs using Gemini API"""
        if not self.client:
            raise Exception("Gemini API client not available. Check GEMINI_API_KEY environment variable.")
        
        try:
            prompt = f"""
            You are an expert educator creating multiple choice questions. Generate exactly {total_questions} high-quality MCQs from this text.
            
            Requirements:
            - Questions should test understanding, not just recall
            - All 4 options should be plausible but only one correct
            - Correct answer should be clearly right
            - Wrong options should be reasonable distractors
            - Focus on key concepts and important details
            - Generate EXACTLY {total_questions} MCQs, no more, no less
            
            Text: {text[:3000]}  # Limit text length for better focus
            
            Return ONLY valid JSON in this exact format:
            {{
                "mcqs": [
                    {{
                        "question": "What is the main concept discussed?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "correct_answer_index": 0
                    }}
                ]
            }}
            """
            
            response = self.client.generate_content(prompt)
            
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]  # Remove markdown code blocks
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            try:
                import json
                result = json.loads(response_text)
                mcqs = result.get("mcqs", [])
                
                # Validate response quality
                if not mcqs or len(mcqs) < total_questions:
                    raise Exception(f"Gemini returned insufficient MCQs. Expected {total_questions}, got {len(mcqs)}")
                
                return {
                    "mcqs": mcqs,
                    "total_mcqs": len(mcqs),
                    "text_length": len(text),
                    "processing_method": "gemini_api"
                }
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse Gemini response as JSON: {e}. Response: {response_text[:200]}")
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise Exception(f"Gemini API failed: {str(e)}")
    
    # Remove fallback methods - they're no longer needed

# Global instance
gemini_service = GeminiService()
