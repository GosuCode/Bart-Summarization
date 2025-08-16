from typing import List, Dict, Tuple
import re
import random
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import os
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    """Service for chunking long text into manageable pieces"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """
        Split text into chunks with overlap to preserve context
        
        Args:
            text: Input text to chunk
            chunk_size: Target chunk size in words
            overlap: Number of words to overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        words = text.split()
        word_count = len(words)
        
        # Dynamic chunking based on text length
        if word_count <= 100:
            # Very short text: create small chunks for variety
            chunk_size = max(20, word_count // 3)
            overlap = max(5, chunk_size // 3)
        elif word_count <= 300:
            # Short text: medium chunks
            chunk_size = max(50, word_count // 2)
            overlap = max(10, chunk_size // 4)
        elif word_count <= 800:
            # Medium text: smaller chunks for variety
            chunk_size = max(100, word_count // 3)
            overlap = max(20, chunk_size // 5)
        else:
            # Long text: use provided chunk_size and overlap
            pass
        
        logger.info(f"Text length: {word_count} words, Chunk size: {chunk_size}, Overlap: {overlap}")
        
        if word_count <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(words):
                break
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks

class FlashcardGenerator:
    """Service for generating flashcards from text chunks"""
    
    def __init__(self):
        # Models will be loaded lazily when needed
        pass
    
    def generate_question_answer_pair(self, text_chunk: str, question_index: int = 0) -> Dict[str, str]:
        """
        Generate a question-answer pair from text chunk
        
        Args:
            text_chunk: Text chunk to generate Q&A from
            question_index: Index of the question for variety
            
        Returns:
            Dictionary with question and answer
        """
        try:
            # Lazy load T5 models only when needed
            from services.model_manager import model_manager
            tokenizer, model = model_manager.get_t5_models()
            
            if not tokenizer or not model:
                # Fallback to basic generation
                return self._generate_basic_qa(text_chunk, question_index)
            
            # Prepare input for T5 model
            input_text = f"generate question: {text_chunk[:500]}"  # Limit input length
            
            inputs = tokenizer.encode(
                input_text, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True
            )
            
            # Generate question
            question_outputs = model.generate(
                inputs,
                max_length=64,
                num_beams=4,
                early_stopping=True,
                do_sample=True,
                temperature=0.7
            )
            
            question = tokenizer.decode(question_outputs[0], skip_special_tokens=True)
            
            # For now, use the chunk as answer (in production, you'd generate a proper answer)
            answer = text_chunk[:200] + "..." if len(text_chunk) > 200 else text_chunk
            
            return {
                "question": question,
                "answer": answer
            }
            
        except Exception as e:
            logger.error(f"Error generating Q&A with T5: {e}")
            return self._generate_basic_qa(text_chunk, question_index)
    
    def _generate_basic_qa(self, text_chunk: str, question_index: int = 0) -> Dict[str, str]:
        """Enhanced basic Q&A generation with variety"""
        sentences = re.split(r'[.!?]+', text_chunk)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return {
                "question": "What is the main topic of this text?",
                "answer": text_chunk[:100] + "..." if len(text_chunk) > 100 else text_chunk
            }
        
        # Use different question types for variety
        question_templates = [
            lambda s: f"What is the main point of: '{s[:80]}...'?",
            lambda s: f"What does this statement tell us about: '{s[:80]}...'?",
            lambda s: f"What is the key information in: '{s[:80]}...'?",
            lambda s: f"What concept is being explained in: '{s[:80]}...'?",
            lambda s: f"What is the primary focus of: '{s[:80]}...'?",
            lambda s: f"What can we learn from: '{s[:80]}...'?",
            lambda s: f"What does the text reveal about: '{s[:80]}...'?",
            lambda s: f"What is the significance of: '{s[:80]}...'?"
        ]
        
        # Pick sentence and template based on question index for variety
        sentence_index = question_index % len(sentences)
        sentence = sentences[sentence_index]
        template = question_templates[question_index % len(question_templates)]
        
        # Generate different types of questions based on index
        if question_index == 0:
            # First question: general overview
            question = template(sentence)
            answer = sentence
        elif question_index == 1:
            # Second question: focus on key concepts
            key_words = [w for w in sentence.split() if len(w) > 4]
            if key_words:
                question = f"What is the key concept mentioned in: '{sentence[:80]}...'?"
                answer = ' '.join(key_words[:3])
            else:
                question = template(sentence)
                answer = sentence
        else:
            # Third question: focus on process or mechanism
            if 'process' in sentence.lower() or 'how' in sentence.lower():
                question = f"How does the process described in: '{sentence[:80]}...' work?"
                answer = sentence
            else:
                question = template(sentence)
                answer = sentence
        
        # Truncate long answers
        if len(answer) > 150:
            words = answer.split()
            answer = ' '.join(words[:8]) + '...' if len(words) > 8 else answer
        
        return {
            "question": question,
            "answer": answer
        }
    
    def generate_flashcards(self, text: str, questions_per_chunk: int = 3) -> List[Dict[str, str]]:
        """
        Generate flashcards from long text using chunking strategy
        
        Args:
            text: Input text
            questions_per_chunk: Number of questions to generate per chunk
            
        Returns:
            List of flashcards
        """
        chunks = TextChunker.chunk_text(text)
        flashcards = []
        
        for chunk in chunks:
            for i in range(questions_per_chunk):
                qa_pair = self.generate_question_answer_pair(chunk, i)
                flashcards.append(qa_pair)
        
        return flashcards

class MCQGenerator:
    """Enhanced MCQ generator using flashcards as base"""
    
    def __init__(self):
        self.flashcard_generator = FlashcardGenerator()
    
    def generate_distractors(self, correct_answer: str, num_distractors: int = 3) -> List[str]:
        """
        Generate plausible distractors for MCQ options
        
        Args:
            correct_answer: The correct answer
            num_distractors: Number of distractors to generate
            
        Returns:
            List of distractor options
        """
        # This is a simplified distractor generation
        # In production, you'd use more sophisticated techniques
        
        distractors = []
        
        # Generate distractors based on answer type
        if self._is_date(correct_answer):
            distractors = self._generate_date_distractors(correct_answer, num_distractors)
        elif self._is_number(correct_answer):
            distractors = self._generate_number_distractors(correct_answer, num_distractors)
        elif self._is_name(correct_answer):
            distractors = self._generate_name_distractors(correct_answer, num_distractors)
        else:
            distractors = self._generate_generic_distractors(correct_answer, num_distractors)
        
        return distractors[:num_distractors]
    
    def _is_date(self, text: str) -> bool:
        """Check if text represents a date"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns)
    
    def _is_number(self, text: str) -> bool:
        """Check if text represents a number"""
        return re.match(r'^\d+(?:\.\d+)?$', text.strip()) is not None
    
    def _is_name(self, text: str) -> bool:
        """Check if text represents a person's name"""
        name_patterns = [
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+$'
        ]
        return any(re.match(pattern, text.strip()) for pattern in name_patterns)
    
    def _generate_date_distractors(self, correct_date: str, num_distractors: int) -> List[str]:
        """Generate date-based distractors"""
        # Simplified date manipulation
        distractors = [
            "Yesterday",
            "Tomorrow", 
            "Next week",
            "Last month",
            "Next year"
        ]
        return random.sample(distractors, min(num_distractors, len(distractors)))
    
    def _generate_number_distractors(self, correct_number: str, num_distractors: int) -> List[str]:
        """Generate number-based distractors"""
        try:
            num = float(correct_number)
            distractors = [
                str(num + 1),
                str(num - 1),
                str(num * 2),
                str(num / 2),
                str(int(num) + 10)
            ]
            return random.sample(distractors, min(num_distractors, len(distractors)))
        except:
            return ["0", "1", "100", "1000"]
    
    def _generate_name_distractors(self, correct_name: str, num_distractors: int) -> List[str]:
        """Generate name-based distractors"""
        distractors = [
            "John Smith",
            "Jane Doe",
            "Robert Johnson",
            "Maria Garcia",
            "David Wilson"
        ]
        return random.sample(distractors, min(num_distractors, len(distractors)))
    
    def _generate_generic_distractors(self, correct_answer: str, num_distractors: int) -> List[str]:
        """Generate generic distractors"""
        generic_distractors = [
            "None of the above",
            "All of the above",
            "Cannot be determined",
            "The information is insufficient",
            "This statement is false"
        ]
        return random.sample(generic_distractors, min(num_distractors, len(generic_distractors)))
    
    def generate_mcqs_from_flashcards(self, flashcards: List[Dict[str, str]]) -> List[Dict]:
        """
        Convert flashcards to MCQs by adding distractors
        
        Args:
            flashcards: List of flashcards with question-answer pairs
            
        Returns:
            List of MCQs with options and correct answer
        """
        mcqs = []
        
        for i, flashcard in enumerate(flashcards):
            correct_answer = flashcard["answer"]
            distractors = self.generate_distractors(correct_answer, 3)
            
            # Create options list
            options = [correct_answer] + distractors
            random.shuffle(options)
            
            # Find correct answer index
            correct_index = options.index(correct_answer)
            
            mcq = {
                "id": i + 1,
                "question": flashcard["question"],
                "options": options,
                "correct_answer_index": correct_index,
                "correct_answer": correct_answer,
                "explanation": f"Based on the text: {correct_answer[:100]}..."
            }
            
            mcqs.append(mcq)
        
        return mcqs
    
    def generate_mcqs(self, text: str, questions_per_chunk: int = 3) -> List[Dict]:
        """
        Generate MCQs from long text using chunking strategy
        
        Args:
            text: Input text
            questions_per_chunk: Number of questions to generate per chunk
            
        Returns:
            List of MCQs
        """
        # First generate flashcards
        flashcards = self.flashcard_generator.generate_flashcards(text, questions_per_chunk)
        
        # Convert to MCQs
        mcqs = self.generate_mcqs_from_flashcards(flashcards)
        
        return mcqs
