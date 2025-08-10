from typing import List, Dict
import re
import random

class MCQGenerator:
    """Service for generating Multiple Choice Questions from text"""
    
    @staticmethod
    def generate_mcq_from_text(text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate MCQ questions from given text
        
        Args:
            text: Input text to generate questions from
            num_questions: Number of questions to generate
            
        Returns:
            List of MCQ questions with options and correct answer
        """
        # This is a simplified implementation
        # In a real scenario, you'd use a more sophisticated approach
        # like fine-tuning the BART model for question generation
        
        questions = []
        
        # Split text into sentences for question generation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Limit to available sentences
        num_questions = min(num_questions, len(sentences))
        
        for i in range(num_questions):
            if i >= len(sentences):
                break
                
            sentence = sentences[i]
            
            # Generate a simple question (this is a placeholder)
            # In practice, you'd use the BART model to generate proper questions
            question_text = f"What is the main point of the following statement: '{sentence[:100]}...'?"
            
            # Generate options (simplified - in practice use the model)
            correct_answer = "The statement provides information about the topic."
            incorrect_options = [
                "The statement is completely false.",
                "The statement has no meaning.",
                "The statement is irrelevant."
            ]
            
            # Shuffle options
            all_options = [correct_answer] + incorrect_options
            random.shuffle(all_options)
            
            # Find correct answer index
            correct_index = all_options.index(correct_answer)
            
            questions.append({
                "id": i + 1,
                "question": question_text,
                "options": all_options,
                "correct_answer_index": correct_index,
                "correct_answer": correct_answer,
                "explanation": f"This question is based on the text: '{sentence[:100]}...'"
            })
        
        return questions
    
    @staticmethod
    def generate_mcq_with_bart(text: str, num_questions: int = 5, model=None, tokenizer=None) -> List[Dict]:
        """
        Generate MCQ using BART model (placeholder for future implementation)
        
        Args:
            text: Input text
            num_questions: Number of questions to generate
            model: BART model instance
            tokenizer: BART tokenizer instance
            
        Returns:
            List of MCQ questions
        """
        # This would be the actual implementation using the BART model
        # For now, return the basic implementation
        return MCQGenerator.generate_mcq_from_text(text, num_questions)
