# DOST AI Deployment Guide 🚀

## 🎯 Deployment Options

Choose your preferred deployment method:

1. **Railway** (Recommended - Easiest)
2. **Render** (Simple, good free tier)
3. **DigitalOcean App Platform** (Reliable)
4. **Docker Local** (Testing)

---

## 🚄 Option 1: Railway (Recommended)

**Why Railway?** Simplest deployment, generous free tier, automatic HTTPS.

### Steps:
1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   ```bash
   # First, push your code to GitHub
   git init
   git add .
   git commit -m "Initial DOST deployment"
   git branch -M main
   # Create a new repo on GitHub, then:
   git remote add origin https://github.com/yourusername/dost.git
   git push -u origin main
   ```

3. **Connect to Railway**
   - Click "Deploy from GitHub repo"
   - Select your dost repository
   - Railway auto-detects the Dockerfile
   - Click "Deploy"

4. **Access Your App**
   - Get your URL: `https://your-app-name.railway.app`
   - Test: `https://your-app-name.railway.app/health`

### Cost: **FREE** (500 hours/month)

---

## 🎨 Option 2: Render

### Steps:
1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy**
   - Click "New Web Service"
   - Connect your GitHub repo
   - Render detects `render.yaml` automatically
   - Click "Create Web Service"

3. **Wait for Build** (~5-10 minutes)

### Cost: **FREE** (750 hours/month)

---

## 🌊 Option 3: DigitalOcean App Platform

### Steps:
1. **Create DO Account**
   - Go to [digitalocean.com](https://digitalocean.com)
   - $200 free credit for new users

2. **Deploy**
   - Apps → Create App
   - Connect GitHub repo
   - Select Dockerfile
   - Choose $5/month plan (or free trial)

### Cost: **$5/month** (but free with credit)

---

## 🐳 Option 4: Docker Local Testing

Test your deployment locally first:

### Prerequisites:
```bash
# Install Docker Desktop from docker.com
# Or install Docker CLI
```

### Test Deployment:
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t dost-ai .
docker run -p 8000:8000 dost-ai

# Test
curl http://localhost:8000/health
```

---

## 🔧 Pre-Deployment Checklist

### 1. Test Locally
```bash
# Make sure your app works
uvicorn main_simple:app --reload
curl http://localhost:8000/health
```

### 2. Environment Variables (Optional)
If you want to add AI features later, prepare:
```bash
# For Railway/Render dashboard:
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./data/dost.db
```

### 3. Check Files
Ensure you have:
- ✅ `Dockerfile`
- ✅ `requirements_minimal.txt`
- ✅ `main_simple.py`
- ✅ `.dockerignore`

---

## 🚀 Quick Deploy Commands

### Test Docker Build:
```bash
docker build -t dost-test .
docker run -p 8000:8000 dost-test
```

### Git Setup for Deployment:
```bash
# Initialize repo
git init
git add .
git commit -m "Deploy DOST AI"

# Push to GitHub (create repo first)
git remote add origin https://github.com/yourusername/dost-ai.git
git push -u origin main
```

---

## 📊 Deployment Comparison

| Platform | Free Tier | Setup | Speed | Features |
|----------|-----------|-------|-------|----------|
| Railway | 500h/month | ⭐⭐⭐⭐⭐ | Fast | Auto HTTPS, domains |
| Render | 750h/month | ⭐⭐⭐⭐ | Medium | Auto deploy, SSL |
| DigitalOcean | Free trial | ⭐⭐⭐ | Fast | Scalable, professional |
| Docker Local | Free | ⭐⭐ | Instant | Testing only |

---

## 🎉 After Deployment

### 1. Test Your Live App
```bash
# Replace with your deployment URL
curl https://your-app.railway.app/health
curl https://your-app.railway.app/status
```

### 2. Create a User
```bash
curl -X POST https://your-app.railway.app/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
```

### 3. Test Chat
```bash
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello DOST!", "user_id": "user_1"}'
```

### 4. Access API Docs
- Visit: `https://your-app.railway.app/docs`
- Interactive API documentation

---

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails**
   ```bash
   # Check Dockerfile syntax
   docker build -t test .
   ```

2. **App Won't Start**
   ```bash
   # Check logs in platform dashboard
   # Ensure port binding: 0.0.0.0:$PORT
   ```

3. **Health Check Fails**
   ```bash
   # Test endpoint
   curl https://your-app.com/health
   ```

### Getting Help:
- Check platform logs (Railway/Render dashboard)
- Test locally first with Docker
- Verify all files are committed to Git

---

## 🎯 Next Steps

After successful deployment:

1. **Add Custom Domain** (optional)
2. **Set Up Monitoring** 
3. **Add AI Features** (when ready)
4. **Scale Resources** (if needed)

Your DOST AI is now live and accessible worldwide! 🌍 