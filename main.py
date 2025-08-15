import functions_framework
from flask import jsonify
import google.generativeai as genai
import os
import traceback # Importamos esta librería para un mejor registro de errores

# --- Configuración de CORS ---
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# --- Configuración del modelo de IA ---
try:
    # Esta configuración funciona automáticamente en Cloud Run
    project_id = os.environ.get("GCLOUD_PROJECT")
    genai.configure(
        project_id=project_id,
    )
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Modelo Gemini configurado correctamente.")
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo configurar el modelo Gemini. Error: {e}")
    model = None # Dejamos el modelo como None si falla la configuración

@functions_framework.http
def analizar_comida(request):
    # Manejo de CORS
    if request.method == 'OPTIONS':
        return add_cors_headers(jsonify({}))

    # Si el modelo no se pudo inicializar, devolvemos un error.
    if model is None:
        error_response = jsonify({'error': 'El modelo de IA no está disponible.'})
        return add_cors_headers(error_response), 500
        
    # Verificación de que se envía una imagen
    if 'image' not in request.files:
        error_response = jsonify({'error': 'No se encontró ningún archivo de imagen.'})
        return add_cors_headers(error_response), 400

    image_file = request.files['image']
    
    # --- Lógica de IA con registro de errores mejorado ---
    try:
        image_bytes = image_file.read()

        prompt_text = "Analiza esta imagen de un plato de comida. Describe los ingredientes principales que ves en una lista simple, separados por comas. Sé conciso y directo. Ejemplo: pasta, salsa de tomate, albahaca, queso parmesano."
        
        print("Enviando petición a Gemini...")
        response = model.generate_content([prompt_text, {'mime_type': 'image/jpeg', 'data': image_bytes}])
        print("Respuesta recibida de Gemini.")

        ingredientes = response.text.strip()

        success_response = jsonify({
            'ingredientes_detectados': ingredientes
        })
        return add_cors_headers(success_response), 200

    except Exception as e:
        # Este es el cambio clave: imprimimos el error completo en los logs.
        print("!!!!!!!!!! ERROR DURANTE LA LLAMADA A GEMINI !!!!!!!!!!")
        print(traceback.format_exc()) # Imprime el traceback completo
        print(f"Excepción: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        error_response = jsonify({'error': 'Hubo un problema al analizar la imagen con la IA.'})
        return add_cors_headers(error_response), 500
