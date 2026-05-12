from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'project': 'MacroLab v7',
        'status': 'online',
        'message': 'API de Inteligência Macroeconômica pronta.'
    })

@app.route('/predict', methods=['GET'])
def predict():
    # Aqui entrará a lógica de carregamento do modelo e predição
    return jsonify({'message': 'Endpoint de predição em desenvolvimento.'})

if __name__ == '__main__':
    app.run(debug=True, port=8081)