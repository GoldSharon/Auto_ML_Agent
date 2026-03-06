# AutoML Platform - Startup Guide

## Quick Start (Development)

### Option 1: Using npm scripts (Recommended)

**Terminal 1 - Backend**
```bash
npm run backend:dev
```
This will install dependencies and start FastAPI on `http://localhost:8000`

**Terminal 2 - Frontend**
```bash
npm run dev
```
This will start Next.js on `http://localhost:3000`

### Option 2: Manual Setup

**Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend Setup**
```bash
npm install
npm run dev
```

## Configuration

### 1. Create `.env.local` for frontend
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Setup LLM Configuration
1. Open `http://localhost:3000` in your browser
2. Click "Configure LLM" on the home page
3. Enter your LLM model name and API key
4. Configuration is saved to backend `.env` file

## Verification Checklist

- [ ] FastAPI running on port 8000
- [ ] Next.js running on port 3000
- [ ] LLM configuration saved
- [ ] GPU detected (optional but recommended)

## Health Check

Visit `http://localhost:3000` and check:
- System Status shows GPU or CPU mode
- LLM Configuration shows "✓ Configured" or "✗ Setup Required"
- "Create New Project" button is clickable

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000
# Or kill it
kill -9 <PID>
```

### Module Not Found (Backend)
```bash
cd backend
pip install -r requirements.txt
```

### Connection Refused
- Verify backend is running on `http://localhost:8000/api/health`
- Check `NEXT_PUBLIC_API_URL` is correct in `.env.local`

### WebSocket Connection Error
- WebSocket connects from browser to backend
- Ensure backend is fully started before opening frontend
- Check browser console for detailed error messages

## First Project Walkthrough

1. **Home Page** (`http://localhost:3000`)
   - Verify system status
   - Setup LLM if needed

2. **Create Project** 
   - Click "Create New Project"
   - Upload CSV file
   - Configure training parameters

3. **Monitor Training**
   - Watch real-time progress via WebSocket
   - View live logs
   - Wait for completion

4. **View Results**
   - See evaluation scores
   - Download results as JSON
   - Access project details

5. **Make Predictions**
   - Upload new CSV
   - Load trained model
   - Get predictions

## Production Deployment

For production, see deployment guides:
- **Backend**: FastAPI on Heroku, Railway, or AWS
- **Frontend**: Next.js on Vercel, Netlify, or AWS

Environment variables needed:
```bash
# Backend
LLM_MODEL_NAME=your-model
LLM_API_KEY=your-api-key

# Frontend  
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```
