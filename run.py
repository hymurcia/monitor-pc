"""
Script de inicio para el Monitor de PC.
Este script carga la configuración desde .env e inicia el servidor Flask.
"""

from app import app
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener configuración
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

if __name__ == '__main__':
    print(f"Iniciando Monitor de PC en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)