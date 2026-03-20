FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads session_data

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## Step 6 — Monitor the Build

1. Go to your Space page on Hugging Face
2. Click the **Logs** tab to watch the Docker build live
3. Once it shows **Running**, your app is live at:
```
   https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
```

---

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| Build fails on `pip install` | Pin problematic packages in `requirements.txt` |
| App crashes on startup | Check Logs tab — likely missing `GR_API_KEY` secret |
| Port error | Ensure `app_port: 7860` in README and `--port 7860` in CMD |
| Files not found | Make sure `uploads/` and `session_data/` are created in Dockerfile |
| Git push rejected | Run `git pull --rebase` first, then push again |

---

## Folder Checklist Before Pushing

Make sure these files are present at the **root** of your repo:
```
✅ Dockerfile
✅ README.md          ← with the HF YAML header
✅ requirements.txt
✅ app/
✅ automl_trainer.py
✅ ml_pipeline.py
✅ asserts/           ← screenshots for README
```

You can add a `.gitignore` to exclude junk:
```
__pycache__/
*.pyc
session_data/
uploads/
.env