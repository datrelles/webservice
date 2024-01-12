from flask import Blueprint, request, jsonify
from numpy.core.defchararray import upper
from os import getenv
from datetime import datetime
import cx_Oracle
from src.function_jwt import validate_token
from src import oracle

import json

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
        sql = "select ROWNUM, P.DESCRIPCION AS PROVINCIA, C.DESCRIPCION AS CIUDAD, T.DESCRIPCION AS NOMBRE, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, REPLACE(T.RUC,'-','') as ID,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO, T.ES_TALLER_AUTORIZADO, T.TIPO_TALLER, T.CUPO_X_HORA from AR_TALLER_SERVICIO_TECNICO T , AD_PROVINCIAS P, ad_cantones c WHERE T.CODIGO_EMPRESA = 20 and T.COD_PROVINCIA = P.CODIGO_PROVINCIA (+) and c.codigo_canton(+) = t.cod_canton and c.codigo_provincia(+) = t.cod_provincia and P.CODIGO_NACION = 1 and T.ANULADO = 'N'"
        cursor = cur_01.execute(sql)
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        empresas = []
        for result in array:
            empresa = dict(zip(row_headers, result))
            empresa['FECHA_ADICION'] = empresa['FECHA_ADICION'].strftime('%Y-%m-%d %H:%M:%S') if empresa[
                                                                                                     'FECHA_ADICION'] is not None else None
            empresa['FECHA_MODIFICACION'] = empresa['FECHA_MODIFICACION'].strftime('%Y-%m-%d %H:%M:%S') if empresa[
                                                                                                               'FECHA_MODIFICACION'] is not None else None
            empresa['FECHA_NACIMIENTO'] = empresa['FECHA_NACIMIENTO'].strftime('%Y-%m-%d') if empresa[
                                                                                                  'FECHA_NACIMIENTO'] is not None else None
            empresa['ES_TALLER_AUTORIZADO'] = 'SI' if empresa['ES_TALLER_AUTORIZADO'] == 1 else 'NO'
            empresa['TIPO_TALLER'] = 'AAA' if empresa['TIPO_TALLER'] == 3 else 'A' if empresa[
                                                                                          'TIPO_TALLER'] == 1 else 'AA' if \
            empresa['TIPO_TALLER'] == 2 else 'SIN CLASIFICACION'
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
        sql = "select ROWNUM, P.DESCRIPCION AS PROVINCIA, C.DESCRIPCION AS CIUDAD, T.DESCRIPCION AS NOMBRE, T.NOMBRE_CONTACTO, T.TELEFONO1, T.TELEFONO2, T.TELEFONO3, T.DIRECCION, REPLACE(T.RUC,'-','') as ID,T.FECHA_ADICION, T.FECHA_MODIFICACION, T.FECHA_NACIMIENTO, T.ES_TALLER_AUTORIZADO, T.TIPO_TALLER, T.CUPO_X_HORA from AR_TALLER_SERVICIO_TECNICO T , AD_PROVINCIAS P, ad_cantones c WHERE T.CODIGO_EMPRESA = 20 and T.COD_PROVINCIA = P.CODIGO_PROVINCIA (+) and c.codigo_canton(+) = t.cod_canton and c.codigo_provincia(+) = t.cod_provincia and REPLACE(T.RUC,'-','') = replace(:id,'-','') and P.CODIGO_NACION = 1 and T.ANULADO = 'N'"
        cursor = cur_01.execute(sql, [id])
        c.close
        row_headers = [x[0] for x in cursor.description]
        array = cursor.fetchall()
        empresas = []
        for result in array:
            empresa = dict(zip(row_headers, result))
            empresa['FECHA_ADICION'] = empresa['FECHA_ADICION'].strftime('%Y-%m-%d %H:%M:%S') if empresa[
                                                                                                     'FECHA_ADICION'] is not None else None
            empresa['FECHA_MODIFICACION'] = empresa['FECHA_MODIFICACION'].strftime('%Y-%m-%d %H:%M:%S') if empresa[
                                                                                                               'FECHA_MODIFICACION'] is not None else None
            empresa['FECHA_NACIMIENTO'] = empresa['FECHA_NACIMIENTO'].strftime('%Y-%m-%d') if empresa[
                                                                                                  'FECHA_NACIMIENTO'] is not None else None
            empresa['ES_TALLER_AUTORIZADO'] = 'SI' if empresa['ES_TALLER_AUTORIZADO'] == 1 else 'NO'
            empresa['TIPO_TALLER'] = 'SIN CLASIFICACION' if empresa['TIPO_TALLER'] == 0 else 'A' if empresa[
                                                                                                        'TIPO_TALLER'] == 1 else 'AA' if \
            empresa['TIPO_TALLER'] == 2 else 'AAA'
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
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where p.empresa = 20 and p.cod_producto = v.COD_PRODUCTO(+) AND p.empresa = v.empresa(+) and p.cod_chasis = v.NUMERO_SERIE(+) and P.COD_CHASIS = ' + "'" + code + "'",
        user, password)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0], (
        {"CODPRODUC": row[1], "CODMOTOR": row[2], "CODCHASIS": row[3], "CPN": row[4], "YEAR": row[5], "COLOR": row[6],
         "CILINDRAJE": row[7], "TONELAJE": row[8], "OCUPANTES": row[9], "MODELO": row[10], "CLASE": row[11],
         "SUBCLASE": row[12], "FECHA CREACION": row[13], "FECHA MODIFICACION": row[14], "CODIGO LIQUIDACION": row[15],
         "IMPORTACION": row[16]}))
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
        'select ROWNUM, P.COD_PRODUCTO, P.COD_MOTOR, P.COD_CHASIS, P.CAMVCPN, P.ANIO, P.COD_COLOR, P.CILINDRAJE, P.TONELAJE, P.OCUPANTES, P.MODELO, P.CLASE, P.SUBCLASE, P.FECHA_ADICION, P.FECHA_MODIFICACION, V.COD_LIQUIDACION, V.NOMBRE from ST_PROD_PACKING_LIST P, VT_VALORACION_SERIE V where p.empresa = 20 and p.cod_producto = v.COD_PRODUCTO(+) AND p.empresa = v.empresa(+) and   p.cod_chasis = v.NUMERO_SERIE(+) and P.anio = ' + year,
        user, password)
    mydict = create_dict()
    for row in array:
        mydict.add(row[0], (
        {"CODPRODUC": row[1], "CODMOTOR": row[2], "CODCHASIS": row[3], "CPN": row[4], "YEAR": row[5], "COLOR": row[6],
         "CILINDRAJE": row[7], "TONELAJE": row[8], "OCUPANTES": row[9], "MODELO": row[10], "CLASE": row[11],
         "SUBCLASE": row[12], "FECHA CREACION": row[13], "FECHA MODIFICACION": row[14], "CODIGO LIQUIDACION": row[15],
         "IMPORTACION": row[16]}))
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
                host = '200.105.245.182:5000'
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
        page_size = 100
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


# WS MODULE WARRANTY
@web_services.route('/warranty/motorcycles', methods=['POST'])
def warranty():
    try:
        # PRE INSERT (Generación de Codigo comprobante )
        v_cod_empresa = 20
        v_cod_tipo_comprobante = 'CP'
        v_cod_agencia = 1
        # Llamada al procedimiento almacenado en DB
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
        # Ejecutar la consulta de inserción
        # Obtén la conexión y el cursor

        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()

        # Variable de salida para capturar el resultado
        result_var = cur.var(cx_Oracle.STRING)

        # Ejecuta el procedimiento almacenado
        cur.execute(query, (v_cod_empresa, v_cod_tipo_comprobante, v_cod_agencia, result_var))
        # Captura el resultado
        result = result_var.getvalue()
        # Confirmar la transacción y cerrar el cursor y la conexión
        c.commit()
        cur.close()
        c.close()

        # INFO TALLER
        ruc = '0106320500001'
        if not ruc:
            return jsonify({"error": "Se requiere el campo 'ruc' en la solicitud"}), 400
        query = """
                        SELECT COD_PROVINCIA, COD_CANTON
                        FROM AR_TALLER_SERVICIO_TECNICO
                        WHERE ruc = :1
                        """
        # Ejecutar la consulta de inserción
        # Obtén la conexión y el cursor
        c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
        cur = c.cursor()
        cur.execute(query, (ruc,))
        # Obtener los resultados
        city = cur.fetchall()
        # Cerrar el cursor y la conexión
        cur.close()
        c.close()

        #INFO MOTOR
        numMotor=' LC162FMJLE050582'
        if not numMotor:
            return jsonify({"error": "Se requiere el campo 'numMotor'"})

        data = oracle.infoMotor(numMotor)
        print(data)
        # Obtén la conexión y el cursor



        return jsonify({'result': result, 'code Province, Ciudad': city, "motorDAta": data})

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
