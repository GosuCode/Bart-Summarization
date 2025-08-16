# Flashcards and MCQ Generation Service

A FastAPI microservice that generates flashcards and multiple choice questions from long text input using advanced NLP models and intelligent text chunking.

## 🚀 Features

### Core Functionality

- **Text Chunking**: Automatically splits long text into manageable chunks (~400 words) with 50-word overlap
- **Flashcard Generation**: Creates question-answer pairs from each text chunk
- **MCQ Generation**: Converts flashcards to multiple choice questions with plausible distractors
- **AI-Powered**: Uses T5 models for intelligent question generation
- **Fallback Support**: Graceful degradation to basic generation if AI models fail

### Smart Chunking Strategy

- **Optimal Size**: 400-word chunks for balanced processing
- **Context Preservation**: 50-word overlap between chunks maintains coherence
- **Automatic Handling**: No manual text splitting required
- **Scalable**: Handles texts of any length

### Intelligent Distractor Generation

- **Context-Aware**: Generates distractors based on answer type (dates, numbers, names)
- **Plausible Options**: Creates realistic but incorrect alternatives
- **Type Consistency**: Maintains same data type across all options
- **Randomized Order**: Shuffles options for variety

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Text   │───▶│  Text Chunker    │───▶│ Flashcard Gen.  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  400-word       │    │   Q&A Pairs    │
                       │  Chunks +       │    │                 │
                       │  50-word        │    └─────────────────┘
                       │  Overlap        │              │
                       └──────────────────┘              ▼
                                                       MCQ Gen.
                                                       with
                                                    Distractors
```

## 📡 API Endpoints

### Base URL

```
http://localhost:8000/api/v1/flashcards
```

### 1. Generate Flashcards

```http
POST /flashcards
```

**Request Body:**

```json
{
  "text": "Your long text here...",
  "questions_per_chunk": 3
}
```

**Response:**

```json
{
  "flashcards": [
    {
      "question": "What is the main topic?",
      "answer": "The main topic is..."
    }
  ],
  "total_flashcards": 9,
  "text_length": 1500,
  "chunks_processed": 4,
  "processing_time": 2.345
}
```

### 2. Generate MCQs

```http
POST /mcqs
```

**Request Body:**

```json
{
  "text": "Your long text here...",
  "questions_per_chunk": 3
}
```

**Response:**

```json
{
  "mcqs": [
    {
      "id": 1,
      "question": "What is the main topic?",
      "options": [
        "The main topic is...",
        "Distractor 1",
        "Distractor 2",
        "Distractor 3"
      ],
      "correct_answer_index": 0,
      "correct_answer": "The main topic is...",
      "explanation": "Based on the text: The main topic..."
    }
  ],
  "total_mcqs": 9,
  "text_length": 1500,
  "chunks_processed": 4,
  "processing_time": 3.456
}
```

### 3. Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "flashcards-mcq",
  "flashcard_generator_ready": true,
  "mcq_generator_ready": true
}
```

### 4. Supported Formats

```http
GET /supported-formats
```

**Response:**

```json
{
  "input_formats": ["plain_text", "long_text"],
  "max_text_length": "No limit (handled by chunking)",
  "chunk_size": "400 words",
  "chunk_overlap": "50 words",
  "questions_per_chunk_range": [1, 10],
  "default_questions_per_chunk": 3,
  "features": [
    "Automatic text chunking",
    "Context preservation with overlap",
    "T5-based question generation",
    "Fallback to basic generation",
    "Smart distractor generation for MCQs"
  ]
}
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Service

```bash
python main.py
```

The service will be available at `http://localhost:8000`

### 3. Test the Service

```bash
python test_flashcards.py
```

## 🔧 Configuration

### Environment Variables

- `MODEL_DIR`: Directory for T5 models (default: "./model")
- `DEVICE`: Device for model inference (default: auto-detect CUDA/CPU)

### Model Configuration

- **T5 Model**: `valhalla/t5-small-qg-hl` for question generation
- **Fallback**: Basic regex-based generation if T5 fails
- **Device**: Automatic CUDA detection with CPU fallback

## 📊 Performance

### Processing Times

- **Small text** (< 400 words): ~0.5-1 second
- **Medium text** (400-2000 words): ~1-3 seconds
- **Large text** (2000+ words): ~3-10 seconds

### Scalability

- **Memory**: Efficient chunking prevents memory issues
- **CPU**: Parallel processing of chunks (future enhancement)
- **GPU**: Automatic CUDA acceleration when available

## 🧪 Testing

### Manual Testing

```bash
# Test flashcards
curl -X POST "http://localhost:8000/api/v1/flashcards/flashcards" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here...", "questions_per_chunk": 3}'

# Test MCQs
curl -X POST "http://localhost:8000/api/v1/flashcards/mcqs" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here...", "questions_per_chunk": 3}'
```

### Automated Testing

```bash
python test_flashcards.py
```

## 🔍 Error Handling

### Common Errors

- **Empty Text**: Returns 400 with descriptive message
- **Text Too Short**: Minimum 50 characters required
- **Model Loading**: Graceful fallback to basic generation
- **Processing Errors**: Detailed error messages with logging

### Fallback Strategy

1. **Primary**: T5 model for intelligent generation
2. **Secondary**: Basic regex-based generation
3. **Tertiary**: Generic templates with text content

## 🚀 Future Enhancements

### Planned Features

- **Parallel Processing**: Process chunks concurrently
- **Advanced Distractors**: Use embeddings for semantic similarity
- **Custom Models**: Fine-tuned models for specific domains
- **Batch Processing**: Handle multiple texts simultaneously
- **Caching**: Cache generated content for repeated requests

### Performance Optimizations

- **Model Quantization**: Reduce memory footprint
- **Streaming**: Process very long texts incrementally
- **CDN Integration**: Serve static content efficiently

## 📝 Usage Examples

### Python Client

```python
import requests

# Generate flashcards
response = requests.post(
    "http://localhost:8000/api/v1/flashcards/flashcards",
    json={
        "text": "Your academic text here...",
        "questions_per_chunk": 4
    }
)

flashcards = response.json()["flashcards"]
print(f"Generated {len(flashcards)} flashcards")

# Generate MCQs
response = requests.post(
    "http://localhost:8000/api/v1/flashcards/mcqs",
    json={
        "text": "Your academic text here...",
        "questions_per_chunk": 4
    }
)

mcqs = response.json()["mcqs"]
print(f"Generated {len(mcqs)} MCQs")
```

### JavaScript/Node.js Client

```javascript
// Generate flashcards
const response = await fetch(
  "http://localhost:8000/api/v1/flashcards/flashcards",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: "Your academic text here...",
      questions_per_chunk: 4,
    }),
  }
);

const result = await response.json();
console.log(`Generated ${result.total_flashcards} flashcards`);
```

## 🤝 Contributing

### Code Style

- Follow PEP 8 for Python code
- Use type hints throughout
- Comprehensive docstrings for all functions
- Error handling with meaningful messages

### Testing

- Unit tests for all services
- Integration tests for API endpoints
- Performance benchmarks for large texts
- Error scenario testing

## 📄 License

This service is part of the LearnMate project and follows the same licensing terms.

---

**Note**: This service is designed for educational content and academic text processing. For production use, consider implementing additional security measures, rate limiting, and monitoring.
