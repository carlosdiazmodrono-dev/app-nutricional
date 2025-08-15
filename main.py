import functions_framework
from flask import jsonify
import google.generativeai as genai
import os

# --- Configuración de CORS (no cambia) ---
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# --- Configuración del modelo de IA ---
# Esto se configura una sola vez cuando el servicio arranca
# No es necesario poner una API Key, en Cloud Run se autentica solo.
genai.configure(
    project_id=os.environ.get("GCLOUD_PROJECT"),
)
model = genai.GenerativeModel('gemini-1.5-flash')


@functions_framework.http
def analizar_comida(request):
    # Manejo de la petición CORS (no cambia)
    if request.method == 'OPTIONS':
        return add_cors_headers(jsonify({}))

    # Verificación de que se envía una imagen (no cambia)
    if 'image' not in request.files:
        error_response = jsonify({'error': 'No se encontró ningún archivo de imagen en la petición.'})
        return add_cors_headers(error_response), 400

    image_file = request.files['image']

    # --- NUEVA LÓGICA DE IA ---
    try:
        # 1. Lee los bytes de la imagen subida
        image_bytes = image_file.read()

        # 2. Define el prompt (la instrucción para la IA)
        prompt_text = "Analiza esta imagen de un plato de comida. Describe los ingredientes principales que ves en una lista simple, separados por comas. Sé conciso y directo. Ejemplo: pasta, salsa de tomate, albahaca, queso parmesano."

        # 3. Envía la imagen y el prompt a Gemini
        print("Enviando petición a Gemini...")
        response = model.generate_content([prompt_text, {'mime_type': 'image/jpeg', 'data': image_bytes}])
        print("Respuesta recibida de Gemini.")

        # 4. Extrae el texto de la respuesta de la IA
        ingredientes = response.text.strip()

        # 5. Prepara y envía la respuesta al usuario
        success_response = jsonify({
            'ingredientes_detectados': ingredientes
        })
        return add_cors_headers(success_response), 200

    except Exception as e:
        # Manejo de posibles errores con la IA
        print(f"Error al contactar con la API de Gemini: {e}")
        error_response = jsonify({'error': 'Hubo un problema al analizar la imagen con la IA.'})
        return add_cors_headers(error_response), 500

