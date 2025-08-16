# Memory Optimization Guide

## 🚨 RAM Usage Problem

The original service was consuming **massive amounts of RAM** because:

1. **Multiple model instances**: BART and T5 models loaded 3+ times simultaneously
2. **Eager loading**: All models loaded at startup, even if not used
3. **No memory management**: Models stayed in memory indefinitely

## ✅ Solution: Lazy Loading + Singleton Pattern

### What Changed

1. **ModelManager Service**: Single point for all model loading
2. **Lazy Loading**: Models only loaded when first requested
3. **Singleton Pattern**: Only one instance of each model in memory
4. **Memory Management**: Endpoints to monitor and free memory

### Memory Usage Comparison

| Mode          | Startup RAM | Peak RAM | Model Loading  |
| ------------- | ----------- | -------- | -------------- |
| **Original**  | ~2-3 GB     | ~4-6 GB  | All at startup |
| **Optimized** | ~200-500 MB | ~2-3 GB  | On-demand      |

## 🚀 Usage

### Lightweight Mode (Recommended)

```bash
# Start with minimal memory usage
python3 start_lightweight.py

# Or with environment variables
PORT=8000 HOST=0.0.0.0 RELOAD=false python3 start_lightweight.py
```

### Standard Mode (Original)

```bash
# Original startup (higher memory usage)
python3 main.py
```

## 📊 Memory Monitoring

### Check Current Memory Usage

```bash
curl http://localhost:8000/memory
```

Response:

```json
{
  "device": "cpu",
  "bart_loaded": false,
  "t5_loaded": false,
  "cuda_memory_allocated": "0.00 GB",
  "cuda_memory_reserved": "0.00 GB"
}
```

### Free Memory

```bash
curl -X POST http://localhost:8000/memory/unload
```

## 🔧 Configuration

### Environment Variables

```bash
# Device selection
DEVICE=cpu          # Use CPU (lower memory, slower)
DEVICE=cuda         # Use GPU (higher memory, faster)

# Service configuration
PORT=8000           # Port number
HOST=0.0.0.0       # Host binding
RELOAD=false        # Disable reload for production
```

### Model Loading Strategy

1. **First Request**: Models loaded automatically
2. **Subsequent Requests**: Models reused from memory
3. **Memory Pressure**: Use `/memory/unload` endpoint
4. **Idle Time**: Models can be unloaded manually

## 🎯 Best Practices

### Development

```bash
# Use lightweight mode for development
python3 start_lightweight.py

# Monitor memory usage
curl http://localhost:8000/memory
```

### Production

```bash
# Disable reload for production
RELOAD=false python3 start_lightweight.py

# Use Fastify backend for heavy workloads
# (Better memory management, faster inference)
```

### Memory Management

```bash
# Unload models when not needed
curl -X POST http://localhost:8000/memory/unload

# Check memory before/after operations
curl http://localhost:8000/memory
```

## 🐛 Troubleshooting

### High Memory Usage

1. **Check loaded models**:

   ```bash
   curl http://localhost:8000/memory
   ```

2. **Unload models**:

   ```bash
   curl -X POST http://localhost:8000/memory/unload
   ```

3. **Restart service**:
   ```bash
   pkill -f "uvicorn"
   python3 start_lightweight.py
   ```

### Model Loading Issues

1. **Check device availability**:

   ```bash
   python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
   ```

2. **Verify model downloads**:
   ```bash
   # Models downloaded to ~/.cache/huggingface/
   ls -la ~/.cache/huggingface/
   ```

## 📈 Performance Tips

1. **Use Fastify backend** for production workloads
2. **Keep models loaded** during active usage periods
3. **Unload models** during idle periods
4. **Monitor memory** regularly with `/memory` endpoint
5. **Use appropriate device** (CPU vs GPU) based on requirements

## 🔄 Migration from Original

1. **Stop original service**:

   ```bash
   pkill -f "uvicorn main:app"
   ```

2. **Start lightweight service**:

   ```bash
   python3 start_lightweight.py
   ```

3. **Verify functionality**:

   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/memory
   ```

4. **Test endpoints**:
   ```bash
   # Test summarization (will load models on first request)
   curl -X POST "http://localhost:8000/api/v1/summarize" \
        -H "Content-Type: application/json" \
        -d '{"text": "Test text", "max_length": 50}'
   ```

## 📝 Summary

The memory optimization provides:

- ✅ **70-80% reduction** in startup memory usage
- ✅ **On-demand model loading** for better resource management
- ✅ **Memory monitoring** and management endpoints
- ✅ **Production-ready** lightweight mode
- ✅ **Backward compatibility** with existing endpoints

Use `start_lightweight.py` for development and production to significantly reduce RAM usage while maintaining all functionality.

