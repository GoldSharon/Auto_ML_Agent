# AutoML Platform - Quick Reference Guide

## 🎯 What Is This?

A **production-ready system** that automatically builds ML models from CSV files.

**No experience needed.** Just upload data, select what you want to predict, and let it train.

---

## ⚡ Get Started in 5 Minutes

### Step 1: Run This (pick your OS)
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### Step 2: Get API Key
Visit: https://ai.google.dev
- Click "Get API Key"
- Copy it

### Step 3: Open Browser
```
http://localhost:3000
```

### Step 4: Paste API Key
- Click "Configure LLM"
- Paste API key
- Click "Save"

### Step 5: Upload & Train
- Click "Create New Project"
- Upload CSV
- Select target column
- Watch training happen live!

---

## 📊 What Can It Do?

### Classification (Predict Categories)
"Will customer churn?" → Yes/No
"What sentiment?" → Positive/Negative/Neutral
"Which segment?" → Premium/Standard/Basic

### Regression (Predict Numbers)
"What's the price?" → $5,000-$10,000
"How many units?" → 1,000-5,000
"What's the score?" → 1-100

### Clustering (Group Similar Items)
"Which customers are similar?" → Group 1, 2, 3
"Are there patterns?" → 5 distinct clusters
"How to segment?" → Auto-identified segments

---

## 📁 File Structure (What You Need to Know)

```
Your AutoML Platform
├── app/              ← Frontend code (Don't need to edit)
├── backend/          ← ML code (Can customize)
├── projects/         ← Saved models (Auto-created)
├── start.sh          ← Run this (Linux/Mac)
├── start.bat         ← Run this (Windows)
├── .env              ← Add API key here
└── README.md         ← Read this for details
```

---

## 🔧 Commands You Need

### Start Everything
```bash
./start.sh    # Linux/Mac
start.bat     # Windows
```

### Stop Everything
```
Ctrl+C in each terminal
```

### Check If Running
```bash
# Backend
curl http://localhost:8000/api/health

# Frontend  
curl http://localhost:3000
```

### See API Documentation
```
http://localhost:8000/docs
```

---

## 🎓 Learning Path

### Path 1: Just Want to Use It
1. [START_HERE.md](./START_HERE.md) ← Read first
2. Run `./start.sh`
3. Upload CSV and train!
4. Done! That's all you need

### Path 2: Want to Understand It
1. [START_HERE.md](./START_HERE.md) - Quick start
2. [README.md](./README.md) - Overview
3. [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - How it works
4. Source code in `backend/` and `app/`

### Path 3: Want to Customize It
1. [START_HERE.md](./START_HERE.md) - Get running
2. [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) - How to modify
3. Edit files in `backend/`
4. Test changes locally

### Path 4: Want to Deploy It
1. [START_HERE.md](./START_HERE.md) - Local version
2. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - All deployment steps
3. Follow your platform (Vercel, Railway, etc.)
4. Configure monitoring

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | `cd backend && python main.py` |
| Frontend won't start | `npm install && npm run dev` |
| "API key invalid" | Get new one from https://ai.google.dev |
| "Can't connect" | Check NEXT_PUBLIC_API_URL in .env |
| "Out of memory" | Use smaller dataset or Training-Only mode |
| "Training slow" | Enable GPU with `nvidia-smi` or reduce data |

**More help**: See [STARTUP.md](./STARTUP.md)

---

## 📖 Documentation Map

| Document | Time | Purpose |
|----------|------|---------|
| [START_HERE.md](./START_HERE.md) | 5 min | Quick start ⭐ READ FIRST |
| [README.md](./README.md) | 10 min | Overview |
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | 20 min | Detailed setup |
| [STARTUP.md](./STARTUP.md) | 5 min | Quick reference |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | 15 min | How it works |
| [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) | 20 min | How to customize |
| [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) | 25 min | Deploy to production |
| [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) | 5 min | Navigation guide |
| [DELIVERY_SUMMARY.md](./DELIVERY_SUMMARY.md) | 10 min | What you got |

---

## 🚀 Quickest Path to Success

```
1. ./start.sh
   ↓
2. http://localhost:3000
   ↓
3. Add Google API key
   ↓
4. Upload CSV
   ↓
5. Select task type
   ↓
6. Watch it train!
   ↓
7. Download results
```

**Total Time: 15 minutes**

---

## 🤖 Algorithms (What Gets Trained)

### Classification (8 algorithms)
- Logistic Regression
- Support Vector Machine
- Random Forest
- Gradient Boosting
- XGBoost ⭐ (usually wins)
- CatBoost
- Neural Networks
- And more...

### Regression (8 algorithms)
- Linear Regression
- Ridge Regression
- Lasso Regression
- Support Vector Regression
- Random Forest
- Gradient Boosting
- XGBoost
- CatBoost

### Clustering (3 algorithms)
- K-Means
- DBSCAN
- Hierarchical Clustering

**All trained automatically. Best one selected automatically.**

---

## 💾 Your Data

### What Happens to It
1. Uploaded to temporary storage
2. Analyzed by Google Gemini AI
3. Preprocessed automatically
4. Split into train/test sets
5. Models trained on train set
6. Evaluated on test set
7. Saved in `projects/` folder
8. Can be deleted anytime

### Privacy
- Data never leaves your computer (runs locally)
- Only summary sent to LLM for analysis
- Saved securely in `projects/`
- You can delete anytime

---

## ⚙️ Configuration

### Environment File (.env)
```bash
# Required (get from https://ai.google.dev)
LLM_API_KEY=your_key_here

# Already set
LLM_MODEL_NAME=gemini-2.0-flash
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional (for GPU selection)
CUDA_VISIBLE_DEVICES=0
```

### Model Training Options
- **ML Type**: Supervised vs Unsupervised
- **Task**: Classification / Regression / Clustering
- **Preprocessing**: Full (recommended) or Training-Only
- **Test Size**: How much data for testing (default 20%)
- **Tuning**: Enable hyperparameter optimization

---

## 📊 Metrics

### Classification Metrics
- **Accuracy** - % correct predictions
- **Precision** - True positives / all positive predictions
- **Recall** - True positives / all actual positives
- **F1 Score** - Balance of precision and recall
- **ROC-AUC** - Performance across thresholds

### Regression Metrics
- **R² Score** - How much variance explained (0-1)
- **MAE** - Average absolute error
- **MSE** - Average squared error
- **RMSE** - Root mean squared error
- **Explained Variance** - Proportion explained

### Clustering Metrics
- **Silhouette Score** - How well separated clusters
- **Calinski-Harabasz** - Cluster density ratio
- **Davies-Bouldin** - Average cluster similarity

---

## 🌐 API Endpoints (Advanced)

### Train Your Model
```
POST /api/upload         - Upload CSV
POST /api/analyze        - Analyze data
POST /api/train          - Start training
WS /ws/{project}         - Real-time updates
```

### Use Your Model
```
GET /api/projects        - List all projects
GET /api/project/{name}  - Get project details
POST /api/predict/{name} - Make predictions
```

### Configuration
```
GET /api/health          - System status
GET /api/env-status      - LLM check
POST /api/setup-llm      - Configure LLM
```

Full docs: http://localhost:8000/docs

---

## 🔐 Security

✅ **Your Data**
- Stays on your machine
- Not shared or sold
- Can be deleted anytime

✅ **Your Code**
- All open source
- Can audit everything
- Can self-host

✅ **Your API Key**
- Only used for data analysis
- Not stored in code
- Stored in .env (git ignored)

---

## 💡 Tips & Tricks

### Pro Tips
1. **Start small** - Test with small CSV first
2. **Check quality** - Good data = good models
3. **Pick clear target** - Make sure target column makes sense
4. **Try both modes** - Full preprocessing vs Training-Only
5. **Download results** - Save evaluation_scores.json

### Common Mistakes
1. ❌ Wrong target column - Model won't make sense
2. ❌ Leaky features - Using future data to predict
3. ❌ Missing values - Too many missing breaks preprocessing
4. ❌ Wrong task - Classification for continuous values
5. ❌ Imbalanced data - Extreme class imbalance affects metrics

---

## 📈 Example Workflow

```
Dataset: customer_transactions.csv (50K rows)

Step 1: Upload
  → System detects: 20 features, 1 target, 2% missing

Step 2: Configure
  → Task: Classification (predict churn)
  → Target: is_churned (0/1)
  → Preprocessing: Full
  → Tuning: Yes

Step 3: Train (5 minutes)
  → Data: Clean, encode, engineer features
  → Models: 8 algorithms train in parallel
  → Best: XGBoost with F1=0.91

Step 4: Results
  → Download: evaluation_scores.json
  → See: All model performances
  → Use: For predictions

Step 5: Predict
  → Upload: New 10K customers
  → Predict: 4,200 will churn
  → Download: predictions.csv
```

---

## 🎯 Getting Help

| Question | Answer |
|----------|--------|
| How do I...? | Check [START_HERE.md](./START_HERE.md) |
| It's broken | See [STARTUP.md](./STARTUP.md) |
| How do I customize? | Read [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) |
| I want to deploy | Follow [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) |
| Where's the docs? | See [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) |

---

## ✅ You're Ready!

Everything is installed and ready to go. Just run:

```bash
./start.sh      # Linux/Mac
# or
start.bat       # Windows
```

Then open: **http://localhost:3000**

**Happy machine learning!** 🚀

---

*Bookmark this page and [START_HERE.md](./START_HERE.md) for quick reference*
