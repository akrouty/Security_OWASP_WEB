# OWASP Top 10 Starter (FastAPI + security pack)

This is a clean project to practice securing a backend step-by-step.

## Windows + VS Code quick start

1) Open VS Code terminal in this folder and create a venv:
```
py -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Create a `.env` from the template and set a strong SECRET_KEY:
```
copy .env.example .env
# then edit .env and replace SECRET_KEY with a secure random value
```
Generate one:
```
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

3) Run the API:
```
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/health 
