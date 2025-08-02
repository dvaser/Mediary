from flask import Flask, request, jsonify, send_from_directory
from transformers import pipeline

app = Flask(__name__, static_folder='static', static_url_path='')

# Modeli yükleyin
generator = pipeline('text-generation', model='gpt2')

# API endpoint
@app.route('/api/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt', '')
    out = generator(prompt, max_length=50)
    return jsonify(out)

# Statik dosyaları sun
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    return send_from_directory('static', path)

if __name__ == '__main__'
    app.run(debug=True, port=5000)