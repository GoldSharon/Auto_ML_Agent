# 🚀 START HERE - AutoML Platform Quick Launch

## Welcome! Let's Get You Running in 5 Minutes

This is a **complete, production-ready AutoML system** combining your ML pipeline with a professional web interface.

---

## The Fastest Way (Choose Your OS)

### 🐧 Linux or Mac
```bash
chmod +x start.sh
./start.sh
```

### 🪟 Windows
```bash
start.bat
```

That's it! The script will:
- ✅ Check Python and Node.js
- ✅ Install all dependencies
- ✅ Create your `.env` file
- ✅ Start both backend and frontend
- ✅ Give you the URLs

Then visit: **http://localhost:3000**

---

## What You'll See

### Home Page
- System status (GPU detection)
- LLM configuration check
- Quick start button

### Setup (First Time Only)
1. Add your Google API key (from https://ai.google.dev)
2. Click "Save Configuration"
3. One-time setup, done!

### Create Your First Project
1. Click "Create New Project"
2. Upload a CSV file (any size)
3. Select task type (Classification/Regression/Clustering)
4. Choose target column
5. Click "Start Training"
6. Watch real-time progress
7. Download results

---

## What This System Does

### You Upload CSV → We Train Models

```
Your CSV file
    ↓
Google Gemini AI analyzes your data
    ↓
Advanced preprocessing (automatic!)
    ↓
8+ ML algorithms train simultaneously
    ↓
Best model selected automatically
    ↓
Download results & use for predictions
```

**No manual feature engineering needed. No configuration required. Just upload and train.**

---

## Example: Predict Customer Churn

```
1. Upload: customer_data.csv (20,000 rows)
   ↓
2. Configure: 
   - ML Type: Supervised
   - Task: Classification (predict churn)
   - Target: is_churned
   ↓
3. Train:
   - Auto preprocessing
   - 8 models trained in parallel
   - Takes 5-10 minutes
   ↓
4. Results:
   - XGBoost wins with F1=0.91
   - Download scores.json
   ↓
5. Predict:
   - Upload new 5K customers
   - Get predictions instantly
```

---

## Key Features

✨ **Intelligent** - Google Gemini AI understands your data
🚀 **Fast** - Multiple models train simultaneously  
💰 **Affordable** - Uses free Google API (with generous quota)
🎯 **Automatic** - No manual configuration needed
📊 **Comprehensive** - Classification, Regression, Clustering
⚡ **Accelerated** - Automatic GPU detection
💾 **Persistent** - Save models, re-predict anytime

---

## First Steps

### 1. Get Google API Key (2 minutes)
1. Go to https://ai.google.dev
2. Click "Get API Key" 
3. Create new project or use existing
4. Copy your API key
5. Keep it somewhere safe

### 2. Run the Startup Script (2 minutes)
```bash
./start.sh    # Linux/Mac
# or
start.bat     # Windows
```

### 3. Configure LLM (1 minute)
1. Visit http://localhost:3000
2. Click "Configure LLM"
3. Enter API key from step 1
4. Click "Save"

### 4. Train Your First Model (5 minutes)
1. Click "Create New Project"
2. Upload CSV file
3. Configure (select target column, task type)
4. Click "Start Training"
5. Watch progress in real-time

### 5. Use Your Model (1 minute)
1. Go to "Projects"
2. Click your project
3. Click "Make Predictions"
4. Upload new CSV with same columns
5. Download predictions

---

## I'm Stuck! Quick Fixes

### Backend won't start
```bash
# Check Python is installed
python --version  # Should be 3.10+

# Try these commands
cd backend
python main.py
```

### Frontend won't start  
```bash
npm install
npm run dev
```

### LLM error
- Get API key from https://ai.google.dev
- Make sure it's in your `.env` file
- Copy entire key (don't add quotes)

### Can't connect frontend to backend
- Check `.env` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Both servers running?
- Try different browser

### Out of memory
- Upload smaller dataset
- Use "Training-Only" mode
- Enable GPU if available

### More issues?
See [STARTUP.md](./STARTUP.md) for quick fixes
See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed troubleshooting

---

## File Locations

| What | Where |
|------|-------|
| Frontend code | `app/` directory |
| Backend code | `backend/` directory |
| Trained models | `projects/` directory |
| Configuration | `.env` file |
| Documentation | `*.md` files |
| Startup scripts | `start.sh` or `start.bat` |

---

## Common Commands

```bash
# Start everything
./start.sh              # Linux/Mac
start.bat               # Windows

# Just backend
cd backend && python main.py

# Just frontend  
npm run dev

# Stop everything
Ctrl+C                  # In each terminal

# Check if running
curl http://localhost:8000/api/health     # Backend
curl http://localhost:3000                # Frontend

# See API docs
# Visit: http://localhost:8000/docs
```

---

## What's Inside

### Backend (Python/FastAPI)
- 8+ ML algorithms
- Google Gemini integration
- WebSocket for real-time updates
- Model saving and loading
- Batch predictions

### Frontend (Next.js/React)
- Upload interface
- Real-time training dashboard
- Project history
- Prediction interface
- Results visualization

### ML Pipeline (Your Code)
- Data analysis (intelligent_data_analyzer.py)
- Preprocessing (intelligent_data_processor.py)
- Model training (model_registry.py)
- Pipeline orchestration (automl_pipeline.py)
- LLM integration (cognitive_engine.py)

---

## Next: Read More

### Want to understand how it works?
→ Read [README.md](./README.md)

### Need detailed setup help?
→ Read [SETUP_GUIDE.md](./SETUP_GUIDE.md)

### Want to customize it?
→ Read [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

### Ready to deploy?
→ Read [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

### Need quick reference?
→ Read [STARTUP.md](./STARTUP.md)

### Documentation map?
→ Read [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)

---

## That's It! 

You're ready to go. Run the startup script and start training ML models!

```bash
./start.sh    # or start.bat on Windows
```

Then visit: **http://localhost:3000**

---

**Questions?** Check the relevant guide above.
**Ready?** Start with `./start.sh`
**Let's build something amazing!** 🚀

---

*AutoML Platform - Production-Ready Machine Learning for Everyone*
