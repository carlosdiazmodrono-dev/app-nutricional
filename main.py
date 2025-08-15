import functions_framework
from flask import jsonify

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@functions_framework.http
def analizar_comida(request):
    if request.method == 'OPTIONS':
        return add_cors_headers(jsonify({}))

    if 'image' not in request.files:
        error_response = jsonify({'error': 'No se encontró ningún archivo de imagen en la petición.'})
        return add_cors_headers(error_response), 400

    file = request.files['image']
    print(f"Imagen recibida: {file.filename}, Tamaño: {file.content_length} bytes")

    success_response = jsonify({
        'message': '¡Imagen recibida correctamente por el backend!',
        'filename': file.filename,
        'content_type': file.content_type
    })

    return add_cors_headers(success_response), 200
