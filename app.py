from flask import Flask, request, jsonify, send_from_directory
from model.ask_question import ask_question, chat

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/api/ask_stage1', methods=['POST'])
def handle_question_stage1():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'Soru boş olamaz'}), 400

    try:
        answer = ask_question(user_q=question, stage=1)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ask_stage2', methods=['POST'])
def handle_question_stage2():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'Soru boş olamaz'}), 400

    try:
        answer = ask_question(user_q=question, stage=2)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': 'Soru boş olamaz'}), 400

    try:
        answer = chat(user_q=question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Statik dosyaları (HTML, CSS, JS) servis et ---
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
