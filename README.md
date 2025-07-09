# BART Text Summarization Service

A FastAPI-based web service that provides text summarization capabilities using BART (Bidirectional and Auto-Regressive Transformers) models. This project includes both a pre-trained model for immediate use and training capabilities for custom models.

## 🚀 Features

- **Text Summarization**: Convert long articles into concise summaries
- **Web Interface**: User-friendly web UI for easy interaction
- **REST API**: Programmatic access via HTTP endpoints
- **Custom Training**: Train your own models on specific datasets
- **Docker Support**: Containerized deployment
- **Real-time Processing**: Fast inference with optimized models

## 🏗️ Architecture

### Project Structure

```
bart-summarization/
├── app/                    # FastAPI web service
│   ├── summarization_app.py    # Main application
│   ├── static/                 # Web interface files
│   ├── requirements.txt        # App dependencies
│   ├── Dockerfile             # Container configuration
│   └── model/                 # Pre-trained model storage
├── training/               # Model training utilities
│   ├── train_bart_summarization.py  # Main training script
│   ├── train.py                   # Training loop
│   ├── data_utils.py              # Data preprocessing
│   ├── config.yaml               # Training configuration
│   └── requirements.txt          # Training dependencies
├── docker-compose.yml      # Multi-container setup
└── README.md              # This file
```

## 🤖 Model Information

### Current Model: DistilBART-CNN-12-6

- **Model**: `sshleifer/distilbart-cnn-12-6`
- **Type**: Distilled BART model fine-tuned for summarization
- **Base Architecture**: BART (Bidirectional and Auto-Regressive Transformers)
- **Training Data**: CNN/DailyMail dataset
- **Model Size**: ~1.2GB (distilled version, smaller than full BART)
- **Performance**: Optimized for speed while maintaining quality

### Why This Model?

- **Pre-trained for Summarization**: Specifically fine-tuned on summarization tasks
- **Distilled**: Smaller and faster than full BART models
- **Proven Performance**: Well-established in the summarization community
- **Balanced**: Good trade-off between speed and quality

## 🛠️ Technology Stack

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face library for state-of-the-art NLP models
- **Uvicorn**: ASGI server for FastAPI

### Frontend

- **HTML/CSS/JavaScript**: Simple, responsive web interface
- **Fetch API**: For making requests to the backend

### Training

- **Datasets**: Hugging Face datasets library
- **Weights & Biases**: Experiment tracking (optional)
- **Scikit-learn**: Data preprocessing utilities

## 📦 Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- Docker (optional, for containerized deployment)

### Quick Start (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/GosuCode/Bart-Summarization.git
   cd Bart-Summarization
   ```

2. **Install dependencies**

   ```bash
   pip install -r app/requirements.txt
   ```

3. **Download pre-trained model**

   ```bash
   cd app
   mkdir -p model
   python3 -c "import transformers; print('Downloading BART summarization model...'); model = transformers.BartForConditionalGeneration.from_pretrained('sshleifer/distilbart-cnn-12-6'); tokenizer = transformers.BartTokenizerFast.from_pretrained('sshleifer/distilbart-cnn-12-6'); model.save_pretrained('./model'); tokenizer.save_pretrained('./model'); print('✅ Model downloaded successfully!')"
   ```

4. **Run the application**

   ```bash
   python summarization_app.py
   ```

   > **Note**: If you haven't downloaded the model yet, the app will show an error. Make sure to run the download command in step 3 first.

5. **Access the service**
   - Web Interface: http://localhost:8000
   - API Endpoint: http://localhost:8000/summarize

### Docker Deployment

> **Note**: Docker is great for production deployment and consistent environments. For development, the local setup above is faster and easier to debug.

1. **Download the model first** (required for Docker)

   ```bash
   cd app
   mkdir -p model
   python3 -c "import transformers; print('Downloading BART summarization model...'); model = transformers.BartForConditionalGeneration.from_pretrained('sshleifer/distilbart-cnn-12-6'); tokenizer = transformers.BartTokenizerFast.from_pretrained('sshleifer/distilbart-cnn-12-6'); model.save_pretrained('./model'); tokenizer.save_pretrained('./model'); print('✅ Model downloaded successfully!')"
   cd ..
   ```

2. **Build and run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

3. **Access the service**

   - Web Interface: http://localhost:8000 (direct app)
   - Web Interface: http://localhost:80 (via nginx)
   - API Endpoint: http://localhost:8000/summarize
   - API Endpoint: http://localhost:80/summarize

4. **Stop the service**

   ```bash
   docker-compose down
   ```

## 🎯 Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Paste your text in the textarea
3. Click "Summarize"
4. View the generated summary

### API Usage

#### Basic Summarization

```bash
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your long article text here...",
       "max_length": 100,
       "num_beams": 4
     }'
```

#### Python Example

```python
import requests

url = "http://localhost:8000/summarize"
data = {
    "text": "Your long article text here...",
    "max_length": 100,
    "num_beams": 4
}

response = requests.post(url, json=data)
summary = response.json()["summary"]
print(summary)
```

### API Parameters

| Parameter    | Type    | Default  | Description                     |
| ------------ | ------- | -------- | ------------------------------- |
| `text`       | string  | required | Input text to summarize         |
| `max_length` | integer | 128      | Maximum length of the summary   |
| `num_beams`  | integer | 4        | Number of beams for beam search |

## 🎓 Training Custom Models

> **📖 For detailed training instructions, see [TRAINING.md](TRAINING.md)**

### Quick Training Start

1. **Install training dependencies**

   ```bash
   cd training
   pip install -r requirements.txt
   ```

2. **Configure training** (optional)

   ```bash
   # Edit config.yaml to adjust hyperparameters
   ```

3. **Start training**
   ```bash
   python train_bart_summarization.py
   ```

### Why Train Custom Models?

- **Domain-specific**: Better performance on specific types of text
- **Language-specific**: Optimized for particular languages
- **Style-specific**: Match your desired summary style
- **Performance**: Potentially better results than general models

### Training Configuration

The training uses the CNN/DailyMail dataset by default:

- **Training samples**: 100,000 articles
- **Validation samples**: 10,000 articles
- **Model**: BART-base as starting point
- **Optimizer**: AdamW with learning rate scheduling
- **Monitoring**: Weights & Biases integration

### Key Training Parameters

```yaml
model_name: facebook/bart-base
max_input_length: 1024
max_target_length: 128
batch_size: 8
epochs: 3
lr: 0.00003
weight_decay: 0.01
warmup_steps: 500
early_stopping_patience: 2
```

## 🔧 Technical Details

### Summarization Technique

This project uses **Abstractive Summarization** with BART:

1. **Tokenization**: Input text is tokenized using BART tokenizer
2. **Encoding**: BART encoder processes the input sequence
3. **Decoding**: BART decoder generates summary tokens autoregressively
4. **Beam Search**: Uses beam search for better quality generation
5. **Post-processing**: Tokens are decoded back to text

### Model Architecture

**BART (Bidirectional and Auto-Regressive Transformers)**:

- **Encoder**: Bidirectional attention (like BERT)
- **Decoder**: Auto-regressive generation (like GPT)
- **Pre-training**: Denoising autoencoder objective
- **Fine-tuning**: Sequence-to-sequence learning

### Performance Optimizations

- **Model Distillation**: Using smaller, faster distilled version
- **Beam Search**: Configurable beam size for quality/speed trade-off
- **Length Penalty**: Prevents overly short summaries
- **Early Stopping**: Stops generation when appropriate
- **GPU Acceleration**: Automatic CUDA detection and usage

## 📊 Performance Metrics

### Quality Metrics

- **ROUGE Score**: Standard evaluation metric for summarization
- **BLEU Score**: Translation quality metric (sometimes used for summarization)
- **Human Evaluation**: Subjective quality assessment

### Speed Metrics

- **Inference Time**: ~1-3 seconds per summary (CPU)
- **Throughput**: ~20-50 summaries per minute (depending on text length)
- **Memory Usage**: ~2-4GB RAM (model + processing)

## 🚨 Troubleshooting

### Common Issues

1. **CUDA Warnings**

   - These are harmless warnings about GPU detection
   - The app will automatically use CPU if GPU is not available

2. **Model Download Issues**

   - Check internet connection
   - Ensure sufficient disk space (~2GB for model)
   - Try running the app again (it will retry download)

3. **Memory Issues**

   - Reduce batch size in training
   - Use smaller model variants
   - Increase system RAM

4. **Port Conflicts**
   - Change port in `summarization_app.py`
   - Check if port 8000 is already in use

### Environment Variables

| Variable    | Default    | Description              |
| ----------- | ---------- | ------------------------ |
| `MODEL_DIR` | `../model` | Path to model directory  |
| `DEVICE`    | `auto`     | Device to use (cuda/cpu) |
| `PORT`      | `8000`     | Server port              |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For the transformers library and model hub
- **Facebook Research**: For the BART model architecture
- **CNN/DailyMail**: For the summarization dataset
- **FastAPI**: For the excellent web framework

---

**Note**: This service is designed for educational and research purposes. For production use, consider additional security, monitoring, and scaling considerations.
