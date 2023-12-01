from flask import  Blueprint, request, jsonify
from os import getenv
from datetime import datetime

from src import oracle
import json

image_service = Blueprint("image_service", __name__)

#BLOB JPG BY CODE
@image_service.route('/img', methods = ['GET'])
def obtener_archivos_material():
    try:
        # Realiza la conexión a la base de datos
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()

        # Escribe la consulta SQL para obtener los archivos relacionados a un material específico
        cod_code = request.args.get('code')
        if cod_code is None and cod_enterprise is None:
            return jsonify({"error": "Se requiere el parámetro 'cod_material' en la solicitud."}), 400

        sql = f"SELECT IMAGEN FROM st_material_imagen WHERE COD_MATERIAL = :cod_code"

        # Ejecuta la consulta SQL
        cursor = cur_01.execute(sql, [cod_code])

        # Obtiene el primer resultado de la consulta
        resultado = cursor.fetchone()

        if resultado:
            # Obtiene el contenido BLOB del resultado
            blob_data = resultado[0].read()

            # Cierra la conexión a la base de datos
            c.close()

            # Devuelve el contenido BLOB como una respuesta binaria
            return blob_data, 200, {'Content-Type': 'image/jpeg'}
        else:
            # En caso de que no se encuentre el archivo
            return jsonify({"error": "No se encontraron archivos para el material especificado."}), 404

    except Exception as ex:
        print(ex)
        return jsonify({"error": "Ocurrió un error al recuperar los archivos"}),500