import logging
import torch
import os
from transformers import BartForConditionalGeneration, BartTokenizerFast

logger = logging.getLogger(__name__)

class ModelManager:
    _instance = None
    _bart_model = None
    _bart_tokenizer = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._device = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
            self._initialized = True
    
    def get_bart_models(self):
        if self._bart_model is None or self._bart_tokenizer is None:
            try:
                logger.info("🔄 Loading BART model from Hugging Face...")
                self._bart_tokenizer = BartTokenizerFast.from_pretrained("sshleifer/distilbart-cnn-12-6")
                self._bart_model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6").to(self._device)
                self._bart_model.eval()
                logger.info(f"✅ BART model: WORKING on {self._device}")
            except Exception as e:
                logger.error(f"❌ BART model: FAILED to load - {e}")
                self._bart_tokenizer = None
                self._bart_model = None
        
        return self._bart_tokenizer, self._bart_model

model_manager = ModelManager()
