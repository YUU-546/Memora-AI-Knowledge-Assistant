# Memora

Memora is an AI personal knowledge assistant. The MVP goal is simple:

```text
Send content from WeChat/WeCom
→ analyze it with DeepSeek
→ save a structured knowledge card to Feishu Bitable
```

## Current Stage

MVP scaffold:

- FastAPI backend
- DeepSeek knowledge analyzer
- Feishu Bitable integration client
- Message orchestration API
- GitHub-ready project layout

## Tech Stack

- Backend: FastAPI
- AI model: DeepSeek `deepseek-v4-flash`
- MVP storage: Feishu Bitable
- Deployment: Docker Compose + Nginx on Aliyun ECS

## Project Structure

```text
backend/        FastAPI service
docs/           Product and architecture docs
config/         Deployment config
scripts/        Helper scripts
frontend/       Reserved for future admin/search UI
```

## Local Development

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Environment

Copy `.env.example` to `.env` and fill in the required keys.

DeepSeek is the default model provider because token cost is a major MVP constraint.

## GitHub

After creating an empty GitHub repository, add the remote:

```powershell
git remote add origin https://github.com/<your-name>/<repo-name>.git
git branch -M main
git push -u origin main
```
