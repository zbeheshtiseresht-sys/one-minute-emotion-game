ONE MINUTE, ONE COLOR

LOCAL:
1) Open this folder in VS Code.
2) Run: py -m pip install -r requirements.txt
3) Run: py app.py
4) Open: http://127.0.0.1:5000

RENDER:
- Create a Web Service from this repository.
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app --workers 1 --timeout 180
- The app uses HTTPS on Render, so phone microphone access works.

IMPORTANT:
- The first analysis can take longer because the Whisper model is loaded/downloaded.
- The generated color is RANDOM and has no emotional or psychological meaning.
