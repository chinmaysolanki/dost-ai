# OpenAI API Cost Management for DOST

## 💰 Understanding Costs

### What Uses the API in DOST:
1. **Chat Messages** - GPT-4 for intelligent responses
2. **Voice Transcription** - Whisper for speech-to-text
3. **Voice Synthesis** - TTS for text-to-speech (optional)
4. **Intent Analysis** - GPT-4 for understanding user requests
5. **Task Processing** - GPT-4 for smart task management
6. **Calendar Insights** - GPT-4 for schedule analysis

## 🔧 Cost Control Strategies

### 1. Use GPT-3.5 Turbo Instead of GPT-4
```python
# In app/config.py, change:
OPENAI_MODEL = "gpt-3.5-turbo"  # Instead of "gpt-4"
# This reduces costs by ~90%
```

### 2. Set Usage Limits
```python
# Add to app/config.py
MAX_DAILY_REQUESTS = 100  # Limit requests per day
MAX_TOKENS_PER_REQUEST = 500  # Limit response length
```

### 3. Disable Expensive Features Initially
```python
# In main.py, disable features:
ENABLE_VOICE_PROCESSING = False  # Saves Whisper costs
ENABLE_TTS = False  # Saves TTS costs
ENABLE_CALENDAR_INSIGHTS = False  # Reduces GPT usage
```

### 4. Monitor Usage with OpenAI Dashboard
- Visit: https://platform.openai.com/usage
- Set up billing alerts
- Monitor daily/monthly spend

## 📊 Cost Estimation Tool

### Calculate Your Expected Costs:

**Chat Messages:**
- Average tokens per message: ~100-300
- With GPT-3.5: $0.0003-0.0009 per message
- With GPT-4: $0.003-0.009 per message

**Voice Processing:**
- 30-second voice message: ~$0.003
- 2-minute voice message: ~$0.012

**Example: 50 messages/day with GPT-3.5:**
- Chat: 50 × $0.0006 = $0.03/day = $0.90/month
- Voice (10 messages): 10 × $0.003 = $0.03/day = $0.90/month
- **Total: ~$1.80/month**

## 🆓 Free Alternatives

### For Development/Testing:
1. **Mock Responses**: Use the current simplified version
2. **Ollama**: Run local models (free but needs powerful hardware)
3. **Hugging Face**: Free models with API limits

### Local Model Setup (Free):
```bash
# Install Ollama for local AI
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2  # Download free model
```

## 💳 Getting Started Safely

### 1. Start with OpenAI Free Tier
- New accounts get $5 free credit
- Perfect for testing DOST

### 2. Set Hard Limits
- Set a monthly budget in OpenAI dashboard
- Start with $10-20 limit

### 3. Begin with Basic Features
```bash
# Run simplified version first
uvicorn main_simple:app --reload

# Then gradually enable AI features
uvicorn main:app --reload
```

## 🚨 Cost Alerts Setup

### OpenAI Dashboard:
1. Go to https://platform.openai.com/account/billing
2. Set usage alerts at $5, $10, $25
3. Monitor daily usage

### DOST Built-in Monitoring:
- Check `/api/usage` endpoint for token tracking
- View costs in the admin dashboard

## 💡 Pro Tips

1. **Start Small**: Use GPT-3.5 and basic features first
2. **Monitor Daily**: Check usage in OpenAI dashboard
3. **Set Budgets**: Hard limits prevent surprises
4. **Optimize Prompts**: Shorter, clearer prompts cost less
5. **Cache Responses**: Avoid repeat API calls for same queries

## 🔄 Switching Models

You can easily switch between models based on your budget:

```env
# Budget option (.env file)
OPENAI_MODEL=gpt-3.5-turbo
ENABLE_VOICE=false

# Premium option
OPENAI_MODEL=gpt-4
ENABLE_VOICE=true
``` 