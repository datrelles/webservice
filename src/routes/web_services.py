from flask import Blueprint, request, jsonify
from numpy.core.defchararray import upper
from os import getenv
from datetime import datetime

from src.function_jwt import validate_token
from src import oracle

import json


web_services = Blueprint("web_services", __name__)


@web_services.before_request
def verify_token_middleware():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token,output=False)


@web_services.route("/atelier", methods=["POST"])
def atelier():

    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        sql = "select ROWNUM, P.DESCRIPCION AS PROVINCIA, C.DESCRIPCION AS CIUDAD, T.DESCRIPCION AS NOMBRE, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, REPLACE(T.RUC,'-','') as ID,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO, T.ES_TALLER_AUTORIZADO, T.TIPO_TALLER from AR_TALLER_SERVICIO_TECNICO T , AD_PROVINCIAS P, ad_cantones c WHERE T.CODIGO_EMPRESA = 20 and T.COD_PROVINCIA = P.CODIGO_PROVINCIA (+) and c.codigo_canton(+) = t.cod_canton and c.codigo_provincia(+) = t.cod_provincia and P.CODIGO_NACION = 1 and T.ANULADO = 'N'"
        cursor = cur_01.execute(sql)
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        empresas = []
        for result in array:
            empresa = dict(zip(row_headers, result))
            empresa['FECHA_ADICION'] = empresa['FECHA_ADICION'].strftime('%Y-%m-%d %H:%M:%S') if empresa['FECHA_ADICION'] is not None else None
            empresa['FECHA_MODIFICACION'] = empresa['FECHA_MODIFICACION'].strftime('%Y-%m-%d %H:%M:%S') if empresa['FECHA_MODIFICACION'] is not None else None
            empresa['FECHA_NACIMIENTO'] = empresa['FECHA_NACIMIENTO'].strftime('%Y-%m-%d') if empresa['FECHA_NACIMIENTO'] is not None else None
            empresa['ES_TALLER_AUTORIZADO'] = 'SI' if empresa['ES_TALLER_AUTORIZADO'] == 1 else 'NO'
            empresa['TIPO_TALLER'] = 'AAA' if empresa['TIPO_TALLER'] == 3 else 'A' if empresa['TIPO_TALLER'] == 1 else 'AA' if empresa['TIPO_TALLER'] == 2 else 'SIN CLASIFICACION'
            empresas.append(empresa)
        return json.dumps(empresas)
    except Exception as ex:
        raise Exception(ex)
    return response_body

@web_services.route("/atelier_by_code", methods=["GET"])
def atelier_by_id():

    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        id = request.args.get('id', None)
        id = str(upper(id))
        sql = "select ROWNUM, P.DESCRIPCION AS PROVINCIA, C.DESCRIPCION AS CIUDAD, T.DESCRIPCION AS NOMBRE, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, REPLACE(T.RUC,'-','') as ID,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO, T.ES_TALLER_AUTORIZADO, T.TIPO_TALLER from AR_TALLER_SERVICIO_TECNICO T , AD_PROVINCIAS P, ad_cantones c WHERE T.CODIGO_EMPRESA = 20 and T.COD_PROVINCIA = P.CODIGO_PROVINCIA (+) and c.codigo_canton(+) = t.cod_canton and c.codigo_provincia(+) = t.cod_provincia and REPLACE(T.RUC,'-','') = replace(:id,'-','') and P.CODIGO_NACION = 1 and T.ANULADO = 'N'"
        cursor = cur_01.execute(sql, [id])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        empresas = []
        for result in array:
            empresa = dict(zip(row_headers, result))
            empresa['FECHA_ADICION'] = empresa['FECHA_ADICION'].strftime('%Y-%m-%d %H:%M:%S') if empresa['FECHA_ADICION'] is not None else None
            empresa['FECHA_MODIFICACION'] = empresa['FECHA_MODIFICACION'].strftime('%Y-%m-%d %H:%M:%S') if empresa['FECHA_MODIFICACION'] is not None else None
            empresa['FECHA_NACIMIENTO'] = empresa['FECHA_NACIMIENTO'].strftime('%Y-%m-%d') if empresa['FECHA_NACIMIENTO'] is not None else None
            empresa['ES_TALLER_AUTORIZADO'] = 'SI' if empresa['ES_TALLER_AUTORIZADO'] == 1 else 'NO'
            empresa['TIPO_TALLER'] = 'SIN CLASIFICACION' if empresa['TIPO_TALLER'] == 0 else 'A' if empresa['TIPO_TALLER'] == 1 else 'AA' if empresa['TIPO_TALLER'] == 2 else 'AAA'
            empresas.append(empresa)
        return json.dumps(empresas)
    except Exception as ex:
        raise Exception(ex)
    return response_body

@web_services.route("/pedidos", methods=["GET"])
def pedido_by_code():

    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        code = request.args.get('code', None)
        id = request.args.get('id', None)
        if code is None or id is None:
            return jsonify(
                {"error": "Se requieren ambos parámetros 'PEDIDO EXTERNO(code)' Y 'RUC (id)' en la solicitud."}), 400
        sql = """select V.pedido, V.GUIA, V.CODIGO,
                V.chasis, V.motor, V.RAM, V.MARCA, V.MODELO, V.COLOR, V.ANIO,
                V.PAIS_ORIGEN,  V.CLASE, V.TIPO, V.CILINDRAJE
                from VT_PED_GUIAS_LAGANGA V
                where V.IDENTIFICACION_DESTINATARIO       =             :id
                AND   V.PEDIDO                =             :code"""

        cursor = cur_01.execute(sql, [id, code])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        pedidos = []
        for result in array:
            pedido = dict(zip(row_headers, result))
            pedidos.append(pedido)
        return json.dumps(pedidos)
    except Exception as ex:
        raise Exception(ex)
    return response_body

@web_services.route("/pedidos_by_date", methods=["GET"])
def pedido_by_date():

    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        from_date = request.args.get('fecha_desde', None)
        to_date = request.args.get('fecha_hasta', None)
        id = request.args.get('id', None)
        if from_date is None or id is None or to_date is None:
            return jsonify(
                {"error": "Se requieren parámetros 'RUC (id)' y fechas en la solicitud."}), 400
        try:
            from_date_n = datetime.strptime(from_date, '%d/%m/%Y')
            to_date_n = datetime.strptime(to_date, '%d/%m/%Y')
            if from_date_n > to_date_n:
                return jsonify(
                    {"error": "Fecha Desde es mayor a Fecha hasta"}), 400
        except Exception as ex:
            return jsonify(
                        {"error": "Formato de fechas incorrecto"}), 400

        sql = """select *
                from VT_PED_GUIAS_LAGANGA V
                where V.IDENTIFICACION_DESTINATARIO = :id
                AND V.FECHA >= TO_DATE(:from_date, 'DD/MM/YYYY')  
                AND V.FECHA <= TO_DATE(:to_date, 'DD/MM/YYYY')"""
        cursor = cur_01.execute(sql, [id, from_date, to_date])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        pedidos = []
        for result in array:
            pedido = dict(zip(row_headers, result))
            pedido['FECHA'] = pedido['FECHA'].strftime('%Y-%m-%d') if pedido['FECHA'] is not None else None
            pedidos.append(pedido)
        return json.dumps(pedidos)
    except Exception as ex:
        raise Exception(ex)
    return response_body

@web_services.route('/api-packing-list-by-code', methods = ['GET'])
def byCode():
    class create_dict(dict):

        # __init__ function
        def __init__(self):
            self = dict()

            # Function to add key:value

        def add(self, key, value):
            self[key] = value

    code = request.args.get('code')
    code = code.upper()
    token = request.headers['Authorization'].split(" ")[1]
    info = validate_token(token, output=True)
    user = info['username']
    password = info['password']
    array = oracle.execute_sql(
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where p.empresa = 20 and p.cod_producto = v.COD_PRODUCTO(+) AND p.empresa = v.empresa(+) and p.cod_chasis = v.NUMERO_SERIE(+) and P.COD_CHASIS = '+ "'"+code+"'",user,password)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"CODPRODUC":row[1],"CODMOTOR":row[2],"CODCHASIS":row[3], "CPN":row[4], "YEAR":row[5],"COLOR":row[6],"CILINDRAJE":row[7],"TONELAJE":row[8], "OCUPANTES":row[9], "MODELO":row[10],"CLASE":row[11], "SUBCLASE":row[12], "FECHA CREACION":row[13], "FECHA MODIFICACION":row[14], "CODIGO LIQUIDACION":row[15], "IMPORTACION":row[16]}))
    stud_json = json.dumps(mydict, indent=2, default=str, ensure_ascii=False).encode('utf8')
    return stud_json


@web_services.route('/api-packing-list', methods = ['GET'])
def byYear():
    class create_dict(dict):

        # __init__ function
        def __init__(self):
            self = dict()

            # Function to add key:value

        def add(self, key, value):
            self[key] = value

    year = request.args.get('year')

    if year == None:
        year = 'P.ANIO'
    token = request.headers['Authorization'].split(" ")[1]
    info = validate_token(token, output=True)
    user = info['username']
    password = info['password']
    array = oracle.execute_sql(
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where p.empresa = 20 and p.cod_producto = v.COD_PRODUCTO(+) AND p.empresa = v.empresa(+) and   p.cod_chasis = v.NUMERO_SERIE(+) and P.anio = '+year,user,password)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0],({"CODPRODUC":row[1],"CODMOTOR":row[2],"CODCHASIS":row[3], "CPN":row[4], "YEAR":row[5],"COLOR":row[6],"CILINDRAJE":row[7],"TONELAJE":row[8], "OCUPANTES":row[9], "MODELO":row[10],"CLASE":row[11], "SUBCLASE":row[12], "FECHA CREACION":row[13], "FECHA MODIFICACION":row[14], "CODIGO LIQUIDACION":row[15], "IMPORTACION":row[16]}))
    stud_json = json.dumps(mydict, indent=2, default=str, ensure_ascii=False).encode('utf8')
    return stud_json

@web_services.route('/sri_motos_matriculas', methods=['POST'])
def cargaMatriculas():
    try:
        data = request.get_json()
        print(data)
        anio = data.get('anio')
        page_size = 100
        page_number = data.get('page',1)
        offset = (page_number-1)*page_size
        print(anio)
        # Modifica tu consulta SQL para incluir LIMIT y OFFSET
        # Obtener la conexión y el cursor
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        sql = """SELECT CAMVCPN
                 FROM (
                     SELECT CAMVCPN, ROW_NUMBER() OVER (ORDER BY CAMVCPN) AS r
                     FROM vt_vta_consigna_motos
                 )
                 WHERE r BETWEEN :offset + 1 AND :offset + :page_size"""

        result = cur_01.execute(sql, {'page_size': page_size, 'offset': offset}).fetchall()
        json_result = [{'CAMVCPN': row[0]} for row in result]
        cur_01.close()
        c.close()

        return jsonify({'result': json_result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web_services.route('/sri_motos_matriculas_save', methods=['POST'])
def saveMatriculas():
    try:
        data = request.get_json()
        # Obtener la conexión y el cursor
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()

        for record in data:
            if record.get("PLACA") == '':
                print('vacion')
                continue

            # Formatear las fechas desde los datos JSON
            fecha_ultima_matricula = datetime.strptime(record["FECHA ULTIMA MATRICULA"], '%d/%m/%Y')
            fecha_de_compra = datetime.strptime(record[" FECHA DE COMPRA"], '%d/%m/%Y')
            fecha_caducidad_matricula = datetime.strptime(record["FECHA CADUCIDAD MATRICULA"], '%d/%m/%Y')
            fecha_de_revision = datetime.strptime(record[" FECHA DE REVISION"], '%d/%m/%Y')
            # Verificar si el registro ya existe
            select_query = "SELECT COUNT(*) FROM ST_MATRICULACION_MOTOS WHERE PLACA = :1"
            cur_01.execute(select_query, (record["PLACA"],))
            result = cur_01.fetchone()

            # Si el registro ya existe, continuar a la siguiente iteración
            if result and result[0] > 0:
                print(f"Registro con PLACA {record['PLACA']} ya existe. Saltando inserción.")
                continue

            # Preparar la consulta de inserción
            insert_query = """
                INSERT INTO ST_MATRICULACION_MOTOS (
                    EMPRESA, NOMBRE, TIPO_IDENTIFICACION, IDENTIFICACION, DIRECCION, TELEFONO,
                    PLACA, CAMV_O_CPN, MARCA, MODELO, PAIS, ANIO, CILINDRAJE, CLASE, SERVICIO,
                    FECHA_ULTIMA_MATRICULA, FECHA_DE_COMPRA, FECHA_CADUCIDAD_MATRICULA,
                    ANIO_ULTIMO_PAGO, CANTON, ENTIDAD_POLICIAL, ESTADO_MATRICULADO,
                    ESTADO_EXONERACION, COLOR_1, PROHIBICION_DE_ENAJENAR, COLOR_2,
                    FECHA_DE_REVISION, TIPO_DE_USO_DEL_VEHICULO, ESTADO, OBSERVACION
                ) VALUES (
                    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16,
                    :17,:18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30
                )
            """
            values = (
                20,  # Replace with the correct value for EMPRESA
                record["NOMBRE"],
                record["TIPO IDENTIFICACION"],
                record["IDENTIFICACION"],
                record["DIRECCION"],
                record["TELEFONO"],
                record["PLACA"],
                record[" CAMV O CPN"],
                record["MARCA"],
                record[" MODELO"],
                record["PAIS"],
                record[" ANO"],
                record["CILINDRAJE"],
                record["CLASE"],
                record[" SERVICIO"],
                fecha_ultima_matricula,
                fecha_de_compra,
                fecha_caducidad_matricula,
                record[" ANO ULTIMO PAGO"],
                record["CANTON"],
                record[" ENTIDAD POLICIAL"],
                record["ESTADO MATRICULADO"],
                record[" ESTADO EXONERACION"],
                record["COLOR 1"],
                record[" PROHIBICION DE ENAJENAR"],
                record["COLOR 2"],
                fecha_de_revision,
                record["TIPO DE USO DEL VEHICULO"],
                record["ESTADO"],
                record[" OBSERVACION"]
            )

            # Ejecutar la consulta de inserción
            cur_01.execute(insert_query, values)

        # Confirmar la transacción y cerrar los cursores y la conexión
        c.commit()
        cur_01.close()
        c.close()

        return jsonify({'result': 'complete'})

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500



