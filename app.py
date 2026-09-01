import os
import random
import tempfile
import logging
from flask import Flask, jsonify, render_template, request
from faster_whisper import WhisperModel

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None

COLORS = [
    "#ffb3c6", "#ffc6a8", "#ffe28a", "#bfe8c8", "#9ed8ff",
    "#b9b7ff", "#e3b3ff", "#f4a6a6", "#8fd8d8", "#c9c9c9",
    "#d8c3a5", "#b8e0d2"
]


def get_model():
    global _model
    if _model is None:
        model_name = os.getenv("WHISPER_MODEL", "tiny")
        logger.info("Loading Whisper model: %s", model_name)
        _model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
        )
    return _model


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/analyze")
def analyze():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file was received."}), 400

    audio = request.files["audio"]
    if not audio or not audio.filename:
        return jsonify({"error": "The audio file is empty."}), 400

    suffix = os.path.splitext(audio.filename)[1] or ".webm"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp_path = temp.name
            audio.save(temp_path)

        model = get_model()
        segments, info = model.transcribe(
            temp_path,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        if not transcript:
            transcript = "No clear speech was detected."

        # The color is intentionally random. It has no emotion or psychological meaning.
        color = random.choice(COLORS)

        return jsonify({
            "color": color,
            "transcript": transcript,
            "language": getattr(info, "language", "unknown"),
            "message": "Your random color is ready."
        })

    except Exception as exc:
        logger.exception("Audio analysis failed")
        return jsonify({"error": f"Analysis failed: {str(exc)}"}), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "The recording is too large."}), 413


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
