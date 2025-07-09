# Training Guide for BART Summarization

This guide will help you train your own BART model for text summarization.

## 🎯 Why Train Your Own Model?

- **Domain-specific**: Better performance on your specific type of text
- **Language-specific**: Optimized for particular languages
- **Style-specific**: Match your desired summary style
- **Performance**: Potentially better results than general models

## 📋 Prerequisites

### 1. Install Training Dependencies

```bash
cd training
pip install -r requirements.txt
```

### 2. Set Up Weights & Biases (Optional but Recommended)

```bash
pip install wandb
wandb login
```

## 🚀 Quick Start Training

### 1. Configure Training Parameters

Edit `training/config.yaml` to adjust hyperparameters:

```yaml
model_name: facebook/bart-base # Base model to fine-tune
max_input_length: 1024 # Maximum input text length
max_target_length: 128 # Maximum summary length
batch_size: 8 # Batch size (reduce if OOM)
epochs: 3 # Number of training epochs
lr: 0.00003 # Learning rate
weight_decay: 0.01 # Weight decay
warmup_steps: 500 # Warmup steps
early_stopping_patience: 2 # Early stopping patience
output_dir: ../app/model # Where to save the model
device: cuda # cuda or cpu
gradient_accumulation_steps: 4 # Gradient accumulation
```

### 2. Start Training

```bash
cd training
python train_bart_summarization.py
```

### 3. Monitor Training

- **Console**: Training progress will be displayed
- **Weights & Biases**: Visit your W&B dashboard for detailed metrics
- **Logs**: Check for validation loss and ROUGE scores

## 📊 Training Details

### Dataset

The training uses the **CNN/DailyMail** dataset by default:

- **Training samples**: ~100,000 articles
- **Validation samples**: ~10,000 articles
- **Format**: News articles with human-written summaries

### Model Architecture

- **Base Model**: `facebook/bart-base`
- **Parameters**: ~140M parameters
- **Architecture**: BART (Bidirectional and Auto-Regressive Transformers)

### Training Process

1. **Tokenization**: Input text is tokenized using BART tokenizer
2. **Encoding**: BART encoder processes the input sequence
3. **Decoding**: BART decoder generates summary tokens
4. **Loss**: Cross-entropy loss on generated tokens
5. **Optimization**: AdamW with learning rate scheduling

## ⚙️ Advanced Configuration

### Custom Dataset

To use your own dataset, modify `training/data_utils.py`:

```python
def prepare_data(tokenizer, config):
    # Load your custom dataset
    dataset = load_dataset("your_dataset_name")

    # Preprocess your data
    def preprocess_function(examples):
        # Your preprocessing logic here
        return tokenized_examples

    # Apply preprocessing
    tokenized_dataset = dataset.map(preprocess_function, batched=True)

    return train_loader, val_loader
```

### Hyperparameter Tuning

Key parameters to experiment with:

```yaml
# Learning rate (try: 1e-5, 3e-5, 5e-5)
lr: 0.00003

# Batch size (reduce if out of memory)
batch_size: 8

# Number of epochs (more = longer training)
epochs: 3

# Maximum lengths (affect memory usage)
max_input_length: 1024
max_target_length: 128
```

## 🔧 Training on Different Hardware

### CPU Training

```yaml
device: cpu
batch_size: 4 # Reduce batch size for CPU
```

### GPU Training

```yaml
device: cuda
batch_size: 8 # Increase for better GPUs
```

### Multi-GPU Training

```bash
# Use DistributedDataParallel
python -m torch.distributed.launch --nproc_per_node=2 train_bart_summarization.py
```

## 📈 Monitoring and Evaluation

### Metrics Tracked

- **Training Loss**: Cross-entropy loss during training
- **Validation Loss**: Loss on validation set
- **ROUGE Scores**: ROUGE-1, ROUGE-2, ROUGE-L
- **BLEU Score**: Translation quality metric

### Early Stopping

- Training stops when validation loss doesn't improve
- Patience: 2 epochs (configurable)
- Best model is automatically saved

## 💾 Model Output

After training, the model will be saved to:

- `../app/model/` (or your configured `output_dir`)
- Includes model weights, tokenizer, and configuration
- Ready to use with your FastAPI app

## 🚨 Troubleshooting

### Out of Memory (OOM)

```yaml
# Reduce these values
batch_size: 4
max_input_length: 512
max_target_length: 64
gradient_accumulation_steps: 8
```

### Slow Training

```yaml
# Increase batch size if you have more memory
batch_size: 16
# Use gradient accumulation
gradient_accumulation_steps: 2
```

### Poor Results

- Try different learning rates
- Increase training epochs
- Use a larger base model (e.g., `facebook/bart-large`)
- Check your dataset quality

## 🎯 Next Steps

1. **Evaluate**: Test your trained model on sample texts
2. **Deploy**: Replace the pre-trained model with your custom model
3. **Iterate**: Train again with different parameters or data
4. **Monitor**: Track performance in production

## 📚 Resources

- [BART Paper](https://arxiv.org/abs/1910.13461)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Weights & Biases](https://wandb.ai/)
- [ROUGE Evaluation](<https://en.wikipedia.org/wiki/ROUGE_(metric)>)
