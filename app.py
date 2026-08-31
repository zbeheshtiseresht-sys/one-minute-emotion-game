import os, uuid, tempfile
from flask import Flask, render_template, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)
print('Loading local Whisper model...')
whisper_model = WhisperModel('base', device='cpu', compute_type='int8')

# Deliberately arbitrary palette: colors are not intuitive emotion symbols.
COLORS = {
    'happy': '#B8C7FF', 'sad': '#F3C7D3', 'angry': '#C8B08A',
    'anxious': '#D4C4E8', 'calm': '#BFDCCB', 'excited': '#FFD1A8',
    'lonely': '#C7D2E0', 'confused': '#E7D8A8', 'neutral': '#D7D7D7'
}

KEYWORDS = {
    'happy': ['happy','great','good','wonderful','love','joy','خوشحال','عالی','خوب','دوست دارم','لذت'],
    'sad': ['sad','cry','crying','bad','upset','hurt','غمگین','ناراحت','گریه','دلم گرفته'],
    'angry': ['angry','mad','furious','hate','annoyed','عصبانی','خشمگین','متنفر','اعصابم'],
    'anxious': ['anxious','anxiety','worried','worry','stress','stressed','scared','نگران','استرس','اضطراب','ترس'],
    'calm': ['calm','peaceful','relaxed','quiet','آرام','آرامش','راحت'],
    'excited': ['excited','thrilled','can\'t wait','هیجان','مشتاق'],
    'lonely': ['lonely','alone','isolated','تنها','تنهایی'],
    'confused': ['confused','confusing','lost','نمی دانم','نمیدانم','گیج']
}

def analyze_text(text):
    lower = text.lower()
    scores = {emotion: sum(lower.count(k) for k in words) for emotion, words in KEYWORDS.items()}
    emotion = max(scores, key=scores.get)
    total = sum(scores.values())
    if total == 0:
        emotion = 'neutral'
        confidence = 50.0
    else:
        confidence = round(50 + 50 * scores[emotion] / total, 1)
    return emotion, confidence

@app.get('/')
def home():
    return render_template('index.html')

@app.post('/api/analyze')
def analyze():
    audio = request.files.get('audio')
    if not audio:
        return jsonify(error='No audio received.'), 400
    path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}.webm')
    audio.save(path)
    try:
        segments, _ = whisper_model.transcribe(path, beam_size=3, vad_filter=True)
        transcript = ' '.join(s.text.strip() for s in segments).strip()
        if not transcript:
            return jsonify(error='I could not understand the audio. Please try again.'), 400
        emotion, confidence = analyze_text(transcript)
        return jsonify(transcript=transcript, emotion=emotion, confidence=confidence, color=COLORS[emotion])
    except Exception as e:
        return jsonify(error=f'Analysis failed: {str(e)}'), 500
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
