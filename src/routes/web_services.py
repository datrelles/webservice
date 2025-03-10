from flask import Blueprint, request, jsonify
from numpy.core.defchararray import upper
from os import getenv
from datetime import datetime, date
import cx_Oracle
from src.function_jwt import validate_token
from src import oracle
import json
import random

web_services = Blueprint("web_services", __name__)


@web_services.before_request
def verify_token_middleware():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token, output=False)



@web_services.route("/atelier", methods=["POST"])
def atelier():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        sql = "select ROWNUM, P.DESCRIPCION AS PROVINCIA, C.DESCRIPCION AS CIUDAD, T.DESCRIPCION AS NOMBRE, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, REPLACE(T.RUC,'-','') as ID,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO, T.ES_TALLER_AUTORIZADO, T.TIPO_TALLER, T.CUPO_X_HORA, T.CODIGO from AR_TALLER_SERVICIO_TECNICO T , AD_PROVINCIAS P, ad_cantones c WHERE T.CODIGO_EMPRESA = 20 and T.COD_PROVINCIA = P.CODIGO_PROVINCIA (+) and c.codigo_canton(+) = t.cod_canton and c.codigo_provincia(+) = t.cod_provincia and P.CODIGO_NACION = 1 and T.ANULADO = 'N'"

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
        sql = "select ROWNUM, P.DESCRIPCION AS PROVINCIA, C.DESCRIPCION AS CIUDAD, T.DESCRIPCION AS NOMBRE, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, REPLACE(T.RUC,'-','') as ID,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO, T.ES_TALLER_AUTORIZADO, T.TIPO_TALLER, T.CUPO_X_HORA, T.CODIGO from AR_TALLER_SERVICIO_TECNICO T , AD_PROVINCIAS P, ad_cantones c WHERE T.CODIGO_EMPRESA = 20 and T.COD_PROVINCIA = P.CODIGO_PROVINCIA (+) and c.codigo_canton(+) = t.cod_canton and c.codigo_provincia(+) = t.cod_provincia and REPLACE(T.RUC,'-','') = replace(:id,'-','') and P.CODIGO_NACION = 1 and T.ANULADO = 'N'"
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



@web_services.route('/api-packing-list-by-code', methods=['GET'])
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


@web_services.route('/api-packing-list', methods=['GET'])
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


# Api Product Img+Info
@web_services.route('/imageByCode', methods=['GET'])
def imageByCode():
    try:
        # buscar imagen
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        # Escribe la consulta
        cod_code = request.args.get('code')
        if cod_code is None:
            return jsonify({"error": "Se requiere el parámetro 'cod_material' en la solicitud."}), 400
        sql_query = """
            SELECT 
            P.COD_PRODUCTO,
            P.NOMBRE,
            P.IVA,
            P.ICE,
            M.NOMBRE AS MARCA,
            BUF.ES_BUFFER AS CONTROL_BUFFER,
            C.nombre color,
            T.NOMBRE categoria
            FROM 
            PRODUCTO P
            JOIN 
            MARCA M ON  P.COD_MARCA= M.COD_MARCA
            JOIN
            st_material_imagen IM ON  P.COD_PRODUCTO= IM.COD_MATERIAL
            JOIN
            st_producto_buffer BUF ON  P.COD_PRODUCTO= BUF.COD_PRODUCTO
            JOIN
            st_color c ON p.partida= c.cod_color
            JOIN 
            TG_MODELO_ITEM T ON P.COD_MODELO_CAT1=  T.COD_MODELO AND T.COD_ITEM = P.COD_ITEM_CAT1
            WHERE 
            P.COD_PRODUCTO=: cod_code
            AND  
            P.EMPRESA = 20
            AND
            T.EMPRESA = P.EMPRESA

"""
        # ejecuta la consulta SQL
        cursor = cur_01.execute(sql_query, {'cod_code': cod_code})
        resultado = cursor.fetchone()
        if resultado:
            code = resultado[0]
            name = resultado[1]
            iva = resultado[2]
            ice = resultado[3]
            marca = resultado[4]
            buffer = resultado[5]
            color = resultado[6]
            category = resultado[7]
            host = request.host
            imageurl = f"http://{host}/imageApi/img?code={code}"
            response_data = {
                "img": imageurl,
                "code": code,
                "name": name,
                "iva": iva,
                "ice": ice,
                "marca": marca,
                "buffer": buffer,
                "color": color,
                "category": category,
            }
            c.close()
            return jsonify(response_data), 200, {'Content-Type': 'application/json'}
        else:
            return jsonify({"error": "No se encontraron archivos para el material especificado."}), 404


    except Exception as ex:
        print(ex)
        return jsonify({"error": "Ocurrio un error al recuperar archivos"}), 500


@web_services.route('/searchProduct', methods=['GET'])
def searchProduct():
    try:
        # buscar imagen
        page = int(request.args.get('page'))
        items_per_page = 50
        offset = (page - 1) * items_per_page
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        # Escribe la consulta
        sql_query = """
            SELECT
            P.COD_PRODUCTO,
            P.NOMBRE,
            P.IVA,
            P.ICE,
            CASE 
                WHEN M.NOMBRE = 'SHINERAY - REPUESTOS' THEN 'SHINERAY'
                ELSE M.NOMBRE
            END AS MARCA,
            BUF.ES_BUFFER AS CONTROL_BUFFER,
            C.nombre color,
            T.NOMBRE categoria_SKU,
            l.cod_agencia,
            b.bodega,
            b.nombre,
            substr(ks_reporte.tipo_modelo_cat(p.empresa, p.cod_producto),1,INSTR(ks_reporte.tipo_modelo_cat(p.empresa, p.cod_producto),CHR(9))-1) categoria_moto,
            substr(substr(ks_reporte.tipo_modelo_cat(p.empresa, p.cod_producto),INSTR(ks_reporte.tipo_modelo_cat(p.empresa, p.cod_producto),CHR(9))+1),1,instr(substr(ks_reporte.tipo_modelo_cat(p.empresa, p.cod_producto),INSTR(ks_reporte.tipo_modelo_cat(p.empresa, p.cod_producto),CHR(9))+1),CHR(9))-1) modelo_moto,
            l.cod_unidad,
            l.precio,
            KS_INVENTARIO.consulta_existencia(20,l.cod_agencia,P.COD_PRODUCTO,'U',TO_DATE(sysdate, 'YYYY/MM/DD'),1,'Z',1) STOCK
            FROM 
            PRODUCTO P, 
            MARCA M,
            st_material_imagen IM,
            st_producto_buffer BUF,
            ST_COLOR C ,
            TG_MODELO_ITEM T,
            ST_LISTA_PRECIO l,
            bodega b
             
            WHERE     P.EMPRESA                     = 20
            AND       M.COD_MARCA                   = P.COD_MARCA
            AND       M.EMPRESA                     = P.EMPRESA
            AND       IM.COD_TIPO_MATERIAL          = 'PRO'
            AND       IM.COD_MATERIAL               = P.COD_PRODUCTO
            AND       IM.EMPRESA                    = P.EMPRESA
            AND       BUF.COD_PRODUCTO              = P.COD_PRODUCTO
            AND       BUF.EMPRESA                   = P.EMPRESA
            AND       C.COD_COLOR                   = P.PARTIDA
            AND       T.EMPRESA                     = P.EMPRESA
            AND       T.COD_MODELO                  = P.COD_MODELO_CAT1
            AND       T.COD_ITEM                    = P.COD_ITEM_CAT1
            AND       L.COD_PRODUCTO                = P.COD_PRODUCTO
            AND       L.COD_AGENCIA                 = 50
            AND       L.COD_UNIDAD                  = P.COD_UNIDAD
            AND       L.COD_FORMA_PAGO              = 'EFE'
            AND       L.COD_DIVISA                  = 'DOLARES'
            AND       L.COD_MODELO_CLI              = 'CLI1'
            AND       L.COD_ITEM_CLI                = 'CF'
            AND       L.ESTADO_GENERACION           = 'R' 
            AND      (L.FECHA_FINAL                 IS NULL
            OR        L.FECHA_FINAL                 >= TRUNC(SYSDATE))
            and       b.empresa                     = l.empresa
            and       b.bodega                      = l.cod_agencia

"""
        # ejecuta la consulta SQL
        cursor = cur_01.execute(sql_query)
        resultados = cursor.fetchall()
        paginated_results = resultados[offset:offset + items_per_page]

        if paginated_results:
            response_data = []
            for resultado in paginated_results:
                code = resultado[0]
                name = resultado[1]
                iva = resultado[2]
                ice = resultado[3]
                marca = resultado[4]
                buffer = resultado[5]
                color = resultado[6]
                category = resultado[7]
                cod_agencia = resultado[8]
                bodega = resultado[9]
                nombre = resultado[10]
                motoCategory = resultado[11]
                motoModel = resultado[12]
                cod_unidad = resultado[13]
                precio = resultado[14]
                stock = resultado[15]
                host = '201.218.59.182:5000'
                imageurl = f"http://{host}/imageApi/img?code={code}"

                response_data.append({
                    "img": imageurl,
                    "code": code,
                    "name": name,
                    "iva": iva,
                    "ice": ice,
                    "marca": marca,
                    "buffer": buffer,
                    "color": color,
                    "category_sku": category,
                    "codigo agencia": cod_agencia,
                    "bodega": bodega,
                    "nombre": nombre,
                    "moto_Category": motoCategory,
                    "moto_Model": motoModel,
                    "cod_unidad": cod_unidad,
                    "precio": precio,
                    "stock": stock
                })

            c.close()
            return jsonify(response_data), 200, {'Content-Type': 'application/json'}
        else:
            c.close()
            return jsonify({"error": "No se encontraron archivos para el material especificado."}), 404


    except Exception as ex:
        print(ex)
        return jsonify({"error": "Ocurrio un error al recuperar archivos"}), 500


@web_services.route('/sri_motos_matriculas', methods=['POST'])
def cargaMatriculas():
    try:
        data = request.get_json()
        print(data)
        anio = data.get('anio')
        page_size = 300
        page_number = data.get('page', 1)
        offset = (page_number - 1) * page_size
        print(anio)
        # Modifica tu consulta SQL para incluir LIMIT y OFFSET
        # Obtener la conexión y el cursor
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        sql = """SELECT CAMVCPN
                 FROM (
                     SELECT CAMVCPN, ROW_NUMBER() OVER (ORDER BY CAMVCPN) AS r
                     FROM vt_vta_consigna_motos_rep
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
            #fecha_ultima_matricula = datetime.strptime(record["FECHA ULTIMA MATRICULA"], '%d/%m/%Y')
            #fecha_de_compra = datetime.strptime(record[" FECHA DE COMPRA"], '%d/%m/%Y')
            #fecha_caducidad_matricula = datetime.strptime(record["FECHA CADUCIDAD MATRICULA"], '%d/%m/%Y')
            #fecha_de_revision = datetime.strptime(record[" FECHA DE REVISION"], '%d/%m/%Y')

            # Formatear las fechas desde los datos JSON
            fecha_ultima_matricula = None
            fecha_de_compra = None
            fecha_caducidad_matricula = None
            fecha_de_revision = None



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
                record["TIPO IDENTIFICACION"] if "TIPO IDENTIFICACION" in record else None,
                record["IDENTIFICACION"] if "IDENTIFICACION" in record else None,
                record["DIRECCION"] if "DIRECCION" in record else None,
                record["TELEFONO"] if "TELEFONO" in record else None,
                record["PLACA"] if "PLACA" in record else None,
                record[" CAMV O CPN"] if " CAMV O CPN" in record else None,
                record["MARCA"] if "MARCA" in record else None,
                record[" MODELO"] if " MODELO" in record else None,
                record["PAIS"] if "PAIS" in record else None,
                record[" ANO"] if " ANO" in record else None,
                record["CILINDRAJE"] if "CILINDRAJE" in record else None,
                record["CLASE"] if "CLASE" in record else None,
                record[" SERVICIO"] if " SERVICIO" in record else None,
                fecha_ultima_matricula if fecha_ultima_matricula else None,
                fecha_de_compra if fecha_de_compra else None,
                fecha_caducidad_matricula if fecha_caducidad_matricula else None,
                record[" ANO ULTIMO PAGO"] if " ANO ULTIMO PAGO" in record else None,
                record["CANTON"] if "CANTON" in record else None,
                record[" ENTIDAD POLICIAL"] if " ENTIDAD POLICIAL" in record else None,
                record["ESTADO MATRICULADO"] if "ESTADO MATRICULADO" in record else None,
                record[" ESTADO EXONERACION"] if " ESTADO EXONERACION" in record else None,
                record["COLOR 1"] if "COLOR 1" in record else None,
                record[" PROHIBICION DE ENAJENAR"] if " PROHIBICION DE ENAJENAR" in record else None,
                record["COLOR 2"] if "COLOR 2" in record else None,
                fecha_de_revision if fecha_de_revision else None,
                record["TIPO DE USO DEL VEHICULO"] if "TIPO DE USO DEL VEHICULO" in record else None,
                record["ESTADO"] if "ESTADO" in record else None,
                record[" OBSERVACION"] if " OBSERVACION" in record else None
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

@web_services.route('/sri_doc_elec_save', methods=['POST'])
def save_sri_doc_elec_save():
    try:
        data = request.get_json()
        # Conexión a la base de datos Oracle
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()

        for doc in data:
            # Verificar si ya existe un registro con el mismo RUC y SERIE_COMPROBANTE
            cursor.execute(
                """
                SELECT 1 FROM CONTABILIDAD.TC_DOC_ELEC_RECIBIDOS 
                WHERE ruc_emisor = :ruc_emisor AND serie_comprobante = :serie_comprobante
                """,
                {
                    'ruc_emisor': doc.get('RUC_EMISOR'),
                    'serie_comprobante': doc.get('SERIE_COMPROBANTE')
                }
            )
            exists = cursor.fetchone()

            # Si el registro ya existe, omitir la inserción
            if exists:
                continue

            # Convertir las fechas al formato adecuado si están presentes
            fecha_emision = (
                datetime.strptime(doc.get('FECHA_EMISION'), '%d/%m/%Y').strftime('%Y-%m-%d')
                if doc.get('FECHA_EMISION') else None
            )
            fecha_autorizacion = (
                datetime.strptime(doc.get('FECHA_AUTORIZACION'), '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                if doc.get('FECHA_AUTORIZACION') else None
            )

            # Ejecutar la inserción en la tabla
            cursor.execute(
                """
                INSERT INTO CONTABILIDAD.TC_DOC_ELEC_RECIBIDOS (
                    comprobante, serie_comprobante, ruc_emisor, razon_social_emisor, fecha_emision,
                    fecha_autorizacion, tipo_emision, numero_documento_modificado, identificacion_receptor,
                    clave_acceso, numero_autorizacion, importe_total, valor_sin_impuestos, iva
                ) VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), 
                          TO_DATE(:6, 'YYYY-MM-DD HH24:MI:SS'), :7, :8, :9, :10, :11, :12, :13, :14)
                """,
                (
                    doc.get('TIPO_COMPROBANTE').upper(),  # comprobante
                    doc.get('SERIE_COMPROBANTE'),  # serie_comprobante
                    doc.get('RUC_EMISOR'),  # ruc_emisor
                    doc.get('RAZON_SOCIAL_EMISOR').upper(),  # razon_social_emisor
                    fecha_emision,  # fecha_emision en formato YYYY-MM-DD
                    fecha_autorizacion,  # fecha_autorizacion en formato YYYY-MM-DD HH:MM:SS
                    'NORMAL',  # tipo_emision (valor por defecto)
                    doc.get('NUMERO_DOCUMENTO_MODIFICADO', ''),  # numero_documento_modificado
                    doc.get('IDENTIFICACION_RECEPTOR'),  # identificacion_receptor
                    doc.get('CLAVE_ACCESO'),  # clave_acceso
                    doc.get('CLAVE_ACCESO'),  # numero_autorizacion
                    float(doc.get('IMPORTE_TOTAL', 0)),  # importe_total
                    float(doc.get('VALOR_SIN_IMPUESTOS', 0)),  # valor_sin_impuestos
                    float(doc.get('IVA', 0))  # iva
                )
            )

        # Confirmar la transacción
        c.commit()
        return jsonify({'result': 'Transaction completed successfully'}), 200

    except Exception as e:
        c.rollback()  # Revertir en caso de error
        print(e)
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()


# WS MODULE WARRANTY
@web_services.route('/warranty/motorcycles', methods=['POST'])
def warranty():
    try:
        # Capturar datos del request
        dataCaso = json.loads(request.data)
        validacion_exitosa, mensaje_error = validar_campos(dataCaso)
        if not validacion_exitosa:
            return jsonify({"error": mensaje_error}), 400

        for clave, valor in dataCaso.items():
            try:
                # Intenta convertir a mayúsculas, pero si es un entero, captura la excepción
                dataCaso[clave] = str(valor).upper()
            except AttributeError:
                # Maneja la excepción si el valor no se puede convertir a mayúsculas
                print(f"Error: La clave '{clave}' tiene un valor que no se puede convertir a mayúsculas.")
        # Configuración de datos no variables
        set_non_variable_data(dataCaso)
        # Obtener información del taller
        get_taller_info(dataCaso)
        # Obtener información del motor
        get_motor_info(dataCaso)
        # Generación de Codigo comprobante y guardar Entrada en st_casos_postventa
        data_st_casos_post_venta=dataCaso.copy()
        del data_st_casos_post_venta["problemas"]
        del data_st_casos_post_venta["evidencias"]
        generate_comprobante_code(data_st_casos_post_venta, dataCaso)
        # Guardar tipo Problema
        save_cod_tipo_problema(dataCaso)
        #Guardar evidencias
        save_url_st_casos_postVenta(dataCaso)
        return jsonify({"casoData": dataCaso})
    except Exception as e:
        return jsonify({'Error en el registro del caso': str(e)}), 500
def validar_campos(data):
    campos_necesarios = [
        "nombre_caso",
        "descripcion",
        "nombre_cliente",
        "cod_tipo_identificacion",
        "identificacion_cliente",
        "cod_motor",
        "kilometraje",
        "codigo_taller",
        "cod_tipo_problema"
    ]
    for campo in campos_necesarios:
        if campo not in data:
            return False, f"Falta el campo {campo} en el JSON recibido."

    return True, None
def set_non_variable_data(data):
    data['empresa'] = 20
    data['tipo_comprobante'] = 'CP'
    fecha_formateada = datetime.strptime(data['fecha'], '%Y/%m/%d %H:%M:%S')
    data['fecha'] = fecha_formateada
    data['codigo_nacion'] = 1
    data['cod_canal'] = 5
    data['adicionado_por'] = 'WSSHIBOT'
    fecha_venta = datetime.strptime(data['fecha_venta'], '%Y/%m')
    data['fecha_venta'] = fecha_venta
    data['aplica_garantia'] = 2
    codigo_taller_responsable = data.get('codigo_taller')
    nombre_usuario_responsable = get_codigo_responsable(codigo_taller_responsable)
    data['codigo_responsable'] = nombre_usuario_responsable

def generate_comprobante_code(data, dataCaso):
    v_cod_empresa = 20
    v_cod_tipo_comprobante = 'CP'
    v_cod_agencia = 1

    query = """
                    DECLARE
                      v_cod_empresa           FLOAT := :1;
                      v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                      v_cod_agencia           FLOAT := :3;
                      v_result                VARCHAR2(50);
                    BEGIN
                      v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                  p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                  p_cod_agencia => v_cod_agencia);
                    :4 := v_result;
                    END;
                    """

    # Obtener la conexión y el cursor
    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cur = c.cursor()

    # Variable de salida para capturar el resultado
    result_var = cur.var(cx_Oracle.STRING)

    # Ejecutar la consulta
    cur.execute(query, (v_cod_empresa, v_cod_tipo_comprobante, v_cod_agencia, result_var))
    result = result_var.getvalue()
    dataCaso['cod_comprobante'] = result
    data['cod_comprobante'] = result
    # Insercion en la tabla, confirmar la transacción y cerrar el cursor y la conexión
    sql = """
    INSERT INTO ST_CASOS_POSTVENTA (
        nombre_caso, descripcion, nombre_cliente, cod_tipo_identificacion, identificacion_cliente,
        cod_motor, kilometraje, codigo_taller, cod_tipo_problema, fecha_venta, manual_garantia,
        telefono_contacto1, telefono_contacto2, e_mail1, empresa, tipo_comprobante, fecha,
        codigo_nacion, codigo_responsable, cod_canal, adicionado_por, codigo_provincia,
        codigo_canton, cod_producto, cod_distribuidor_cli, cod_comprobante, aplica_garantia
    ) VALUES (
        :nombre_caso, :descripcion, :nombre_cliente, :cod_tipo_identificacion, :identificacion_cliente,
        :cod_motor, :kilometraje, :codigo_taller, :cod_tipo_problema, :fecha_venta, :manual_garantia,
        :telefono_contacto1, :telefono_contacto2, :e_mail, :empresa, :tipo_comprobante, :fecha,
        :codigo_nacion, :codigo_responsable, :cod_canal, :adicionado_por, :codigo_provincia,
        :codigo_canton, :cod_producto, :cod_distribuidor_cli, :cod_comprobante, :aplica_garantia
    )
    """


    cur.execute(sql, data)
    c.commit()
    cur.close()
    c.close()
def get_taller_info(data):
    id_taller = data['codigo_taller']

    if not id_taller:
        return jsonify({"error": "Se requiere el campo 'codigo_taller' en la solicitud"}), 400

    query = """
                    SELECT COD_PROVINCIA, COD_CANTON
                    FROM AR_TALLER_SERVICIO_TECNICO
                    WHERE CODIGO = :1
                    """

    # Obtener la conexión y el cursor
    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cur = c.cursor()

    # Ejecutar la consulta
    cur.execute(query, (id_taller,))
    city = cur.fetchall()

    # Cerrar el cursor y la conexión
    data['codigo_provincia'] = city[0][0]
    data['codigo_canton'] = city[0][1]
    cur.close()
    c.close()
def get_motor_info(data):
    num_motor = data['cod_motor']
    if not num_motor:
        return jsonify({"error": "Se requiere el campo 'cod_motor'"})

    data_motor = oracle.infoMotor(num_motor)
    data['cod_producto'] = data_motor[1]
    data['cod_distribuidor_cli'] = data_motor[0]
def save_cod_tipo_problema(data):
    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cur = c.cursor()
    sql = """
             INSERT INTO ST_CASOS_TIPO_PROBLEMA
             (empresa, tipo_comprobante, cod_comprobante, codigo_duracion, adicionado_por, descripcion )
             VALUES
             (:empresa, :tipo_comprobante, :cod_comprobante, :codigo_duracion, :adicionado_por, :descripcion)          
          """
    problemas = data.get("problemas",[])
    problemas = problemas.replace("'", '"')
    problemas = json.loads(problemas)
    #Datos predefinidos
    empresa = 20
    cod_comprobante = data["cod_comprobante"]
    tipo_comprobante = data["tipo_comprobante"]
    adicionado_por = 'SHIBOT'

    # Iterar sobre los datos y ejecutar la insercion
    for problema in problemas:
        data = {
            'empresa': empresa,
            'tipo_comprobante': tipo_comprobante,
            'cod_comprobante': cod_comprobante,
            'codigo_duracion': problema["CODIGO_TIPO_PROBLEMA"],
            'adicionado_por': adicionado_por,
            'descripcion': problema["DESCRIPCION_DEL_PROBLEMA"],
        }
        cur.execute(sql, data)
    c.commit()
    cur.close()
    c.close()
def save_url_st_casos_postVenta(data):
    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cur = c.cursor()
    cur.execute("SELECT COUNT(*) FROM ST_CASOS_URL")
    # Obtener el número total de registros
    total_registros = cur.fetchone()[0]
    siguiente_secuencial = total_registros + 1


    sql = """
             INSERT INTO ST_CASOS_URL
             (empresa, tipo_comprobante, cod_comprobante,secuencial, url_photos, url_videos, adicionado_por )
             VALUES
             (:empresa, :tipo_comprobante, :cod_comprobante,:secuencial, :url_photos, :url_videos, :adicionado_por)          
          """
    url = data.get("evidencias", {})
    url = url.replace("'", '"')
    url = json.loads(url)
    print(url)
    print(type(url))

    #Datos predefinidos
    empresa = 20
    cod_comprobante = data["cod_comprobante"]
    tipo_comprobante = data["tipo_comprobante"]
    adicionado_por = 'SHIBOT'

    data = {
        'empresa': empresa,
        'tipo_comprobante': tipo_comprobante,
        'cod_comprobante': cod_comprobante,
        'secuencial': siguiente_secuencial,
        'url_photos': ', '.join(url["URL_IMAGENES"]),
        'url_videos': ', '.join(url["URL_VIDEOS"]),
        'adicionado_por': adicionado_por,
    }
    cur.execute(sql, data)
    c.commit()
    cur.close()
    c.close()
def get_codigo_responsable(cod_taller):
    """
    get "usuario_responsable" filtrando por empresa=20 y activo=1 y cod_taller.
    """
    try:
        empresa = 20
        activo = 1

        query = """
            SELECT usuario 
            FROM AR_TALLER_SERVICIO_USUARIO
            WHERE empresa = :empresa AND codigo_taller = :cod_taller AND activo = :activo
            AND ROWNUM = 1
        """

        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        cur.execute(query, empresa=empresa, cod_taller=cod_taller, activo=activo)
        usuario_responsable = cur.fetchone()
        print(usuario_responsable)

        cur.close()
        c.close()

        if usuario_responsable:
            return usuario_responsable[0]
        else:
            return "WSSHIBOT"

    except Exception as e:
        print(f"Error al obtener código responsable: {str(e)}")
        return "WSSHIBOT"


@web_services.route('/get/cod_tipo_problema', methods=['GET'])
def get_cod_tipo_problema():
    query = """SELECT DESCRIPCION TIPO_PROBLEMA, to_char(CODIGO_DURACION) CODIGO
                FROM AR_DURACION_REPARACION
                WHERE TIPO_DURACION='N'
                AND CODIGO_EMPRESA= :1"""

    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cur_01 = c.cursor()
    result = cur_01.execute(query, (20,)).fetchall()
    dictionary = dict(result)
    cur_01.close()
    c.close()
    return jsonify(dictionary)
@web_services.route('/status_warranty/<code_comprobante>', methods=['GET'])
def get_status_warranty(code_comprobante):
    try:
        "SELECT ESTADO, CODIGO_DURACION, DESCRIPCION FROM ST_CASOS_TIPO_PROBLEMA"

        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()
        sql = """
            SELECT ESTADO, CODIGO_DURACION, DESCRIPCION from ST_CASOS_TIPO_PROBLEMA where 
            EMPRESA = 20 AND
            TIPO_COMPROBANTE = 'CP' AND
            cod_comprobante = :code_comprobante
        """
        result = cur.execute(sql, {'code_comprobante': code_comprobante}).fetchall()
        if not result:  # Si result está vacío
            return jsonify({
                'mensaje': 'NO SE ENCONTRARON REGISTROS PARA ESE CODIGO'
            }), 404  # Devuelve un código 404 Not Found para indicar que no se encontraron registros

        dataDic = []
        #Iterara sobre la lista
        for item in result:
            estado, cod_tipo_problema, descripcion = item
            # Crear el diccionario con los datos correspondientes
            dictionary = {
                'Estado': estado,
                'cod_tipo_problema': cod_tipo_problema,
                'descripcion': descripcion
            }
            # Agregar el diccionario a la lista de resultados
            dataDic.append(dictionary)
        return jsonify(dataDic)
    except TypeError:
        return jsonify({
            'mensaje': 'Ocurrió un error al procesar la solicitud.'
        }), 500  # Devuelve un código 500 Internal Server Error si ocurre un error en el servidor
    finally:
        cur.close()  # Cierra el cursor
        c.close()    # Cierra la conexión con la base de datos

@web_services.route('/list_price_work', methods=['GET'])
def get_select_price_work():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()
        sql = "select DESCRIPCION, COSTO, CODIGO_DURACION from ST_TIPO_PRECIO"
        cur.execute(sql)
        # Fetchall para obtener todos los resultados
        result = cur.fetchall()
        # Lista para almacenar los resultados como diccionarios
        data_list = []
        for row in result:
            # Cada fila es una tupla, extraemos los valores
            descripcion, costo, codigo_duracion = row
            # Creamos un diccionario para cada fila
            row_dict = {
                'descripcion': descripcion,
                'costo': costo,
                'cod_tipo_problema': codigo_duracion
            }
            # Agregamos el diccionario a la lista de resultados
            data_list.append(row_dict)

        # Devolvemos los resultados utilizando jsonify
        return jsonify(data_list)

    except Exception as e:
        # Si ocurre algún error, devolvemos un mensaje de error
        return jsonify({
            'mensaje': 'Ocurrió un error al procesar la solicitud: {}'.format(str(e))
        }), 500  # Devolvemos un código 500 Internal Server Error

@web_services.route('/getcode/comprobante_secuencial/<tipo_comprobante>', methods=['GET'])
def get_comprobante_secuencial(tipo_comprobante):
    try:
        v_cod_empresa = 20
        if tipo_comprobante=='alistamiento':
            v_cod_tipo_comprobante = 'AL'
        if tipo_comprobante=='mantenimiento':
            v_cod_tipo_comprobante= 'MA'
        v_cod_agencia = 1
        query = """
                            DECLARE
                              v_cod_empresa           FLOAT := :1;
                              v_cod_tipo_comprobante  VARCHAR2(50) := :2;
                              v_cod_agencia           FLOAT := :3;
                              v_result                VARCHAR2(50);
                            BEGIN
                              v_result := KC_ORDEN.asigna_cod_comprobante(p_cod_empresa => v_cod_empresa,
                                                                          p_cod_tipo_comprobante => v_cod_tipo_comprobante,
                                                                          p_cod_agencia => v_cod_agencia);
                            :4 := v_result;
                            END;
                            """

        # Obtener la conexión y el cursor
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        # Variable de salida para capturar el resultado
        result_var = cur.var(cx_Oracle.STRING)

        # Ejecutar la consulta
        cur.execute(query, (v_cod_empresa, v_cod_tipo_comprobante, v_cod_agencia, result_var))
        result = result_var.getvalue()
        c.commit()
        cur.close()
        c.close()
        return jsonify({"cod_secuencial_alistamiento": result})
    except Exception as e:
        # Si ocurre algún error, devolvemos un mensaje de error
        return jsonify({
            'mensaje': 'Ocurrió un error al procesar la solicitud: {}'.format(str(e))
        }), 500  # Devolvemos un código 500 Internal Server Error

@web_services.route('/info_moto/<type_placa_or_camv>/<camv_or_placa>', methods=['GET'])
def get_infomoto_by_placa_or_camv(type_placa_or_camv, camv_or_placa):
    try:
        if type_placa_or_camv == 'placa':
            placa = camv_or_placa
            camv = ''
            chasis = ''
        if type_placa_or_camv == 'camv':
            placa = ''
            camv = camv_or_placa
            chasis=''

        if type_placa_or_camv == 'chasis':
            placa = ''
            camv = ''
            chasis = camv_or_placa


        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()
        sql = """
            SELECT A.TIPO_IDENTIFICACION, A.IDENTIFICACION, A.NOMBRE, A.DIRECCION, A.TELEFONO, A.ANIO_ULTIMO_PAGO,  A.PLACA, 
            b.COD_PRODUCTO, b.COD_MOTOR, b.COD_CHASIS, b.CAMVCPN, b.ANIO, b.COD_COLOR, c.nombre color, b.CILINDRAJE, 
            b.TONELAJE, b.OCUPANTES, b.MODELO, b.CLASE, b.SUBCLASE 
            FROM ST_MATRICULACION_MOTOS  A, ST_PROD_PACKING_LIST B, VT_VALORACION_SERIE V, st_color c
            WHERE B.EMPRESA              =  20
            AND  (B.CAMVCPN          =  :camv
            OR    B.COD_CHASIS           = :chasis
            OR    A.PLACA               = :placa
            )
            AND   B.EMPRESA              =  A.EMPRESA(+) 
            AND   B.CAMVCPN              =  A.CAMV_O_CPN (+)
            and   b.cod_producto         =  v.COD_PRODUCTO(+) 
            AND   b.empresa              =  v.empresa(+) 
            and   b.cod_chasis           =  v.NUMERO_SERIE(+) 
            and   b.cod_color (+)        =  c.cod_color        
        """
        result = cur.execute(sql, {'camv': camv, 'placa': placa, 'chasis': chasis}).fetchone()  # Añadir () para llamar a fetchone
        cur.close()
        c.close()

        # Keys correspondientes a cada valor
        keys = [
            "TIPO_IDENTIFICACION",
            "IDENTIFICACION",
            "NOMBRE",
            "DIRECCION",
            "TELEFONO",
            "ANIO_ULTIMO_PAGO",
            "PLACA",
            "COD_PRODUCTO",
            "COD_MOTOR",
            "COD_CHASIS",
            "CAMVCPN",
            "ANIO",
            "COD_COLOR",
            "COLOR",
            "CILINDRAJE",
            "TONELAJE",
            "OCUPANTES",
            "MODELO",
            "CLASE",
            "SUBCLASE"
        ]
        resultado_dict = {keys[i]: result[i] for i in range(len(keys))}
        if result:
            return jsonify({
                'resultado': resultado_dict # Devolver el resultado como JSON
            }), 200
        else:
            return jsonify({
                'mensaje': 'No se encontraron resultados para la consulta.'
            }), 404
    except Exception as e:

        return jsonify({
            'mensaje': 'Ocurrió un error al procesar la solicitud: {}'.format(str(e))
        }), 500

@web_services.route('/list_price_work/<cod_tipo_problema>', methods=['GET'])
def get_select_price_work_for_code(cod_tipo_problema):
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()
        sql = "select DESCRIPCION, COSTO, CODIGO_DURACION from ST_TIPO_PRECIO where CODIGO_DURACION= :cod_tipo_problema "
        cur.execute(sql, {'cod_tipo_problema':cod_tipo_problema})
        result = cur.fetchall()
        data_list = []
        for row in result:
            descripcion, costo, codigo_duracion = row
            row_dict = {
                'descripcion': descripcion,
                'costo': costo,
                'cod_tipo_problema': codigo_duracion
            }
            data_list.append(row_dict)
        return jsonify(data_list)
    except Exception as e:
        # error message
        return jsonify({
            'mensaje': 'Ocurrió un error al procesar la solicitud: {}'.format(str(e))
        }), 500  #500 Internal Server Error

##--------------------------WS BLUBEAR-----------------------------------------------##

@web_services.route('/marcas/dropdown', methods=['GET'])
def dropdown_despieces():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
                SELECT nombre_e, cod_despiece
                    FROM st_despiece
                WHERE empresa = 20
                    AND nivel = 1
                    AND cod_despiece IN ('S', 'B', 'E')
                """
        brands = cursor.execute(sql).fetchall()

        list_brands = []
        for brand in brands:
            dict = {
                "MARCA": brand[0],
                "COD_MARCA": brand[1]
            }
            list_brands.append(dict)
        return jsonify(list_brands), 200
    except Exception as e:
        print(e)
        return jsonify({'Error del servidor': str(e)}), 50

@web_services.route('/categories/dropdown', methods=['GET'])
def dropdown_categories():
    try:
        cod_despiece_padre = request.args.get('cod_marca')
        cod_despiece_padre =cod_despiece_padre.upper()
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
            SELECT 
                    cod_despiece,
                    nombre_e,
                    nivel,
                    cod_despiece_padre
       
            FROM st_despiece
            WHERE  empresa=20
            AND    nivel=2
            AND    cod_despiece_padre=:cod_despiece_padre
                """
        categories = cursor.execute(sql, {"cod_despiece_padre": cod_despiece_padre}).fetchall()
        list_categories = []
        for category in categories:
            if category[0] =='SGN' or category[0]=='BGN' or category[0] =='SCU' or category[0] =='SLF' or category[0] =='BCR' or category[0] =='BPA' or category[0] =='BMO':
                continue
            dict = {
                "COD_CATEGORIA": category[0],
                "CATEGORIA": category[1]
            }
            list_categories.append(dict)
        return jsonify(list_categories), 200
    except Exception as e:
        print(e)
        return jsonify({'Error del servidor': str(e)}), 50

@web_services.route('/modelos/dropdown', methods=['GET'])
def dropdown_modelos():
    try:
        # Lista de modelos permitidos
        modelos_permitidos = [
            "ARMY",
            "XTREME 200",
            "STEELER",
            "XY250GY-6I",
            "SMX-8",
            "THOR",
            "A-VENTURE",
            "XY250-8 TITAN",
            "XY300GY-13",
            "CHIEF II",
            "XY250-11",
            "SPORT-II",
            "XY200 GP",
            "SPARTA 170",
            "SPARTA 200",
            "150-CS",
            "GN STARK",
            "XY150-10F",
            "XY150-10D",
            "CLASICA",
            "XY125-30A",
            "FREEDOM",
            "JEDI",
            "CITY-MAX",
            "CROSSMAX - XY300-13",
            "FLASH S600",
            "E-MAX 1500",
            "AVATAR 1200",
            "RAYO 500"
        ]

        cod_despiece_padre = request.args.get('cod_categoria')
        cod_despiece_padre = cod_despiece_padre.upper()
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
            SELECT 
                    cod_despiece,
                    nombre_i,
                    nivel,
                    cod_despiece_padre
            FROM st_despiece
            WHERE  empresa=20
            AND    nivel=3
            AND    cod_despiece_padre=:cod_despiece_padre
        """

        categories = cursor.execute(sql, {"cod_despiece_padre": cod_despiece_padre}).fetchall()
        list_categories = []
        for category in categories:
            if category[1] in modelos_permitidos:
                dict = {
                    "COD_MODELO": category[0],
                    "MODELO": category[1]
                }
                list_categories.append(dict)
        return jsonify(list_categories), 200
    except Exception as e:
        print(e)
        return jsonify({'Error del servidor': str(e)}), 500

@web_services.route('/subsistema/dropdown', methods=['GET'])
def dropdown_subsistema():
    try:
        cod_modelo = request.args.get('cod_modelo')
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
                            SELECT  DISTINCT  MI.NOMBRE
                            FROM ST_PRODUCTO_DESPIECE D, ST_DESPIECE DP, PRODUCTO p, TG_MODELO_ITEM mi
                            where dp.empresa                         =                         20
                            and   dp.cod_despiece_padre              =                         :cod_modelo
                            and   d.COD_DESPIECE                     =                         dp.cod_despiece
                            and   d.EMPRESA                          =                         dp.empresa
                            and   p.empresa                          =                         d.empresa
                            and   p.cod_producto                     =                         d.cod_producto
                            and   mi.empresa                         =                         p.empresa
                            and   mi.cod_modelo                      =                         p.cod_modelo_cat1
                            and   mi.cod_item                        =                         p.cod_item_cat1
                            and   mi.cod_item                        !=                        'PTA'  
        """
        subsystems = cursor.execute(sql, {"cod_modelo": cod_modelo}).fetchall()
        subsystems_dict = []
        for subsystem in subsystems:
            dict = {
                "SUBSISTEMA": subsystem[0]
            }
            subsystems_dict.append(dict)
        return jsonify(subsystems_dict)
    except Exception as e:
        print(e)
        return jsonify({'Error del servidor': str(e)}), 500

@web_services.route('/anio/dropdown', methods=['GET'])
def dropdown_anio_repuesto():
    try:
        modelo_name = request.args.get('modelo_name')
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
                SELECT DISTINCT AAAA 
                FROM        VT_MODELOS_MOTOS_ANIO_BI
                WHERE       NOMBRE        =       :modelo_name
        """
        subsystems = cursor.execute(sql, {"modelo_name": modelo_name}).fetchall()
        subsystems_dict = []
        for subsystem in subsystems:
            dict = {
                "AÑO": subsystem[0]
            }
            subsystems_dict.append(dict)

        return jsonify(subsystems_dict)
    except Exception as e:
        print(e)
        return jsonify({'Error del servidor': str(e)}), 500

@web_services.route('/all_parts', methods=['GET'])
def get_all_parts():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
          SELECT
    D.COD_PRODUCTO,
    P.NOMBRE AS NOMBRE_PRODUCTO,
    P.IVA,
    P.ICE,
    C.nombre color,
    BUF.ES_BUFFER AS CONTROL_BUFFER,
    DP.COD_DESPIECE_PADRE AS CODIGO_MODELO_MOTO,
    DP2.NOMBRE_E AS MOTO_MODELO,
    MI.NOMBRE AS NOMBRE_SUBSISTEMA,
    MI.COD_ITEM AS CODIGO_SUBSISTEMA,
    DP2.COD_DESPIECE_PADRE AS CODIGO_CATEGORIA,
    DP3.NOMBRE_E AS NOMBRE_CATEGORIA,
    DP4.NOMBRE_E AS NOMBRE_MARCA,
    DP4.COD_DESPIECE AS CODIGO_MARCA,
    L.COD_AGENCIA,
    B.BODEGA,
    B.NOMBRE AS NOMBRE_BODEGA,
    L.COD_UNIDAD,
    L.PRECIO,
    P.VOLUMEN AS PESO,
    COALESCE(RPA.ANIO_DESDE, NULL) AS FROM_YEAR,
    COALESCE(RPA.ANIO_HASTA, NULL) AS TO_YEAR
FROM
    ST_PRODUCTO_DESPIECE D
    JOIN ST_DESPIECE DP ON D.COD_DESPIECE = DP.COD_DESPIECE AND D.EMPRESA = DP.EMPRESA
    JOIN PRODUCTO P ON P.EMPRESA = D.EMPRESA AND D.COD_PRODUCTO = P.COD_PRODUCTO
    JOIN TG_MODELO_ITEM MI ON MI.EMPRESA = P.EMPRESA AND P.COD_ITEM_CAT1 = MI.COD_ITEM --P.COD_MODELO_CAT1 = MI.COD_MODELO 
    JOIN ST_DESPIECE DP2 ON DP2.EMPRESA = D.EMPRESA AND DP.COD_DESPIECE_PADRE = DP2.COD_DESPIECE
    JOIN ST_DESPIECE DP3 ON DP3.EMPRESA = DP2.EMPRESA AND DP2.COD_DESPIECE_PADRE = DP3.COD_DESPIECE
    JOIN ST_DESPIECE DP4 ON DP4.EMPRESA = DP3.EMPRESA AND DP3.COD_DESPIECE_PADRE = DP4.COD_DESPIECE
    JOIN ST_COLOR C ON C.COD_COLOR = P.PARTIDA
    JOIN ST_PRODUCTO_BUFFER BUF ON BUF.COD_PRODUCTO = P.COD_PRODUCTO AND BUF.EMPRESA = P.EMPRESA
    JOIN ST_LISTA_PRECIO L ON L.COD_PRODUCTO = P.COD_PRODUCTO AND L.COD_AGENCIA = 50 AND L.COD_UNIDAD = P.COD_UNIDAD AND L.COD_FORMA_PAGO = 'EFE' AND L.COD_DIVISA = 'DOLARES' AND L.COD_MODELO_CLI = 'CLI1' AND L.COD_ITEM_CLI = 'CF' AND L.ESTADO_GENERACION = 'R' AND (L.FECHA_FINAL IS NULL OR  L.FECHA_FINAL >= TRUNC(SYSDATE))
    JOIN BODEGA B ON B.EMPRESA = L.EMPRESA AND B.BODEGA = L.COD_AGENCIA
    JOIN ST_MATERIAL_IMAGEN IM ON IM.COD_TIPO_MATERIAL = 'PRO' AND IM.COD_MATERIAL = P.COD_PRODUCTO AND IM.EMPRESA = P.EMPRESA
    LEFT JOIN ST_PRODUCTO_REP_ANIO RPA ON RPA.EMPRESA = MI.EMPRESA AND RPA.COD_PRODUCTO = P.COD_PRODUCTO
WHERE
    DP.EMPRESA = 20
    --AND DP4.COD_DESPIECE NOT IN ('U', '1', 'L')
    --AND L.COD_AGENCIA = 50
    --AND B.BODEGA = 50
    AND
    (SELECT KS_INVENTARIO.consulta_existencia(
                        DP.EMPRESA,
                        L.COD_AGENCIA,
                        P.COD_PRODUCTO,
                        'U',
                        TO_DATE(SYSDATE, 'YYYY/MM/DD'),
                        1,
                        'Z',
                        1
                    )
                    FROM dual)>0
        """
        valor_politica_ecommerce = get_politica_credito_ecommerce()
        cursor.execute(sql)
        results = []
        for row in cursor.fetchall():
            #host = '192.168.30.8:5000'
            host = '201.218.59.182:5000'
            imagen_url = f"http://{host}/imageApi/img?code={row[0]}"
            anios = [2020, 2021, 2022]
            result_dict = {
                'COD_PRODUCTO': row[0],
                'NOMBRE_PRODUCTO': row[1],
                'IVA': row[2],
                'ICE': row[3],
                'COLOR': row[4],
                'CONTROL_BUFFER': row[5],
                'CODIGO_MODELO_MOTO': row[6],
                'MOTO_MODELO': row[7],
                'NOMBRE_SUBSISTEMA': row[8],
                'CODIGO_SUBSISTEMA': row[9],
                'CODIGO_CATEGORIA': row[10],
                'NOMBRE_CATEGORIA': row[11],
                'NOMBRE_MARCA': row[12],
                'CODIGO_MARCA': row[13],
                'COD_AGENCIA': row[14],
                'BODEGA': row[15],
                'NOMBRE_BODEGA': row[16],
                'COD_UNIDAD': row[17],
                'PRECIO': round(row[18]*valor_politica_ecommerce,3),
                'URL_IMAGE': imagen_url,
                'PESO': row[19],
                'ANIO_DESDE': row[20],
                'ANIO_HASTA': row[21]
            }
            results.append(result_dict)
        return jsonify(results)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})
def get_politica_credito_ecommerce():
    try:
        # Establece la conexión
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()

        # Define y ejecuta la consulta SQL
        sql = """
                select factor_credito from st_politica_credito_d a
                where a.num_cuotas=0
                and   a.cod_politica=4
        """
        cursor.execute(sql)
        rules_politica = cursor.fetchone()
        if rules_politica:
            result = rules_politica[0]
        else:
            # Si no hay resultado, asigna un valor por defecto o maneja el caso adecuadamente
            result = None
        return result
    except cx_Oracle.DatabaseError as e:
        print(f"Error de base de datos: {e}")
    finally:
        # Asegúrate de cerrar el cursor y la conexión
        if cursor:
            cursor.close()
        if c:
            c.close()

@web_services.route('/checkStock', methods=['POST'])
def check_stock(): #EndPoint to check stock before purchase
    try:
        # Get the parameters from the request.
        empresa = 20    #default Massline
        agencia = 50    #The Ecommerce agency's code
        data = request.get_json()
        db = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = db.cursor()
        parts = []
        #Verify the stock availability for each part and provide the corresponding information
        for products in data:
            flag_available = False
            result = validate_existance(cursor, products['cod_producto'], empresa, agencia)
            if result >= int(products['quantity']):
                flag_available = True
            parts.append({'cod_producto': products['cod_producto'], 'available': result, 'complete_purchase': flag_available})
        cursor.close()
        return jsonify(parts)
    except Exception as e:
        return jsonify({'error': str(e)})
def validate_existance(cursor, cod_producto, empresa, cod_agencia): #Verify function for the stock inventary
    try:
        cursor.execute("""
                    SELECT KS_INVENTARIO.consulta_existencia(
                        :param1,
                        :param2,
                        :param3,
                        :param4,
                        TO_DATE(:param5, 'YYYY/MM/DD'),
                        :param6,
                        :param7,
                        :param8 
                    ) AS resultado
                    FROM dual
                """,
                       param1=empresa, param2=cod_agencia, param3=cod_producto, param4='U', param5=date.today(), param6=1, param7='Z',
                       param8=1)
        result = cursor.fetchone()
        return result[0]
    except Exception as e:
        return str(e)

@web_services.route('/get_info_cliente_facturacion', methods=['GET'])
def get_data_clients(): #endPoint to get data from a client, it needs values: id and type of id
    try:
        empresa = 20  # default Massline
        type_id = request.args.get('type_id') #type of id document 1: cedula, 2 Ruc, 3 passaport
        cod_client = request.args.get('id')
        cod_client = cod_client[:-1] + "-" + cod_client[-1]
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        cursor.execute("""
            select a.cod_cliente, a.nombre, a.apellido1, b.direccion_calleh, b.celular, b.email_factura from cliente a, cliente_hor b WHERE
            a.empresa                         =                         :empresa
            and b.empresah                    =                         a.empresa
            and a.cod_tipo_identificacion     =                         :tipo_identificacion
            and a.cod_cliente                 =                         :cod_client
            and b.cod_clienteh                =                         a.cod_cliente       
            
                                                                  """, tipo_identificacion=type_id, empresa=empresa, cod_client=cod_client)

        client = cursor.fetchone()
        if client:
            data_client = {
                'id':           client[0].replace("-", "") if client[0] is not None else '',
                'nombres':      client[1] if client[1] is not None else '',
                'apellidos':    client[2] if client[2] is not None else '',
                'direccion':    client[3] if client[3] is not None else '',
                'celular':      client[4] if client[4] is not None else '',
                'email':        client[5] if client[5] is not None else ''
                }
        else:
            data_client = {
                'estado': 'NO REGISTRADO'
            }
        c.close()
        return jsonify({'cliente': data_client}), 200
    except Exception as e:
        print(e)
        return str(e)

@web_services.route('/save_new_data_client', methods=['POST'])
def save_new_data_client():
    try:
        data_client = json.loads(request.data)
        empresa = 20  # default Massline
        type_client = 'CF'
        cod_client = data_client['id']
        cod_client = cod_client[:-1] + "-" + cod_client[-1]
        if checkJsonData_json(data_client):

            c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
            cursor = c.cursor()
            try:
                cursor.execute("""
                                INSERT INTO cliente (empresa, cod_cliente, nombre, apellido1, cod_tipo_identificacion)
                                VALUES (:empresa, :cod_cliente, :name, :second_name, :cod_tipo_id)
                                """, empresa=empresa, cod_cliente=cod_client,
                               name=data_client['nombre'].upper(), second_name=data_client['apellidos'].upper(),
                               cod_tipo_id=data_client['type_id'])

                cursor.execute("""
                                INSERT INTO cliente_hor (empresah, cod_clienteh, direccion_calleh, celular, email_factura, cod_tipo_clienteh)
                                VALUES (:empresa, :cod_cliente, :address, :phone,:email, :cod_type_client)
                                """, empresa=empresa, cod_cliente=cod_client,
                               address=data_client['direccion'].upper(),
                               phone=data_client['celular'], email=data_client['email'].upper(), cod_type_client= type_client)
                c.commit()
                return jsonify({"Registro exitoso": "1"})
            except Exception as e:
                c.rollback()
                print(e)
                return str(e)
            finally:
                cursor.close()
        else:
            return jsonify({'error': 'El JSON contiene valores no válidos'}), 400

    except Exception as e:
        print(e)
        return str(e)
def checkJsonData_json(json_data):
    for key, value in json_data.items():
        if key != 'type_id' and not isinstance(value, str):
            return False
    if isinstance(json_data['type_id'], int):
        return True
    else:
        return False

@web_services.route('/save_invoice/cf/parts', methods=['POST'])
def save_invoice_cf_parts():
    try:
        data_invoice = json.loads(request.data)
        empresa = 20  # for this WS default 20 = massline
        if not data_invoice:
            return jsonify({"error": "No input data provided"}), 400

        # validate received data
        is_valid, error_message = validate_data(data_invoice)
        if not is_valid:
            return jsonify({"error": "Missing data", "details": error_message}), 400

        # -----------------------OPERATION --------------------------------------
        flag_save_bill = save_data_bill_extended(data_invoice, empresa)
        if flag_save_bill == True:
            # -----------------------------------------------------------------------
            number = random.randint(1, 10000)
            message = f"FE-{number}"
            return jsonify(
                {"message": "Transaction completed successfully", "data": data_invoice, "order_code": message}), 200
        else:
            return jsonify({"error": flag_save_bill})
    except Exception as e:
        return str(e)
def validate_data(data):
    # Lista de campos obligatorios a nivel superior
    required_fields = ['id', 'paymentType', 'paymentBrand', 'total', 'subTotal', 'discountPercentage', 'discountAmount',
                       'currency', 'batchNo']
    # Lista de campos obligatorios para la tarjeta y el cliente
    required_card_fields = ['cardType', 'bin', 'last4Digits', 'holder', 'expiryMonth', 'expiryYear', 'acquirerCode']
    required_client_fields = ['name', 'lastName', 'clientId', 'address']

    # Verificar que todos los campos a nivel superior estén presentes y no estén vacíos
    for field in required_fields:
        if field not in data or data[field] in [None, '']:
            return False, f"Missing or empty field: {field}"

    # Verificar que la información de la tarjeta esté presente y sea válida
    if 'card' not in data:
        return False, "Missing card data"
    for field in required_card_fields:
        if field not in data['card'] or data['card'][field] in [None, '']:
            return False, f"Missing or empty field in card: {field}"

    # Verificar que la información del cliente esté presente y sea válida
    if 'client' not in data:
        return False, "Missing client data"
    for field in required_client_fields:
        if field not in data['client'] or data['client'][field] in [None, '']:
            return False, f"Missing or empty field in client: {field}"

    if 'cod_products' not in data:
        return False, "Missing cod_products data"
    cod_products = data['cod_products']
    if isinstance(cod_products, list) and len(cod_products) > 0:  # Verifica que sea una lista y no esté vacía
        pass
    else:
        return False, "Missing cod_products data"

    return True, None
def save_data_bill_extended(data_invoice, empresa):
    # Extrae datos del JSON
    id_transaction = data_invoice['id']
    payment_type = data_invoice['paymentType']
    payment_brand = data_invoice['paymentBrand']
    total = data_invoice['total']
    sub_total = data_invoice['subTotal']
    discount_percentage = data_invoice['discountPercentage']
    discount_amount = data_invoice['discountAmount']
    currency = data_invoice['currency']
    batch_no = data_invoice['batchNo']
    card_type = data_invoice['card']['cardType']
    bin_card = data_invoice['card']['bin']
    last_4_digits = data_invoice['card']['last4Digits']
    holder = data_invoice['card']['holder']
    expiry_month = data_invoice['card']['expiryMonth']
    expiry_year = data_invoice['card']['expiryYear']
    acquirer_code = data_invoice['card']['acquirerCode']
    client_type_id = data_invoice['client']['typeId']
    client_name = data_invoice['client']['name']
    client_last_name = data_invoice['client']['lastName']
    client_id = data_invoice['client']['clientId']
    client_address = data_invoice['client']['address']
    cod_products = data_invoice['cod_products']
    id_guia_servientrega = data_invoice['idGuiaServientrega']
    cost_shiping_calculate = data_invoice['costShipingCalculate']
    shiping_discount = data_invoice['shipingDiscount']

    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cursor = c.cursor()
    try:
        # Insert into st_cab_datafast
        cursor.execute(
            """ INSERT INTO st_cab_datafast (
                    empresa, id_transaction, payment_type, payment_brand, total, sub_total, discount_percentage, discount_amount, currency, batch_no,
                    id_guia_servientrega, card_type, bin_card, last_4_digits, holder, expiry_month, expiry_year,
                    acquirer_code, client_type_id, client_name, client_last_name, client_id, client_address,
                    cost_shiping_calculate, shiping_discount
                ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25) """,
            (empresa, id_transaction, payment_type, payment_brand, total, sub_total, discount_percentage,
             discount_amount, currency, batch_no,
             id_guia_servientrega, card_type, bin_card, last_4_digits, holder, expiry_month, expiry_year, acquirer_code,
             client_type_id,
             client_name, client_last_name, client_id, client_address, cost_shiping_calculate, shiping_discount))

        # Insert into st_det_datafast
        for product in cod_products:
            cursor.execute(
                """
                INSERT INTO st_det_datafast (empresa, id_transaction, cod_producto, price, quantity)
                VALUES (:1, :2, :3, :4, :5)                                     
                """, (empresa, id_transaction, product['codProducto'], product['price'], product['quantity'])
            )
            c.commit()
        return True
    except Exception as e:
        c.rollback()
        return str(e)
    finally:
        cursor.close()

@web_services.route('/save_invoice/cf1/parts', methods=['POST'])
def save_invoice_cf1_parts():
    try:
        data_invoice = json.loads(request.data)
        empresa = 20  # for this WS default 20 = massline
        if not data_invoice:
            return jsonify({"error": "No input data provided"}), 400

        # validate received data
        is_valid, error_message = validate_data1(data_invoice)
        if not is_valid:
            return jsonify({"error": "Missing data", "details": error_message}), 400
        #-----------------------OPERATION --------------------------------------
        flag_save_bill = save_data_bill_extended1(data_invoice, empresa)
        if flag_save_bill == True:
            #-----------------------------------------------------------------------
            number = random.randint(1, 100)
            message = f"F1-0653{number}"
            return jsonify({"message": "Transaction completed successfully", "data": data_invoice, "order_code": message}), 200
        else:
            return jsonify({"error": flag_save_bill})
    except Exception as e:
        return str(e)
def validate_data1(data):
    # list of required fields at top level
    required_fields = ['transactionId', 'internalTransactionReference', 'total', 'subTotal', 'discountPercentage', 'discountAmount', 'currency', 'idGuiaServientrega']
    # list of required fields at client level
    required_client_fields = ['name', 'lastName', 'clientId', 'address']

    # Verify that all top levels fields are present and not empty
    for field in required_fields:
        if field not in data or data[field] in [None, '']:
            return False, f"Missing or empty field: {field}"

    # Verify that customer information is present and valid
    if 'client' not in data:
        return False, "Missing client data"

    for field in required_client_fields:
        if field not in data['client'] or data['client'][field] in [None, '']:
            return False, f"Missing or empty field in client: {field}"

    if 'cod_products' not in data:
        return False, "Missing cod_products data"
    cod_products = data['cod_products']
    if isinstance(cod_products, list) and len(cod_products) > 0:  # verify that it is a list and not empty
        pass
    else:
        return False, "Missing cod_products data"

    return True, None
def save_data_bill_extended1(data_invoice, empresa):
    # Extrae datos del JSON
    id_transaction = data_invoice['transactionId']
    internal_transaction_reference = data_invoice['internalTransactionReference']
    total = data_invoice['total']
    sub_total = data_invoice['subTotal']
    discount_percentage = data_invoice['discountPercentage']
    discount_amount = data_invoice['discountAmount']
    currency = data_invoice['currency']
    id_guia_servientrega = data_invoice['idGuiaServientrega']
    client_type_id = data_invoice['client']['typeId']
    client_name = data_invoice['client']['name']
    client_last_name = data_invoice['client']['lastName']
    client_id = data_invoice['client']['clientId']
    client_address = data_invoice['client']['address']
    cost_shiping = data_invoice['costShipingCalculate']
    shiping_discount = data_invoice['shipingDiscount']
    cod_products = data_invoice['cod_products']
    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cursor = c.cursor()
    try:
        # Insert into st_cab_deuna
        cursor.execute(
            """ INSERT INTO st_cab_deuna (
                empresa, id_transaction, internal_transaction_reference, total, sub_total, discount_percentage, discount_amount, currency, id_guia_servientrega,
                client_type_id, client_name, client_last_name, client_id, client_address, cost_shiping, shiping_discount
            ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16) """,
            (empresa, id_transaction, internal_transaction_reference, total, sub_total, discount_percentage, discount_amount, currency,
             id_guia_servientrega, client_type_id, client_name, client_last_name, client_id, client_address, cost_shiping,  shiping_discount))

        # Insert into st_det_deuna
        for product in cod_products:
            cursor.execute(
                """
                INSERT INTO st_det_deuna (empresa, id_transaction, cod_producto, price, quantity)
                VALUES (:1, :2, :3, :4, :5)                                     
                """, (empresa, id_transaction, product['codProducto'], product['price'], product['quantity'])
            )
            c.commit()
        return True
    except Exception as e:
        c.rollback()
        return str(e)
    finally:
        cursor.close()

@web_services.route('/all_consigned_motorcycle', methods=['GET'])
def all_consigned_motorcycle():
    try:
        # Conexión a la base de datos Oracle
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()

        # Consulta SQL
        sql = """
        SELECT
            cod_chasis, cod_motor, codigo, descripcion,
            modelo, camvcpn, anio, color, marca,
            cilindraje, tonelaje, ocupantes, clase,
            subclase, pais_origen, cod_manual_garantia,
            ruc_cliente 
        FROM (
            SELECT
                a.cod_chasis, a.cod_motor, a.cod_producto codigo,
                p.nombre descripcion, a.modelo, a.camvcpn camvcpn,
                a.anio, l.nombre color, m.nombre marca,
                a.cilindraje, a.tonelaje, a.ocupantes, a.clase,
                a.subclase, a.pais_origen, b.cod_manual_garantia,
                n.ruc_cliente
            FROM
                st_prod_packing_list a,
                st_prod_packing_l_garantias b,
                producto p,
                st_color l,
                vt_producto_serie_consigna n,
                marca m
            WHERE
                a.cod_producto = b.cod_producto
                AND a.empresa = b.empresa
                AND a.cod_chasis = b.cod_chasis
                AND a.cod_producto = p.cod_producto
                AND a.empresa = p.empresa
                AND a.cod_color = l.cod_color
                AND a.cod_motor = n.cod_motor
                AND a.cod_producto = n.cod_producto
                AND a.empresa = n.empresa
                AND (n.fecha_despacho > SYSDATE - 10 OR a.fecha_modificacion > SYSDATE - 10)
                AND a.empresa = 20
                AND p.empresa = m.empresa
                AND p.cod_marca = m.cod_marca
            UNION
            SELECT
                a.cod_chasis, a.cod_motor, a.cod_producto codigo,
                p.nombre descripcion, a.modelo, a.camvcpn camvcpn,
                a.anio, l.nombre color, m.nombre marca,
                a.cilindraje, a.tonelaje, a.ocupantes, a.clase,
                a.subclase, a.pais_origen, b.cod_manual_garantia,
                com.cod_persona
            FROM
                st_prod_packing_list a,
                st_prod_packing_l_garantias b,
                producto p,
                st_color l,
                st_serie_movimiento n,
                comprobante com,
                marca m
            WHERE
                a.cod_producto = b.cod_producto
                AND a.empresa = b.empresa
                AND a.cod_chasis = b.cod_chasis
                AND a.cod_producto = p.cod_producto
                AND a.empresa = p.empresa
                AND a.cod_color = l.cod_color
                AND a.cod_motor = n.numero_serie
                AND a.cod_producto = n.cod_producto
                AND a.empresa = n.empresa
                AND com.tipo_comprobante = 'A0'
                AND n.empresa = com.empresa
                AND n.tipo_comprobante = com.tipo_comprobante
                AND n.cod_comprobante = com.cod_comprobante
                AND (com.fecha > SYSDATE - 10 OR a.fecha_modificacion > SYSDATE - 10)
                AND a.empresa = 20
                AND p.empresa = m.empresa
                AND p.cod_marca = m.cod_marca
                AND com.anulado = 'N'
                AND NOT EXISTS (
                    SELECT '+'
                    FROM st_producto_serie_consigna co
                    WHERE a.cod_motor = co.numero_serie
                      AND a.cod_producto = co.cod_producto
                      AND a.empresa = co.empresa
                )
                AND NOT EXISTS (
                    SELECT '+'
                    FROM st_comprobante_comprobante cc, st_serie_movimiento sm
                    WHERE cc.cod_comprobante_s = sm.cod_comprobante
                      AND cc.tipo_comprobante_s = sm.tipo_comprobante
                      AND cc.empresa_s = sm.empresa
                      AND sm.numero_serie = n.numero_serie
                      AND com.cod_comprobante = cc.cod_comprobante
                      AND com.tipo_comprobante = cc.tipo_comprobante
                      AND com.empresa = cc.empresa
                      AND cc.tipo_comprobante_s = 'D0'
                )
        )"""

        cursor.execute(sql)
        results = []
        for row in cursor.fetchall():
            result_dict = {
                'cod_chasis': row[0],
                'cod_motor': row[1],
                'codigo': row[2],
                'descripcion': row[3],
                'modelo': row[4],
                'camvcpn': row[5],
                'anio': row[6],
                'color': row[7],
                'marca': row[8],
                'cilindraje': row[9],
                'tonelaje': row[10],
                'ocupantes': row[11],
                'clase': row[12],
                'subclase': row[13],
                'pais_origen': row[14],
                'cod_manual_garantia': row[15],
                'ruc_cliente': row[16]
            }
            results.append(result_dict)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)})

@web_services.route('/get_all_ruc_b2b_customer', methods=['GET'] )
def get_all_ruc_b2b_customer():
    try:
        empresa = 20  # default Massline
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        cursor.execute("""
                select b.activoh, b.cod_tipo_clienteh, a.cod_cliente, a.nombre, a.apellido1, b.direccion_calleh, b.celular, b.email_factura 
                from cliente a, cliente_hor b 
                WHERE a.empresa = :empresa
                and b.empresah = a.empresa
                and b.cod_tipo_clienteh IN ('DI', 'DM', 'TA', 'AR', 'MX', 'GA', 'MM','CE','MY','MA')
                and b.cod_clienteh = a.cod_cliente
            """, empresa=empresa)

        clients = cursor.fetchall()
        data_clients = []
        for client in clients:
            ruc = client[2].replace("-", "") if client[2] is not None else ''

            # Consulta adicional para obtener las direcciones
            cursor.execute("""
                    select a.descripcion, a.direccion 
                    from ar_taller_servicio_tecnico a 
                    where a.ruc = :ruc
                """, ruc=ruc)

            additional_addresses = cursor.fetchall()
            addresses = [client[5] if client[5] is not None else '']
            for address in additional_addresses:
                addresses.append(f"{address[0]}: {address[1]}")

            data_clients.append({
                'activo': client[0] if client[0] is not None else '',
                'tipo_cliente': client[1] if client[1] is not None else '',
                'id': ruc,
                'nombres': client[3] if client[3] is not None else '',
                'apellidos': client[4] if client[4] is not None else '',
                'direcciones': addresses,
                'celular': client[6] if client[6] is not None else '',
                'email': client[7] if client[7] is not None else ''
            })

        c.close()
        return jsonify({'clientes': data_clients}), 200
    except Exception as e:
        print(e)
        return str(e), 500
@web_services.route('/all_parts_b2b', methods=['GET'])
def get_all_parts_b2b():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
   SELECT
    D.COD_PRODUCTO,
    P.NOMBRE AS NOMBRE_PRODUCTO,
    P.IVA,
    P.ICE,
    C.nombre color,
    BUF.ES_BUFFER AS CONTROL_BUFFER,
    DP.COD_DESPIECE_PADRE AS CODIGO_MODELO_MOTO,
    DP2.NOMBRE_E AS MOTO_MODELO,
    MI.NOMBRE AS NOMBRE_SUBSISTEMA,
    MI.COD_ITEM AS CODIGO_SUBSISTEMA,
    DP2.COD_DESPIECE_PADRE AS CODIGO_CATEGORIA,
    DP3.NOMBRE_E AS NOMBRE_CATEGORIA,
    DP4.NOMBRE_E AS NOMBRE_MARCA,
    DP4.COD_DESPIECE AS CODIGO_MARCA,
    L.COD_AGENCIA,
    B.BODEGA,
    B.NOMBRE AS NOMBRE_BODEGA,
    L.COD_UNIDAD,
    L.PRECIO,
    P.VOLUMEN AS PESO,
    COALESCE(RPA.ANIO_DESDE, NULL) AS FROM_YEAR,
    COALESCE(RPA.ANIO_HASTA, NULL) AS TO_YEAR
FROM
    ST_PRODUCTO_DESPIECE D
    JOIN ST_DESPIECE DP ON D.COD_DESPIECE = DP.COD_DESPIECE AND D.EMPRESA = DP.EMPRESA
    JOIN PRODUCTO P ON P.EMPRESA = D.EMPRESA AND D.COD_PRODUCTO = P.COD_PRODUCTO
    JOIN TG_MODELO_ITEM MI ON MI.EMPRESA = P.EMPRESA AND P.COD_MODELO_CAT1 = MI.COD_MODELO AND P.COD_ITEM_CAT1 = MI.COD_ITEM
    JOIN ST_DESPIECE DP2 ON DP2.EMPRESA = D.EMPRESA AND DP.COD_DESPIECE_PADRE = DP2.COD_DESPIECE
    JOIN ST_DESPIECE DP3 ON DP3.EMPRESA = DP2.EMPRESA AND DP2.COD_DESPIECE_PADRE = DP3.COD_DESPIECE
    JOIN ST_DESPIECE DP4 ON DP4.EMPRESA = DP3.EMPRESA AND DP3.COD_DESPIECE_PADRE = DP4.COD_DESPIECE
    JOIN ST_COLOR C ON C.COD_COLOR = P.PARTIDA
    JOIN ST_PRODUCTO_BUFFER BUF ON BUF.COD_PRODUCTO = P.COD_PRODUCTO AND BUF.EMPRESA = P.EMPRESA
    JOIN ST_LISTA_PRECIO L ON L.COD_PRODUCTO = P.COD_PRODUCTO AND L.COD_AGENCIA = 50 AND L.COD_UNIDAD = P.COD_UNIDAD AND L.COD_FORMA_PAGO = 'EFE' AND L.COD_DIVISA = 'DOLARES' AND L.COD_MODELO_CLI = 'CLI1' AND L.COD_ITEM_CLI = 'CF' AND L.ESTADO_GENERACION = 'R' AND (L.FECHA_FINAL IS NULL OR L.FECHA_FINAL >= TRUNC(SYSDATE))
    JOIN BODEGA B ON B.EMPRESA = L.EMPRESA AND B.BODEGA = L.COD_AGENCIA
    JOIN ST_MATERIAL_IMAGEN IM ON IM.COD_TIPO_MATERIAL = 'PRO' AND IM.COD_MATERIAL = P.COD_PRODUCTO AND IM.EMPRESA = P.EMPRESA
    LEFT JOIN ST_PRODUCTO_REP_ANIO RPA ON RPA.EMPRESA = MI.EMPRESA AND RPA.COD_PRODUCTO = P.COD_PRODUCTO
WHERE
    DP.EMPRESA = 20
    AND EXISTS (
        SELECT 1
        FROM ST_FORMULA F
        WHERE F.EMPRESA = DP.EMPRESA
          AND F.COD_PRODUCTO = P.COD_PRODUCTO
    )
    AND (SELECT KS_INVENTARIO.consulta_existencia(
                        DP.EMPRESA,
                        L.COD_AGENCIA,
                        P.COD_PRODUCTO,
                        'U',
                        TO_DATE(SYSDATE, 'YYYY/MM/DD'),
                        1,
                        'Z',
                        1
                    )
                    FROM dual) > 0

        """
        valor_politica_ecommerce = get_politica_credito_ecommerce()
        cursor.execute(sql)
        results = []
        for row in cursor.fetchall():
            #host = '192.168.30.8:5000'
            host = '201.218.59.182:5000'
            result_dict = {
                'COD_PRODUCTO': row[0],
                'NOMBRE_PRODUCTO': row[1],
                'IVA': row[2],
                'ICE': row[3],
                'COLOR': row[4],
                'CONTROL_BUFFER': row[5],
                'CODIGO_MODELO_MOTO': row[6],
                'MOTO_MODELO': row[7],
                'NOMBRE_SUBSISTEMA': row[8],
                'CODIGO_SUBSISTEMA': row[9],
                'CODIGO_CATEGORIA': row[10],
                'NOMBRE_CATEGORIA': row[11],
                'NOMBRE_MARCA': row[12],
                'CODIGO_MARCA': row[13],
                'COD_AGENCIA': row[14],
                'BODEGA': row[15],
                'NOMBRE_BODEGA': row[16],
                'COD_UNIDAD': row[17],
                'PRECIO': round(row[18]*valor_politica_ecommerce,3),
                'PESO': row[19],
                'ANIO_DESDE': row[20],
                'ANIO_HASTA': row[21]
            }
            results.append(result_dict)
        return jsonify(results)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})

@web_services.route('/politicas_b2b_ecommerce', methods=['GET'])
def get_politicas_b2b_ecommerce():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
            SELECT 
                p.cod_politica, 
                p.cod_tipo_clienteh, 
                c.num_cuotas, 
                c.factor_credito, 
                c.es_activo
            FROM 
                st_pol_cre_tipo_cliente p
            JOIN 
                ST_POLITICA_CREDITO_D c 
                ON p.cod_politica = c.cod_politica 
                AND p.empresa = c.empresa
            WHERE 
                p.empresa = 20
                AND (
                    p.cod_politica = 3 
                    OR (p.cod_politica = 16 AND p.cod_tipo_clienteh = 'TA')
                )
                AND c.num_cuotas <= 3
            """
        cursor.execute(sql)
        results = {}

        for row in cursor.fetchall():
            cod_clienteh = row[1]
            cuotas_info = {
                'num_cuotas': row[2],
                'factor_credito': row[3],
                'es_activo': row[4]
            }

            if cod_clienteh not in results:
                results[cod_clienteh] = []

            results[cod_clienteh].append(cuotas_info)

        # Formatear la respuesta en dos elementos con la estructura solicitada
        formatted_results = [
            {'COD_CLIENTEH': key, 'cuotas_info': value} for key, value in results.items()
        ]

        return jsonify(formatted_results)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})
@web_services.route('/get_info_transportista_ecommerce', methods=['GET'])
def get_data_transportistas_activos():  # Endpoint to get data of active transportistas
    try:
        empresa = 20  # default value or get from request args if needed

        # Establish database connection
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()

        # Execute the query
        cursor.execute("""
            SELECT cod_transportista, nombre, apellido1, direccion, telefono, es_activo, placa
            FROM ST_TRANSPORTISTA
            WHERE empresa = :empresa
              AND es_activo = 1
              AND activo_ecommerce=1
        """, empresa=empresa)

        transportistas = cursor.fetchall()
        transportistas_list = []
        for transportista in transportistas:
            transportistas_list.append({
                'RUC': transportista[0] if transportista[0] is not None else '',
                'RAZON_SOCIAL': f"{transportista[1]} {transportista[2]}" if transportista[1] is not None and
                                                                            transportista[2] is not None else ''
            })

        c.close()
        return jsonify({'transportistas': transportistas_list}), 200
    except Exception as e:
        print(e)
        return str(e), 500

@web_services.route('/parts_ecommerce_recomended_b2b', methods=['GET'])
def parts_ecommerce_recomended_b2b():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        sql = """
            WITH ranked_products AS (
                SELECT 
                    a.cod_persona, 
                    a.cod_producto, 
                    a.num_repetidos,
                    a.cliente,
                    ROW_NUMBER() OVER (PARTITION BY a.cod_persona ORDER BY a.num_repetidos DESC) AS rank,
                    p.cod_producto_modelo,  
                    cb.cod_despiece        
                FROM 
                    vt_factura_detalle_ecommerce a
                JOIN 
                    producto p ON a.cod_producto = p.cod_producto  
                JOIN 
                    st_modelo_crecimiento_bi cb ON p.cod_producto_modelo = cb.cod_modelo  
            ),
            main_query AS (
                SELECT
                    D.COD_PRODUCTO,
                    P.NOMBRE AS NOMBRE_PRODUCTO,
                    P.IVA,
                    P.ICE,
                    C.nombre color,
                    BUF.ES_BUFFER AS CONTROL_BUFFER,
                    DP.COD_DESPIECE_PADRE AS CODIGO_MODELO_MOTO,
                    DP2.NOMBRE_E AS MOTO_MODELO,
                    MI.NOMBRE AS NOMBRE_SUBSISTEMA,
                    MI.COD_ITEM AS CODIGO_SUBSISTEMA,
                    DP2.COD_DESPIECE_PADRE AS CODIGO_CATEGORIA,
                    DP3.NOMBRE_E AS NOMBRE_CATEGORIA,
                    DP4.NOMBRE_E AS NOMBRE_MARCA,
                    DP4.COD_DESPIECE AS CODIGO_MARCA,
                    L.COD_AGENCIA,
                    B.BODEGA,
                    B.NOMBRE AS NOMBRE_BODEGA,
                    L.COD_UNIDAD,
                    L.PRECIO,
                    P.VOLUMEN AS PESO,
                    COALESCE(RPA.ANIO_DESDE, NULL) AS FROM_YEAR,
                    COALESCE(RPA.ANIO_HASTA, NULL) AS TO_YEAR
                FROM
                    ST_PRODUCTO_DESPIECE D
                JOIN 
                    ST_DESPIECE DP ON D.COD_DESPIECE = DP.COD_DESPIECE AND D.EMPRESA = DP.EMPRESA
                JOIN 
                    PRODUCTO P ON P.EMPRESA = D.EMPRESA AND D.COD_PRODUCTO = P.COD_PRODUCTO
                JOIN 
                    TG_MODELO_ITEM MI ON MI.EMPRESA = P.EMPRESA AND P.COD_MODELO_CAT1 = MI.COD_MODELO AND P.COD_ITEM_CAT1 = MI.COD_ITEM
                JOIN 
                    ST_DESPIECE DP2 ON DP2.EMPRESA = D.EMPRESA AND DP.COD_DESPIECE_PADRE = DP2.COD_DESPIECE
                JOIN 
                    ST_DESPIECE DP3 ON DP3.EMPRESA = DP2.EMPRESA AND DP2.COD_DESPIECE_PADRE = DP3.COD_DESPIECE
                JOIN 
                    ST_DESPIECE DP4 ON DP4.EMPRESA = DP3.EMPRESA AND DP3.COD_DESPIECE_PADRE = DP4.COD_DESPIECE
                JOIN 
                    ST_COLOR C ON C.COD_COLOR = P.PARTIDA
                JOIN 
                    ST_PRODUCTO_BUFFER BUF ON BUF.COD_PRODUCTO = P.COD_PRODUCTO AND BUF.EMPRESA = P.EMPRESA
                JOIN 
                    ST_LISTA_PRECIO L ON L.COD_PRODUCTO = P.COD_PRODUCTO AND L.COD_AGENCIA = 50 AND L.COD_UNIDAD = P.COD_UNIDAD AND L.COD_FORMA_PAGO = 'EFE' AND L.COD_DIVISA = 'DOLARES' AND L.COD_MODELO_CLI = 'CLI1' AND L.COD_ITEM_CLI = 'CF' AND L.ESTADO_GENERACION = 'R' AND (L.FECHA_FINAL IS NULL OR L.FECHA_FINAL >= TRUNC(SYSDATE))
                JOIN 
                    BODEGA B ON B.EMPRESA = L.EMPRESA AND B.BODEGA = L.COD_AGENCIA
                JOIN 
                    ST_MATERIAL_IMAGEN IM ON IM.COD_TIPO_MATERIAL = 'PRO' AND IM.COD_MATERIAL = P.COD_PRODUCTO AND IM.EMPRESA = P.EMPRESA
                LEFT JOIN 
                    ST_PRODUCTO_REP_ANIO RPA ON RPA.EMPRESA = MI.EMPRESA AND RPA.COD_PRODUCTO = P.COD_PRODUCTO
                WHERE
                    DP.EMPRESA = 20
                    AND EXISTS (
                        SELECT 1
                        FROM ST_FORMULA F
                        WHERE F.EMPRESA = DP.EMPRESA
                          AND F.COD_PRODUCTO = P.COD_PRODUCTO
                    )
            )
            SELECT 
                mq.COD_PRODUCTO,
                mq.NOMBRE_PRODUCTO,
                mq.IVA,
                mq.ICE,
                mq.color,
                mq.CONTROL_BUFFER,
                mq.CODIGO_MODELO_MOTO,
                mq.MOTO_MODELO,
                mq.NOMBRE_SUBSISTEMA,
                mq.CODIGO_SUBSISTEMA,
                mq.CODIGO_CATEGORIA,
                mq.NOMBRE_CATEGORIA,
                mq.NOMBRE_MARCA,
                mq.CODIGO_MARCA,
                mq.COD_AGENCIA,
                mq.BODEGA,
                mq.NOMBRE_BODEGA,
                mq.COD_UNIDAD,
                mq.PRECIO,
                mq.PESO,
                mq.FROM_YEAR,
                mq.TO_YEAR,
                rp.cod_persona, 
                rp.cod_producto, 
                rp.num_repetidos,
                rp.cliente,
                rp.cod_producto_modelo,
                rp.cod_despiece
            FROM 
                main_query mq
            JOIN 
                ranked_products rp ON mq.CODIGO_MODELO_MOTO = rp.cod_despiece
            WHERE 
                rp.rank <= 10
                AND rp.cod_persona != '0992594926001'
        """
        valor_politica_ecommerce = get_politica_credito_ecommerce()
        cursor.execute(sql)
        results = []
        for row in cursor.fetchall():
            host = '201.218.59.182:5000'
            imagen_url = f"http://{host}/imageApi/img?code={row[0]}"
            result_dict = {
                'COD_PRODUCTO': row[0],
                'NOMBRE_PRODUCTO': row[1],
                'IVA': row[2],
                'ICE': row[3],
                'COLOR': row[4],
                'CONTROL_BUFFER': row[5],
                'CODIGO_MODELO_MOTO': row[6],
                'MOTO_MODELO': row[7],
                'NOMBRE_SUBSISTEMA': row[8],
                'CODIGO_SUBSISTEMA': row[9],
                'CODIGO_CATEGORIA': row[10],
                'NOMBRE_CATEGORIA': row[11],
                'NOMBRE_MARCA': row[12],
                'CODIGO_MARCA': row[13],
                'COD_AGENCIA': row[14],
                'BODEGA': row[15],
                'NOMBRE_BODEGA': row[16],
                'COD_UNIDAD': row[17],
                'PRECIO': round(row[18]*valor_politica_ecommerce, 2),
                'PESO': row[19],
                'FROM_YEAR': row[20],
                'TO_YEAR': row[21],
                'COD_PERSONA': row[22],
                'COD_PRODUCTO_RANKED': row[23],
                'NUM_REPETIDOS': row[24],
                'CLIENTE': row[25],
                'COD_PRODUCTO_MODELO': row[26],
                'COD_DESPIECE_RANKED': row[27],
                'URL_IMAGE': imagen_url
            }
            results.append(result_dict)
        return jsonify(results)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})

@web_services.route('/save_invoice/cf1/credito_directo', methods=['POST'])
def save_invoice_cf1_credito_directo():
    try:
        data_invoice = json.loads(request.data)
        empresa = 20  # for this WS default 20 = massline
        if not data_invoice:
            return jsonify({"error": "No input data provided"}), 400

        # Validate received data
        is_valid, error_message = validate_data_credito_directo(data_invoice)
        if not is_valid:
            return jsonify({"error": "Missing data", "details": error_message}), 400

        #-----------------------OPERATION --------------------------------------
        flag_save_bill = save_data_bill_credito_directo(data_invoice, empresa)
        if flag_save_bill == True:
            # Generate FE-{number}{day}{mes}{año} code
            c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
            cursor = c.cursor()
            try:
                # Count existing records
                cursor.execute("SELECT COUNT(*) FROM ST_CAB_CREDITO_DIRECTO")
                record_count = cursor.fetchone()[0]

                # Get current date components
                day = datetime.now().day
                mes = datetime.now().month
                año = datetime.now().year

                # Generate order code
                order_code = f"FE-{record_count}{day:02d}{mes:02d}{año}"

            finally:
                cursor.close()

            return jsonify({"message": "Transaction completed successfully", "data": data_invoice, "order_code": order_code}), 200
        else:
            return jsonify({"error": flag_save_bill})
    except Exception as e:
        return str(e)
def validate_data_credito_directo(data):
    # List of required fields at top level
    required_fields = ['transactionId', 'total', 'subTotal', 'discountPercentage', 'discountAmount', 'currency', 'cuotas']

    # Verify that all top-level fields are present and not empty
    for field in required_fields:
        if field not in data or data[field] in [None, '']:
            return False, f"Missing or empty field: {field}"

    # If cod_products exists, verify that it's a non-empty list
    if 'cod_products' in data:
        cod_products = data['cod_products']
        if not (isinstance(cod_products, list) and len(cod_products) > 0):
            return False, "cod_products must be a non-empty list if provided"

    return True, None
def save_data_bill_credito_directo(data_invoice, empresa):
    # Extract data from JSON
    id_transaction = data_invoice['transactionId']
    internal_transaction_reference = data_invoice.get('internalTransactionReference')  # Optional field
    total = data_invoice['total']
    sub_total = data_invoice['subTotal']
    discount_percentage = data_invoice['discountPercentage']
    discount_amount = data_invoice['discountAmount']
    currency = data_invoice['currency']
    id_guia_servientrega = data_invoice.get('idGuiaServientrega')  # Optional field
    client_type_id = data_invoice['client'].get('typeId') if 'client' in data_invoice else None
    client_name = data_invoice['client'].get('name') if 'client' in data_invoice else None
    client_last_name = data_invoice['client'].get('lastName') if 'client' in data_invoice else None
    client_id = data_invoice['client'].get('clientId') if 'client' in data_invoice else None
    client_address = data_invoice['client'].get('address') if 'client' in data_invoice else None
    cost_shiping = data_invoice.get('costShipingCalculate')  # Optional field
    shiping_discount = data_invoice.get('shipingDiscount')  # Optional field
    cod_orden_ecommerce = data_invoice.get('codOrdenEcommerce')  # Optional field
    cod_comprobante = data_invoice.get('codComprobante')  # Optional field
    cuotas = data_invoice['cuotas']
    estado_aprobacion = data_invoice.get('estadoAprobacion')  # Optional field
    descripcion = data_invoice.get('descripcion')  # Optional field
    id_agencia_transporte = data_invoice.get('idAgenciaTransporte')  # Optional field
    nombre_agencia_transporte = data_invoice.get('nombreAgenciaTransporte')  # Optional field
    cod_products = data_invoice.get('cod_products')  # Optional field

    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cursor = c.cursor()
    try:
        # Insert into ST_CAB_CREDITO_DIRECTO
        cursor.execute(
            """ INSERT INTO ST_CAB_CREDITO_DIRECTO (
                empresa, id_transaction, internal_transaction_reference, total, sub_total, discount_percentage, discount_amount, currency, id_guia_servientrega,
                client_type_id, client_name, client_last_name, client_id, client_address, cost_shiping, shiping_discount, cod_orden_ecommerce, cod_comprobante, cuotas, estado_aprobacion, descripcion, id_agencia_transporte, nombre_agencia_transporte
            ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23) """,
            (empresa, id_transaction, internal_transaction_reference, total, sub_total, discount_percentage, discount_amount, currency,
             id_guia_servientrega, client_type_id, client_name, client_last_name, client_id, client_address, cost_shiping,  shiping_discount,
             cod_orden_ecommerce, cod_comprobante, cuotas, estado_aprobacion, descripcion, id_agencia_transporte, nombre_agencia_transporte))

        # Insert into ST_DET_CREDITO_DIRECTO if cod_products is provided
        if cod_products:
            for product in cod_products:
                cursor.execute(
                    """
                    INSERT INTO ST_DET_CREDITO_DIRECTO (empresa, id_transaction, cod_producto, price, quantity)
                    VALUES (:1, :2, :3, :4, :5)                                     
                    """, (empresa, id_transaction, product['codProducto'], product['price'], product['quantity'])
                )
        c.commit()
        return True
    except Exception as e:
        c.rollback()
        return str(e)
    finally:
        cursor.close()

@web_services.route('/get_client_orders_ecommerce/<client_id>', methods=['GET'])
def get_client_orders_ecommerce(client_id):
    try:
        empresa = 20  # Default Massline
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()
        client_id=str(client_id)
        # Consultar registros de la tabla ST_CAB_CREDITO_DIRECTO
        cursor.execute("""
            SELECT * FROM ST_CAB_CREDITO_DIRECTO 
            WHERE empresa = :empresa AND client_id = :client_id
        """, {'empresa': empresa, 'client_id': client_id})

        records = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, record)) for record in records]

        # Ejecutar funciones PL/SQL para obtener valores adicionales
        total_x_vencer = get_balance_function(cursor, 'ksa_balance_cartera.total_x_vencer', empresa, client_id)
        total_vencido = get_balance_function(cursor, 'ksa_balance_cartera.total_vencido', empresa, client_id)
        total_deuda = get_balance_function(cursor, 'ksa_balance_cartera.total_deuda', empresa, client_id)

        # Añadir valores adicionales al resultado
        response = {
            "records": result,
            "total_x_vencer": total_x_vencer,
            "total_vencido": total_vencido,
            "total_deuda": total_deuda
        }

        return jsonify(response)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        c.close()
def get_balance_function(cursor, function_name, empresa, client_id):
    try:
        # Ejecuta la función desde DUAL para obtener el resultado
        cursor.execute(f"""
            SELECT {function_name}(:param1, :param2) AS resultado
            FROM dual
        """, param1=empresa, param2=client_id)

        # Obtiene el resultado de la consulta
        result = cursor.fetchone()

        # Devuelve el resultado convertido a float
        return float(result[0]) if result and result[0] is not None else None
    except Exception as e:
        print(f"Error en la llamada a la función {function_name}: {e}")
        return None  # Manejo de errores

@web_services.route('/save_invoice/deuna_b2b', methods=['POST'])
def save_invoice_deuna_b2b():
    try:
        data_invoice = json.loads(request.data)
        empresa = 20  # for this WS default 20 = massline
        if not data_invoice:
            return jsonify({"error": "No input data provided"}), 400

        # Validate received data
        is_valid, error_message = validate_data_deuna_b2b(data_invoice)
        if not is_valid:
            return jsonify({"error": "Missing data", "details": error_message}), 400

        #-----------------------OPERATION --------------------------------------
        flag_save_bill = save_data_bill_deuna_b2b(data_invoice, empresa)
        if flag_save_bill == True:
            # Generate DEUNA-{number}{day}{mes}{año} code
            c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
            cursor = c.cursor()
            try:
                # Count existing records
                cursor.execute("SELECT COUNT(*) FROM ST_CAB_DEUNA_B2B")
                record_count = cursor.fetchone()[0]

                # Get current date components
                day = datetime.now().day
                mes = datetime.now().month
                año = datetime.now().year

                # Generate order code
                order_code = f"DEUNA-{record_count}{day:02d}{mes:02d}{año}"

            finally:
                cursor.close()

            return jsonify({"message": "Transaction completed successfully", "data": data_invoice, "order_code": order_code}), 200
        else:
            return jsonify({"error": flag_save_bill})
    except Exception as e:
        return str(e)
def validate_data_deuna_b2b(data):
    # List of required fields at top level
    required_fields = ['transactionId', 'total', 'subTotal']

    # Verify that all top-level fields are present and not empty
    for field in required_fields:
        if field not in data or data[field] in [None, '']:
            return False, f"Missing or empty field: {field}"

    # If cod_products exists, verify that it's a non-empty list
    if 'cod_products' in data:
        cod_products = data['cod_products']
        if not (isinstance(cod_products, list) and len(cod_products) > 0):
            return False, "cod_products must be a non-empty list if provided"

    return True, None
def save_data_bill_deuna_b2b(data_invoice, empresa):
    # Extract data from JSON with None defaults for optional fields
    id_transaction = data_invoice['transactionId']
    internal_transaction_reference = data_invoice.get('internalTransactionReference', None)
    total = data_invoice['total']
    sub_total = data_invoice['subTotal']
    discount_percentage = data_invoice.get('discountPercentage', None)
    discount_amount = data_invoice.get('discountAmount', None)
    currency = data_invoice.get('currency', None)
    id_guia_servientrega = data_invoice.get('idGuiaServientrega', None)
    client_type_id = data_invoice.get('client', {}).get('typeId', None)
    client_name = data_invoice.get('client', {}).get('name', None)
    client_last_name = data_invoice.get('client', {}).get('lastName', None)
    client_id = data_invoice.get('client', {}).get('clientId', None)
    client_address = data_invoice.get('client', {}).get('address', None)
    cost_shiping = data_invoice.get('costShiping', None)
    cod_orden_ecommerce = data_invoice.get('codOrdenEcommerce', None)
    cod_comprobante = data_invoice.get('codComprobante', None)
    number_of_payment = data_invoice.get('numberOfPayment', None)
    shiping_discount = data_invoice.get('shipingDiscount', None)
    descripcion = data_invoice.get('descripcion', None)
    id_agencia_transporte = data_invoice.get('idAgenciaTransporte', None)
    nombre_agencia_transporte = data_invoice.get('nombreAgenciaTransporte', None)
    cod_products = data_invoice.get('cod_products', None)

    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cursor = c.cursor()
    try:
        # Insert into ST_CAB_DEUNA_B2B
        cursor.execute(
            """ INSERT INTO ST_CAB_DEUNA_B2B (
                empresa, id_transaction, internal_transaction_reference, total, sub_total, discount_percentage, discount_amount, currency, id_guia_servientrega,
                client_type_id, client_name, client_last_name, client_id, client_address, cost_shiping, cod_orden_ecommerce, cod_comprobante, fecha, shiping_discount,
                number_of_payment, descripcion, id_agencia_transporte, nombre_agencia_transporte
            ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, SYSDATE, :18, :19, :20, :21, :22) """,
            (empresa, id_transaction, internal_transaction_reference, total, sub_total, discount_percentage, discount_amount, currency,
             id_guia_servientrega, client_type_id, client_name, client_last_name, client_id, client_address, cost_shiping,
             cod_orden_ecommerce, cod_comprobante, shiping_discount, number_of_payment, descripcion, id_agencia_transporte, nombre_agencia_transporte))

        # Insert into ST_DET_DEUNA_B2B if cod_products is provided
        if cod_products:
            for product in cod_products:
                cursor.execute(
                    """
                    INSERT INTO ST_DET_DEUNA_B2B (empresa, id_transaction, cod_producto, price, quantity)
                    VALUES (:1, :2, :3, :4, :5)                                     
                    """, (empresa, id_transaction, product['codProducto'], product['price'], product['quantity'])
                )
        c.commit()
        return True
    except Exception as e:
        c.rollback()
        return str(e)
    finally:
        cursor.close()

@web_services.route('/save_invoice/datafast_b2b', methods=['POST'])
def save_invoice_datafast_b2b():
    try:
        data_invoice = json.loads(request.data)
        empresa = 20  # for this WS default 20 = massline

        if not data_invoice:
            return jsonify({"error": "No input data provided"}), 400

        # Validate received data
        is_valid, error_message = validate_data_datafast_b2b(data_invoice)
        if not is_valid:
            return jsonify({"error": "Missing data", "details": error_message}), 400

        # -----------------------OPERATION --------------------------------------
        flag_save_bill = save_data_bill_datafast_b2b(data_invoice, empresa)
        if flag_save_bill == True:
            # Generate DATAFAST-{number}{day}{mes}{año} code
            c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
            cursor = c.cursor()
            try:
                # Count existing records
                cursor.execute("SELECT COUNT(*) FROM ST_CAB_DATAFAST_B2B")
                record_count = cursor.fetchone()[0]

                # Get current date components
                day = datetime.now().day
                mes = datetime.now().month
                año = datetime.now().year

                # Generate order code
                order_code = f"DATAFAST-{record_count}{day:02d}{mes:02d}{año}"

            finally:
                cursor.close()

            return jsonify(
                {"message": "Transaction completed successfully", "data": data_invoice, "order_code": order_code}), 200
        else:
            return jsonify({"error": flag_save_bill}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def validate_data_datafast_b2b(data):
    # List of required fields at top level
    required_fields = ['transactionId', 'total', 'subTotal']

    # Verify that all top-level fields are present and not empty
    for field in required_fields:
        if field not in data or data[field] in [None, '']:
            return False, f"Missing or empty field: {field}"

    # If cod_products exists, verify that it's a non-empty list
    if 'cod_products' in data:
        cod_products = data['cod_products']
        if not (isinstance(cod_products, list) and len(cod_products) > 0):
            return False, "cod_products must be a non-empty list if provided"

    return True, None
def save_data_bill_datafast_b2b(data_invoice, empresa):
    # Extract data from JSON with None defaults for optional fields
    id_transaction = data_invoice['transactionId']
    payment_type = data_invoice.get('paymentType', None)
    payment_brand = data_invoice.get('paymentBrand', None)
    total = data_invoice['total']
    sub_total = data_invoice['subTotal']
    discount_percentage = data_invoice.get('discountPercentage', None)
    discount_amount = data_invoice.get('discountAmount', None)
    currency = data_invoice.get('currency', None)
    batch_no = data_invoice.get('batchNo', None)
    id_guia_servientrega = data_invoice.get('idGuiaServientrega', None)
    card_type = data_invoice.get('cardType', None)
    bin_card = data_invoice.get('binCard', None)
    last_4_digits = data_invoice.get('last4Digits', None)
    holder = data_invoice.get('holder', None)
    expiry_month = data_invoice.get('expiryMonth', None)
    expiry_year = data_invoice.get('expiryYear', None)
    acquirer_code = data_invoice.get('acquirerCode', None)
    client_type_id = data_invoice.get('client', {}).get('typeId', None)
    client_name = data_invoice.get('client', {}).get('name', None)
    client_last_name = data_invoice.get('client', {}).get('lastName', None)
    client_id = data_invoice.get('client', {}).get('clientId', None)
    client_address = data_invoice.get('client', {}).get('address', None)
    cost_shiping_calculate = data_invoice.get('costShipingCalculate', None)
    shiping_discount = data_invoice.get('shipingDiscount', None)
    cod_orden_ecommerce = data_invoice.get('codOrdenEcommerce', None)
    cod_comprobante = data_invoice.get('codComprobante', None)
    cuotas = data_invoice.get('cuotas', None)
    descripcion = data_invoice.get('descripcion', None)
    id_agencia_transporte = data_invoice.get('idAgenciaTransporte', None)
    nombre_agencia_transporte = data_invoice.get('nombreAgenciaTransporte', None)
    cod_products = data_invoice.get('cod_products', None)

    c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
    cursor = c.cursor()
    try:
        # Insert into ST_CAB_DATAFAST_B2B
        cursor.execute(
            """INSERT INTO ST_CAB_DATAFAST_B2B (
                empresa, id_transaction, payment_type, payment_brand, total, sub_total, discount_percentage, discount_amount, currency, batch_no,
                id_guia_servientrega, card_type, bin_card, last_4_digits, holder, expiry_month, expiry_year, acquirer_code, client_type_id, client_name,
                client_last_name, client_id, client_address, cost_shiping_calculate, shiping_discount, cod_orden_ecommerce, cod_comprobante, fecha, cuotas,
                descripcion, id_agencia_transporte, nombre_agencia_transporte
            ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, SYSDATE, :28, :29, :30, :31)""",
            (empresa, id_transaction, payment_type, payment_brand, total, sub_total, discount_percentage,
             discount_amount, currency, batch_no,
             id_guia_servientrega, card_type, bin_card, last_4_digits, holder, expiry_month, expiry_year, acquirer_code,
             client_type_id, client_name,
             client_last_name, client_id, client_address, cost_shiping_calculate, shiping_discount, cod_orden_ecommerce,
             cod_comprobante, cuotas,
             descripcion, id_agencia_transporte, nombre_agencia_transporte)
        )

        # Insert into ST_DET_DATAFAST_B2B if cod_products is provided
        print(cod_products)
        if cod_products:
            for product in cod_products:
                cursor.execute(
                    """INSERT INTO ST_DET_DATAFAST_B2B (empresa, id_transaction, cod_producto, price, quantity)
                       VALUES (:1, :2, :3, :4, :5)""",
                    (empresa, id_transaction, product['codProducto'], product['price'], product['quantity'])
                )
        c.commit()
        return True
    except Exception as e:
        c.rollback()
        return str(e)
    finally:
        cursor.close()

@web_services.route('/get_info_moto_shibot_active_warranty', methods=['GET'])
def get_info_moto_shibot_active_warranty():  # Endpoint to get motorcycle information; requires at least one value: cod_motor, cod_chasis, camvCpn, or placa
    try:
        empresa = 20  # Default Massline
        cod_motor = request.args.get('cod_motor', '').strip()
        cod_chasis = request.args.get('cod_chasis', '').strip()
        camvCpn = request.args.get('camvCpn', '').strip()
        placa = request.args.get('placa', '').strip()

        # Check if at least one parameter is provided
        if not (cod_motor or cod_chasis or camvCpn or placa):
            return jsonify({
                               'error': 'Se necesita al menos uno de los siguientes parámetros: cod_motor, cod_chasis, camvCpn, o placa'}), 400

        # Prepare the query conditions based on provided parameters
        conditions = []
        parameters = {'empresa': empresa}

        if cod_motor:
            conditions.append("b.cod_motor = :cod_motor")
            parameters['cod_motor'] = cod_motor
        if cod_chasis:
            conditions.append("b.cod_chasis = :cod_chasis")
            parameters['cod_chasis'] = cod_chasis
        if camvCpn:
            conditions.append("b.camvcpn = :camvCpn")
            parameters['camvCpn'] = camvCpn
        if placa:
            conditions.append("a.placa = :placa")
            parameters['placa'] = placa

        # Join conditions with OR
        where_clause = " OR ".join(conditions)

        # Prepare the database connection
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cursor = c.cursor()

        # Execute the SQL query with dynamic where clause
        query = f"""
                SELECT a.nombre, a.identificacion, a.direccion, a.placa, a.camv_o_cpn, 
                       b.cod_chasis, b.cod_motor, b.marca, b.modelo, b.anio, 
                       b.cilindraje, b.potencia, b.color
                FROM st_matriculacion_motos a, VT_PROD_PACKING_LIST_BI b
                WHERE a.empresa = :empresa
                  AND a.camv_o_cpn = b.camvcpn
                  AND b.empresa = a.empresa
                  AND ({where_clause})
            """

        # Execute with the parameters as a dictionary
        cursor.execute(query, parameters)

        motos = cursor.fetchall()
        c.close()

        # Format the response
        if motos:
            data_motos = [
                {
                    'nombre': moto[0],
                    'identificacion': moto[1],
                    'direccion': moto[2],
                    'placa': moto[3],
                    'camv_o_cpn': moto[4],
                    'cod_chasis': moto[5],
                    'cod_motor': moto[6],
                    'marca': moto[7],
                    'modelo': moto[8],
                    'anio': moto[9],
                    'cilindraje': moto[10],
                    'potencia': moto[11],
                    'color': moto[12]
                } for moto in motos
            ]
        else:
            data_motos = {'estado': 'NO REGISTRADO'}

        return jsonify({'motos': data_motos}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Error al procesar la solicitud, revise los parámetros y vuelva a intentar.'}), 500


##---------------------------------------------------------------------------------WEB SERVER DE CONSULTA DE INVENTARIO JAHER-------------------------------------------------------------

@web_services.route("/stock_available", methods=["GET"])
def stock_available():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        id = request.args.get('id', None)
        if id is None:
            return jsonify(
                {"error": "Se requieren ambos parámetros ID/RUC de cliente."}), 400
        sql = """
                SELECT * FROM  VT_ASIGNACION_CUPO V
                WHERE V.RUC_CLIENTE = :id 
                """

        cursor = cur_01.execute(sql, [id])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        modelos = []
        for result in array:
            modelo = dict(zip(row_headers, result))
            modelos.append(modelo)
        return json.dumps(modelos)
    except Exception as ex:
        raise Exception(ex)
    return response_body

@web_services.route("/assign_serial", methods=["GET"])
def assign_serial():
    try:
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur_01 = c.cursor()
        id = request.args.get('id', None)
        cod_ext = request.args.get('cod_ext', None)
        cod_producto = request.args.get('cod_producto', None)
        cod_agencia = request.args.get('cod_agencia', None)
        cantidad = request.args.get('cantidad', None)

        if id is None or cod_agencia is None or cantidad is None:
            return jsonify(
                {"error": "Faltan campos requeridos"}), 500

        if id == '' or cod_agencia == '' or cantidad == '':
            return jsonify(
                {"error": "Campos nulos"}), 500

        if cod_producto is None or cod_ext is None:
            return jsonify(
                {"error": "Ingrese al menos código externo o código producto"}), 500

        sql = """
                SELECT P.ANIO, P.CAMVCPN, P.CILINDRAJE, P.CLASE, P.COD_CHASIS, P.COD_COLOR, P.COD_MOTOR, 
                   X.COD_PRODUCTO, X.DESCRIPCION, P.MARCA, P.MODELO, X.NUMERO_SERIE, 
                   P.OCUPANTES, P.PAIS_ORIGEN, P.POTENCIA, P.SECUENCIA_IMPRONTA, P.SUBCLASE, P.TONELAJE  
            FROM (
                  SELECT CODIGO_EXTERNO, DESCRIPCION, COD_PRODUCTO, NUMERO_SERIE, ks_inventario_serie.obt_fecha_produccion_sb(20 ,NUMERO_SERIE,5) as fecha_produccion  
                  FROM (
                        SELECT P.COD_PRODUCTO_CLI AS CODIGO_EXTERNO, Y.DESCRIPCION, S.RUC_CLIENTE,
                        S.PORCENTAJE_MAXIMO, S.Cantidad_Minima, Y.COD_PRODUCTO_TERMINADO AS COD_PRODUCTO,
                        Y.NUMERO_SERIE, Y.EDAD_MESES
                        FROM
                        ST_ASIGNACION_CUPO S,
                        ST_PRODUCTO_CLIENTE P,
                        (
                        SELECT v.COD_PRODUCTO, v.DESCRIPCION, v.NUMERO_SERIE, B.COD_PRODUCTO_TERMINADO, v.edad_meses
                        FROM
                        vt_inventario_sin_bat v
                        JOIN ST_PROD_FORMULA_D A ON v.COD_PRODUCTO = A.COD_PRODUCTO_INSUMO
                        JOIN ST_PROD_FORMULA B ON
                            A.COD_FORMULA = B.COD_FORMULA AND
                            A.COD_TIPO_FORMULA = B.COD_TIPO_FORMULA AND
                            A.EMPRESA = B.EMPRESA
                        WHERE
                        B.EMPRESA = 20 AND
                        A.ES_MOTOR = 1 AND
                        v.COD_BODEGA = 5 AND
                        EXISTS (
                            SELECT *
                                   FROM ST_PROD_FORMULA_D B
                                   WHERE
                                    v.COD_PRODUCTO = B.COD_PRODUCTO_INSUMO AND
                                    v.EMPRESA = B.EMPRESA AND
                                    B.ES_MOTOR = 1) 
                        AND
                        EXISTS (
                            SELECT *
                            FROM ST_PROD_FORMULA_D B, ST_PROD_FORMULA C, STA_MOVIMIENTO D
                            WHERE
                                v.COD_PRODUCTO = B.COD_PRODUCTO_INSUMO AND
                                v.EMPRESA = B.EMPRESA AND
                                B.ES_MOTOR = 1 AND
                                B.EMPRESA = C.EMPRESA AND
                                B.COD_FORMULA = C.COD_FORMULA AND
                                B.COD_TIPO_FORMULA = C.COD_TIPO_FORMULA AND
                                C.EMPRESA = D.EMPRESA AND
                                C.COD_PRODUCTO_TERMINADO = D.COD_PRODUCTO
                        )
                        ) Y
                      WHERE Y.COD_PRODUCTO_TERMINADO = S.COD_PRODUCTO
                      AND Y.COD_PRODUCTO_TERMINADO = P.COD_PRODUCTO
                      AND S.COD_PRODUCTO = P.COD_PRODUCTO
                      AND S.RUC_CLIENTE = P.COD_CLIENTE) 
                 WHERE CODIGO_EXTERNO = :cod_ext
                 OR COD_PRODUCTO = :cod_producto 
                 ORDER BY fecha_produccion ) X, 
            ST_PROD_PACKING_LIST P 
            WHERE P.COD_MOTOR = X.NUMERO_SERIE 
            AND ROWNUM <= :cantidad
                """

        cursor = cur_01.execute(sql, [cod_ext, cod_producto, cantidad])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        series = []
        for result in array:
            serie = dict(zip(row_headers, result))
            for key, value in serie.items():
                if isinstance(value, datetime):
                    serie[key] = value.strftime("%d/%m/%Y")
            series.append(serie)
        return jsonify(series)
    except Exception as ex:
        raise Exception(ex)
    return response_body

