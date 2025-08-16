import logging
import torch
import os
from typing import Optional, Tuple
from transformers import BartForConditionalGeneration, BartTokenizerFast, T5ForConditionalGeneration, T5Tokenizer

logger = logging.getLogger(__name__)

class ModelManager:
    """Singleton model manager to prevent multiple model instances"""
    
    _instance = None
    _bart_model = None
    _bart_tokenizer = None
    _t5_model = None
    _t5_tokenizer = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._device = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
            self._initialized = True
    
    def get_bart_models(self) -> Tuple[Optional[BartTokenizerFast], Optional[BartForConditionalGeneration]]:
        """Lazy load BART models only when needed"""
        if self._bart_model is None or self._bart_tokenizer is None:
            try:
                logger.info("🔄 Loading BART model from Hugging Face...")
                self._bart_tokenizer = BartTokenizerFast.from_pretrained("sshleifer/distilbart-cnn-12-6")
                self._bart_model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6").to(self._device)
                self._bart_model.eval()
                logger.info(f"✅ BART model: LOADED on {self._device}")
            except Exception as e:
                logger.error(f"❌ BART model: FAILED to load - {e}")
                self._bart_model = None
                self._bart_tokenizer = None
        
        return self._bart_tokenizer, self._bart_model
    
    def get_t5_models(self) -> Tuple[Optional[T5Tokenizer], Optional[T5ForConditionalGeneration]]:
        """Lazy load T5 models only when needed"""
        if self._t5_model is None or self._t5_tokenizer is None:
            try:
                logger.info("🔄 Loading T5 model from Hugging Face...")
                model_name = "valhalla/t5-small-qg-hl"
                self._t5_tokenizer = T5Tokenizer.from_pretrained(model_name)
                self._t5_model = T5ForConditionalGeneration.from_pretrained(model_name).to(self._device)
                self._t5_model.eval()
                logger.info(f"✅ T5 model: LOADED on {self._device}")
            except Exception as e:
                logger.error(f"❌ T5 model: FAILED to load - {e}")
                self._t5_model = None
                self._t5_tokenizer = None
        
        return self._t5_tokenizer, self._t5_model
    
    def unload_models(self):
        """Unload models to free memory (useful for testing)"""
        if self._bart_model is not None:
            del self._bart_model
            self._bart_model = None
        if self._t5_model is not None:
            del self._t5_model
            self._t5_model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("🧹 Models unloaded and memory freed")
    
    def get_memory_info(self) -> dict:
        """Get memory usage information"""
        info = {
            "device": self._device,
            "bart_loaded": self._bart_model is not None,
            "t5_loaded": self._t5_model is not None
        }
        
        if torch.cuda.is_available():
            info["cuda_memory_allocated"] = f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB"
            info["cuda_memory_reserved"] = f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB"
        
        return info

# Global instance
model_manager = ModelManager()

