# for seting up backend 
```bash
git clone 
python -m venv venv
venv/scripts/activate
pip install -r reqiurements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
