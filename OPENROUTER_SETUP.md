# 🚀 OpenRouter Integration Setup Guide

## 🌟 **Why OpenRouter is Better Than Direct OpenAI**

### **💰 Cost Benefits:**
- **Often 20-50% cheaper** than direct OpenAI pricing
- **No rate limits** on most models
- **Free models available** (Llama 3, Gemini Pro, etc.)
- **Transparent pricing** with cost estimates

### **🎯 Model Variety:**
- **OpenAI models**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic models**: Claude 3 Haiku, Claude 3 Sonnet
- **Google models**: Gemini Pro, Gemini Flash
- **Meta models**: Llama 3 8B, Llama 3 70B
- **Many more** updated regularly

### **🔧 Technical Benefits:**
- **Better rate limits** than direct API
- **Unified API** for all models
- **Automatic retries** and failover
- **Better uptime** and reliability

---

## 🔑 **Step 1: Get Your OpenRouter API Key**

### **Create OpenRouter Account:**
1. Go to **[OpenRouter.ai](https://openrouter.ai)**
2. **Sign up** with Google/GitHub or email
3. **Add credits** to your account (start with $5-10)
4. **No payment method required** for free models!

### **Generate API Key:**
1. Go to **[Keys & Settings](https://openrouter.ai/keys)**
2. Click **"Create Key"**
3. **Name it**: "DOST-AI-Key"
4. **Copy the key** (starts with `sk-or-...`)
5. **Save it securely** - you'll need it for deployment

### **Set Usage Limits (Optional):**
1. Go to **[Settings](https://openrouter.ai/settings)**
2. Set **monthly spending limit**
3. Enable **usage notifications**

---

## 🚀 **Step 2: Deploy OpenRouter-Enabled Version**

### **Update Render Service:**
1. **Go to your Render dashboard**
2. **Click on your `dost-ai` service**
3. **Go to "Environment" tab**
4. **Add environment variable**:
   - **Key**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key (sk-or-...)
5. **Save changes** - Service will auto-redeploy

---

## 🤖 **Step 3: Available AI Models**

### **🏆 Recommended Models:**

| Model | Best For | Cost/1K tokens | Speed |
|-------|----------|----------------|-------|
| **llama-3-8b** | Fastest, cheapest | $0.0005 | ⚡⚡⚡ |
| **gpt-3.5-turbo** | Balanced performance | $0.002 | ⚡⚡ |
| **claude-3-haiku** | Fast, good quality | $0.0015 | ⚡⚡ |
| **gpt-4-turbo** | Best quality | $0.03 | ⚡ |
| **claude-3-sonnet** | Creative tasks | $0.015 | ⚡ |

### **🆓 Free Models:**
- **Llama 3 8B** - Great for casual conversations
- **Gemini Pro** - Good for coding tasks
- **Some older models** - Check OpenRouter for current free options

---

## 🧪 **Step 4: Test OpenRouter Features**

### **Test Different Models:**
```bash
# Test with default model (GPT-3.5)
curl -X POST https://dost-ai-j558.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! How are you?", "user_id": "user_1"}'

# Test with Llama 3 (free/cheap)
curl -X POST https://dost-ai-j558.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain quantum computing", "user_id": "user_1", "model": "llama-3-8b"}'

# Test with Claude 3 Haiku (fast)
curl -X POST https://dost-ai-j558.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a short poem", "user_id": "user_1", "model": "claude-3-haiku"}'
```

### **Check Available Models:**
```bash
curl https://dost-ai-j558.onrender.com/models
```

### **Check System Status:**
```bash
curl https://dost-ai-j558.onrender.com/status
```

---

## 💰 **Cost Comparison (per 1K tokens)**

| Provider | GPT-3.5 | GPT-4 | Claude 3 | Llama 3 |
|----------|---------|-------|----------|---------|
| **OpenAI Direct** | $0.0015 | $0.03 | N/A | N/A |
| **OpenRouter** | $0.002 | $0.03 | $0.015 | $0.0005 |
| **Savings** | Similar | Similar | Only option | 75% cheaper |

---

## 🎯 **Advanced Features**

### **1. Model Selection in Chat:**
```json
{
  "message": "Hello DOST!",
  "user_id": "user_1",
  "model": "claude-3-haiku"
}
```

### **2. Cost Tracking:**
Every response includes:
- **tokens_used**: Number of tokens consumed
- **model_used**: Which model processed the request
- **cost_estimate**: Estimated cost in USD

### **3. User Preferences:**
```json
{
  "name": "John",
  "email": "john@example.com",
  "preferences": {
    "model": "llama-3-8b"
  }
}
```

---

## 🔍 **New API Endpoints**

### **1. `/models` - Get Available Models**
```bash
curl https://dost-ai-j558.onrender.com/models
```

### **2. Enhanced `/status` - Full System Info**
```bash
curl https://dost-ai-j558.onrender.com/status
```

### **3. Enhanced `/chat` - Model Selection**
```bash
curl -X POST https://dost-ai-j558.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "user_1", "model": "gpt-4-turbo"}'
```

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **"OpenRouter API key missing"**
   - Check environment variable: `OPENROUTER_API_KEY`
   - Ensure key starts with `sk-or-`

2. **"Insufficient credits"**
   - Add credits to your OpenRouter account
   - Check current balance at openrouter.ai

3. **"Model not available"**
   - Check `/models` endpoint for available options
   - Some models may be temporarily unavailable

4. **"Rate limit exceeded"**
   - Much less likely with OpenRouter
   - Wait a moment and try again

---

## 🎉 **Example Conversations**

### **Try Different Models:**

**With Llama 3 (Fast & Free):**
```json
{"message": "Explain machine learning simply", "user_id": "user_1", "model": "llama-3-8b"}
```

**With Claude 3 (Creative):**
```json
{"message": "Write a creative story about AI", "user_id": "user_1", "model": "claude-3-haiku"}
```

**With GPT-4 (Best Quality):**
```json
{"message": "Solve this complex problem: ...", "user_id": "user_1", "model": "gpt-4-turbo"}
```

---

## 📊 **Usage Monitoring**

### **Track Your Usage:**
```bash
# Check total costs and usage
curl https://dost-ai-j558.onrender.com/status

# Check user-specific conversations
curl https://dost-ai-j558.onrender.com/conversations/user_1
```

### **In OpenRouter Dashboard:**
1. Go to **[OpenRouter.ai](https://openrouter.ai)**
2. **"Usage"** tab - See detailed usage stats
3. **"Models"** tab - Compare model performance

---

## 🚀 **Pro Tips**

1. **Start with free models** (Llama 3) for testing
2. **Use GPT-3.5** for general conversations
3. **Use Claude 3** for creative tasks
4. **Use GPT-4** only for complex reasoning
5. **Monitor costs** with the `/status` endpoint

---

## 🎯 **What's New in OpenRouter Version:**

- 🤖 **7+ AI models** available
- 💰 **Cost estimation** for every response
- 🔄 **Model switching** per conversation
- 📊 **Usage tracking** and statistics
- 🆓 **Free models** available
- ⚡ **Better performance** than direct APIs

**Your DOST AI now has access to the best AI models at the best prices!** 🎉 