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
        page_size = 1000
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
        print(e)
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
    data['codigo_responsable'] = 'WSSHIBOT'
    data['cod_canal'] = 5
    data['adicionado_por'] = 'WSSHIBOT'
    fecha_venta = datetime.strptime(data['fecha_venta'], '%Y/%m')
    data['fecha_venta'] = fecha_venta
    data['aplica_garantia'] = 2

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
    print('enter')
    if not num_motor:
        return jsonify({"error": "Se requiere el campo 'cod_motor'"})

    data_motor = oracle.infoMotor(num_motor)
    data['cod_producto'] = data_motor[1]
    data['cod_distribuidor_cli'] = data_motor[0]
    print(data['cod_producto'])
    print(data['cod_distribuidor_cli'])
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

#WS BLUBEAR
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
            print(brand)
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
            if category[0] =='SGN' or category[0]=='BGN':
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
        cod_despiece_padre = request.args.get('cod_categoria')
        cod_despiece_padre = cod_despiece_padre.upper()
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
            AND    nivel=3
            AND    cod_despiece_padre=:cod_despiece_padre
                """

        categories = cursor.execute(sql, {"cod_despiece_padre": cod_despiece_padre}).fetchall()
        list_categories = []
        for category in categories:
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
                L.PRECIO
            FROM 
                ST_PRODUCTO_DESPIECE D,
                ST_DESPIECE DP,
                PRODUCTO P,
                TG_MODELO_ITEM MI,
                ST_DESPIECE DP2,
                ST_DESPIECE DP3,
                ST_DESPIECE DP4,
                ST_PRODUCTO_BUFFER BUF,
                ST_COLOR C,
                ST_LISTA_PRECIO L,
                BODEGA B,
                ST_MATERIAL_IMAGEN IM
            WHERE 
                DP.EMPRESA = 20
                AND D.COD_DESPIECE = DP.COD_DESPIECE
                AND D.EMPRESA = DP.EMPRESA
                AND P.EMPRESA = D.EMPRESA
                AND DP2.EMPRESA = D.EMPRESA
                AND DP3.EMPRESA = DP2.EMPRESA
                AND DP4.EMPRESA = DP3.EMPRESA
                AND MI.EMPRESA = P.EMPRESA
                AND C.COD_COLOR = P.PARTIDA
                AND BUF.COD_PRODUCTO = P.COD_PRODUCTO
                AND BUF.EMPRESA = P.EMPRESA
                AND P.COD_MODELO_CAT1 = MI.COD_MODELO
                AND P.COD_ITEM_CAT1 = MI.COD_ITEM
                AND D.COD_PRODUCTO = P.COD_PRODUCTO
                AND DP.COD_DESPIECE_PADRE = DP2.COD_DESPIECE
                AND DP2.COD_DESPIECE_PADRE = DP3.COD_DESPIECE
                AND DP3.COD_DESPIECE_PADRE = DP4.COD_DESPIECE
                AND DP4.COD_DESPIECE NOT IN ('U', '1', 'L')
                AND L.COD_PRODUCTO = P.COD_PRODUCTO
                AND L.COD_AGENCIA = 50
                AND L.COD_UNIDAD = P.COD_UNIDAD
                AND L.COD_FORMA_PAGO = 'EFE'
                AND L.COD_DIVISA = 'DOLARES'
                AND L.COD_MODELO_CLI = 'CLI1'
                AND L.COD_ITEM_CLI = 'CF'
                AND L.ESTADO_GENERACION = 'R' 
                AND (L.FECHA_FINAL IS NULL OR  L.FECHA_FINAL >= TRUNC(SYSDATE))
                AND B.EMPRESA = L.EMPRESA
                AND B.BODEGA = L.COD_AGENCIA
                AND IM.COD_TIPO_MATERIAL = 'PRO'
                AND IM.COD_MATERIAL = P.COD_PRODUCTO
                AND IM.EMPRESA = P.EMPRESA
        """
        cursor.execute(sql)
        results = []
        for row in cursor.fetchall():
            #host = '192.168.30.8:5000'
            host = '200.105.245.182:5000'
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
                'PRECIO': row[18],
                'URL_IMAGE': imagen_url,
                'ANIO': anios
            }
            results.append(result_dict)
        return jsonify(results)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})

