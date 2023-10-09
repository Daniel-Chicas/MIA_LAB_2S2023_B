from flask import Flask, jsonify, request
from flask_cors import CORS 
import main

# Flask App
app = Flask(__name__)

# Configuración de los CORS
CORS(app, resources={r"/*": {"origins": "*", "methos": [
    "GET", "POST", "PUT", "DELETE"], "headers": "Authorization"}})

# Ruta de inicio de nuestra API
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Bienvenido a la API de Python con Flask"})

# Ruta para obtener información de un usuario
@app.route('/saludo', methods=['POST'])
def saludo():
    #Obtener los datos enviados desde una petición
    nombre = request.json['nombre']
    apellido = request.json['apellido']
    return jsonify({"message": "Hola "+nombre+" "+apellido})

# Ruta para obtener información de un usuario
@app.route('/exec', methods=['POST'])
def exec():
    #Obtener los datos enviados desde una petición
    comando = request.json['comandos']
    for i in comando:
        texto = i
        tk = main.Scanner.comando(texto)
        if texto:
            if main.Scanner.comparar(texto, "PAUSE"):
                print("************** FUNCION PAUSE **************")
                input("Presione enter para continuar...")
                continue
            texto = texto[len(tk) + 1:]
            tks = main.Scanner.separar_tokens(texto)
            main.Scanner.funciones(tk, tks)
    return jsonify({"message": "Ejecución terminada"})




# Iniciar nuestro servidor
if __name__ == '__main__':
    print("Servidor iniciado")
    app.run(debug=True, port=4000, host='0.0.0.0')