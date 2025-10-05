1) create venv + install
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate
pip install -r requirements.txt

 2) copy .env and set your values
cp .env.example .env

 3) (optional) verify integrity of assets on startup
export INTEGRITY_MANIFEST=integrity.json
export STRICT_INTEGRITY=true      # fail hard if tampered

 4) run
uvicorn app.main:app --reload

 5) docs
open http://127.0.0.1:8000/docs
