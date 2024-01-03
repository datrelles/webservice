from flask import Blueprint, jsonify, request
from datetime import datetime
from src.models.users import Usuario, Empresa
from src.models.tipo_comprobante import TipoComprobante
from src.models.proveedores import Proveedor,TgModelo,TgModeloItem, ProveedorHor, TcCoaProveedor
from src.models.orden_compra import StOrdenCompraCab, StOrdenCompraDet, StOrdenCompraTracking, StPackinglist
from src.models.productos import Producto
from src.models.despiece import StDespiece
from src.models.producto_despiece import StProductoDespiece
from src.config.database import db,engine,session
from sqlalchemy import func, text,bindparam,Integer
import logging
import datetime
from datetime import datetime,date
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin


bp = Blueprint('routes', __name__)

logger = logging.getLogger(__name__)

#METODOS GET

@bp.route('/usuarios')
@jwt_required()
@cross_origin()
def obtener_usuarios():
    query = Usuario.query()
    usuarios = query.all()
    serialized_usuarios = []
    for usuario in usuarios:
        serialized_usuarios.append({
            'usuario_oracle': usuario.usuario_oracle,
            'apellido1': usuario.apellido1,
            'apellido2': usuario.apellido2,
            'nombre': usuario.nombre,
            'empresa_actual': usuario.empresa_actual,
            'useridc': usuario.useridc,
            'toda_bodega': usuario.toda_bodega,
            'toda_empresa': usuario.toda_empresa,
            'agencia_actual': usuario.agencia_actual,
            'aa': usuario.aa,
            'e_mail': usuario.e_mail,
            'password': usuario.password
        })
    return jsonify(serialized_usuarios)

@bp.route('/empresas')
@jwt_required()
@cross_origin()
def obtener_empresas():
    empresas = Empresa.query.all()
    #print(type(empresas))
    resultados = []
    for empresa in empresas:
        resultados.append(empresa.to_dict())
    #empresas_dict = [e.__dict__ for e in empresas]
    return jsonify(resultados)

@bp.route('/tipo_comprobante')
@jwt_required()
@cross_origin()
def obtener_tipo_comprobante():
    query = TipoComprobante.query()
    comprobantes = query.all()
    serialized_comprobantes = []
    for comprobante in comprobantes:
        serialized_comprobantes.append({
            'empresa': comprobante.empresa,
            'tipo': comprobante.tipo,
            'nombre': comprobante.nombre,
            'cod_sistema': comprobante.cod_sistema,
        })
    return jsonify(serialized_comprobantes)

@bp.route('/proveedores_ext')
@jwt_required()
@cross_origin()
def obtener_proveedores_ext():
    query = db.session.query(Proveedor).join(ProveedorHor, Proveedor.cod_proveedor == ProveedorHor.cod_proveedorh).filter(ProveedorHor.cod_tipo_proveedorh == 'EXT')
    proveedores = query.all()
    serialized_proveedores = []
    for proveedor in proveedores:
        empresa = proveedor.empresa if proveedor.empresa else ""
        cod_proveedor = proveedor.cod_proveedor if proveedor.cod_proveedor else ""
        nombre = proveedor.nombre if proveedor.nombre else ""
        direccion = proveedor.direccion if proveedor.direccion else ""
        telefono = proveedor.telefono if proveedor.telefono else ""
        # Consulta adicional para obtener la ciudad del proveedor
        ciudad_query = db.session.query(TcCoaProveedor.ciudad_matriz).filter(TcCoaProveedor.ruc == proveedor.cod_proveedor)
        ciudad = ciudad_query.scalar()
        #cod_proveedores = [cod_proveedor.to_dict() for cod_proveedor in proveedor.cod_proveedores]
        serialized_proveedores.append({
            'empresa': empresa,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'ciudad': ciudad,
            'direccion': direccion,
            'telefono': telefono
        })
    return jsonify(serialized_proveedores)

@bp.route('/proveedores_nac')
@jwt_required()
@cross_origin()
def obtener_proveedores_nac():
    query = db.session.query(Proveedor).join(ProveedorHor, Proveedor.cod_proveedor == ProveedorHor.cod_proveedorh).filter(ProveedorHor.cod_tipo_proveedorh == 'NAC')
    proveedores = query.all()
    serialized_proveedores = []
    for proveedor in proveedores:
        empresa = proveedor.empresa if proveedor.empresa else ""
        cod_proveedor = proveedor.cod_proveedor if proveedor.cod_proveedor else ""
        nombre = proveedor.nombre if proveedor.nombre else ""
        direccion = proveedor.direccion if proveedor.direccion else ""
        telefono = proveedor.telefono if proveedor.telefono else ""
        # Consulta adicional para obtener la ciudad del proveedor
        ciudad_query = db.session.query(TcCoaProveedor.ciudad_matriz).filter(TcCoaProveedor.ruc == proveedor.cod_proveedor)
        ciudad = ciudad_query.scalar()
        #cod_proveedores = [cod_proveedor.to_dict() for cod_proveedor in proveedor.cod_proveedores]
        serialized_proveedores.append({
            'empresa': empresa,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'ciudad': ciudad,
            'direccion': direccion,
            'telefono': telefono
        })
    return jsonify(serialized_proveedores)

@bp.route('/orden_compra_cab')
@jwt_required()
@cross_origin()
def obtener_orden_compra_cab():
    query = StOrdenCompraCab.query()
    ordenes_compra = query.all()
    serialized_ordenes_compra = []
    for orden in ordenes_compra:
        empresa = orden.empresa if orden.empresa else ""
        cod_po = orden.cod_po if orden.cod_po else ""
        tipo_comprobante = orden.tipo_comprobante if orden.tipo_comprobante else ""
        cod_agencia = orden.cod_agencia if orden.cod_agencia else ""
        cod_proveedor = orden.cod_proveedor if orden.cod_proveedor else ""
        nombre = orden.nombre if orden.nombre else ""
        proforma = orden.proforma if orden.proforma else ""
        invoice = orden.invoice if orden.invoice else ""
        bl_no = orden.bl_no if orden.bl_no else ""
        cod_po_padre = orden.cod_po_padre if orden.cod_po_padre else ""
        usuario_crea = orden.usuario_crea if orden.usuario_crea else ""
        fecha_crea = datetime.strftime(orden.fecha_crea,"%d/%m/%Y") if orden.fecha_crea else ""
        usuario_modifica = orden.usuario_modifica if orden.usuario_modifica else ""
        fecha_modifica = datetime.strftime(orden.fecha_modifica,"%d/%m/%Y") if orden.fecha_modifica else ""
        cod_modelo = orden.cod_modelo if orden.cod_modelo else ""
        cod_item = orden.cod_item if orden.cod_item else ""
        bodega = orden.bodega if orden.bodega else ""
        ciudad = orden.ciudad if orden.ciudad else ""
        estado = orden.estado if orden.estado else ""
        serialized_ordenes_compra.append({
            'empresa': empresa,
            'cod_po': cod_po,
            'tipo_combrobante': tipo_comprobante,
            'cod_agencia': cod_agencia,
            'cod_proveedor': cod_proveedor,
            'nombre': nombre,
            'proforma': proforma,
            'invoice': invoice,
            'bl_no': bl_no,
            'cod_po_padre': cod_po_padre,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'bodega': bodega,
            'ciudad': ciudad,
            'estado': estado
        })

    return jsonify(serialized_ordenes_compra)

@bp.route('/orden_compra_det')
@jwt_required()
@cross_origin()
def obtener_orden_compra_det():
    query = StOrdenCompraDet.query()
    detalles = query.all()
    serialized_detalles = []
    for detalle in detalles:
        exportar = detalle.exportar if detalle.exportar else ""
        cod_po = detalle.cod_po if detalle.cod_po else ""
        tipo_comprobante = detalle.tipo_comprobante if detalle.tipo_comprobante else ""
        secuencia = detalle.secuencia if detalle.secuencia else ""
        empresa = detalle.empresa if detalle.empresa else ""
        cod_producto = detalle.cod_producto if detalle.cod_producto else ""
        cod_producto_modelo = detalle.cod_producto_modelo if detalle.cod_producto_modelo else ""
        nombre = detalle.nombre if detalle.nombre else ""
        nombre_i = detalle.nombre_i if detalle.nombre_i else ""
        nombre_c = detalle.nombre_c if detalle.nombre_c else ""
        nombre_mod_prov = detalle.nombre_mod_prov if detalle.nombre_mod_prov else ""
        nombre_comercial = detalle.nombre_comercial if detalle.nombre_comercial else ""
        costo_sistema = detalle.costo_sistema if detalle.costo_sistema else ""
        costo_cotizado = detalle.costo_cotizado if detalle.costo_cotizado else ""
        fecha_costo = detalle.fecha_costo if detalle.fecha_costo else ""
        fob = detalle.fob if detalle.fob else ""
        cantidad_pedido = detalle.cantidad_pedido if detalle.cantidad_pedido else ""
        fob_total = fob * cantidad_pedido
        saldo_producto = detalle.saldo_producto if detalle.saldo_producto else ""
        unidad_medida = detalle.unidad_medida if detalle.unidad_medida else ""
        usuario_crea = detalle.usuario_crea if detalle.usuario_crea else ""
        fecha_crea = datetime.strftime(detalle.fecha_crea,"%d/%m/%Y") if detalle.fecha_crea else ""
        usuario_modifica = detalle.usuario_modifica if detalle.usuario_modifica else ""
        fecha_modifica = datetime.strftime(detalle.fecha_modifica,"%d/%m/%Y") if detalle.fecha_modifica else ""
        serialized_detalles.append({
            'exportar': exportar,
            'cod_po': cod_po,
            'tipo_comprobante': tipo_comprobante, 
            'secuencia': secuencia,
            'empresa': empresa,
            'cod_producto': cod_producto,
            'cod_producto_modelo': cod_producto_modelo,
            'nombre': nombre,
            'nombre_ingles': nombre_i,
            'nombre_china': nombre_c,
            'nombre_mod_prov': nombre_mod_prov,
            'nombre_comercial':nombre_comercial,
            'costo_sistema': costo_sistema,
            'costo_cotizado': costo_cotizado,
            'fecha_costo': fecha_costo,
            'fob': fob,
            'fob_total': fob_total,
            'cantidad_pedido': cantidad_pedido,
            'saldo_producto': saldo_producto,
            'unidad_medida': unidad_medida,
            'usuario_crea': usuario_crea,
            'fecha_crea': fecha_crea,
            'usuario_modifica': usuario_modifica,
            'fecha_modifica': fecha_modifica,
        })
    return jsonify(serialized_detalles)

@bp.route('/productos')
@jwt_required()
@cross_origin()
def obtener_productos():
    query = Producto.query()
    productos = query.all()
    serialized_detalles = []
    for producto in productos:
        empresa = producto.empresa if producto.empresa else ""
        cod_producto = producto.cod_producto if producto.cod_producto else ""
        tipo_inventario = producto.tipo_inventario if producto.tipo_inventario else ""
        cod_marca = producto.cod_marca if producto.cod_marca else ""
        cod_alterno = producto.cod_alterno if producto.cod_alterno else ""
        nombre = producto.nombre if producto.nombre else ""
        cod_barra = producto.cod_barra if producto.cod_barra else ""
        useridc = producto.useridc if producto.useridc else ""
        presentacion = producto.presentacion if producto.presentacion else ""
        volumen = producto.volumen if producto.volumen else ""
        grado = producto.grado if producto.grado else ""
        costo = producto.costo if producto.costo else ""
        activo = producto.activo if producto.activo else ""
        cod_modelo = producto.cod_modelo if producto.cod_modelo else ""
        cod_item = producto.cod_item if producto.cod_item else ""
        cod_modelo_cat = producto.cod_modelo_cat if producto.cod_modelo_cat else ""
        cod_item_cat = producto.cod_item_cat if producto.cod_item_cat else ""
        serie = producto.serie if producto.serie else ""
        ice = producto.ice if producto.ice else ""
        cod_producto_modelo = producto.cod_producto_modelo if producto.cod_producto_modelo else ""
        serialized_detalles.append({
            'empresa': empresa,
            'cod_producto': cod_producto,
            'tipo_inventario': tipo_inventario,
            'cod_marca': cod_marca,
            'cod_alterno': cod_alterno,
            'nombre': nombre,
            'cod_barra': cod_barra,
            'useridc': useridc,
            'presentacion': presentacion,
            'volumen': volumen,
            'grado': grado,
            'costo': costo,
            'activo': activo,
            'cod_modelo': cod_modelo,
            'cod_item': cod_item,
            'cod_modelo_cat': cod_modelo_cat,
            'cod_item_cat': cod_item_cat,
            'serie': serie,
            'ice': ice,
            'cod_producto_modelo': cod_producto_modelo
        })
    return jsonify(serialized_detalles)

@bp.route('/estados')
@jwt_required()
@cross_origin()
def obtener_estados():
    try:
        query = TgModeloItem.query()
        estados = query.all()
        #print(estados)
        serialized_estados = []
        for estado in estados:
            empresa = estado.empresa if estado.empresa else ""
            cod_modelo = estado.cod_modelo if estado.cod_modelo else ""
            cod_item = estado.cod_item if estado.cod_item else ""
            nombre = str(estado.nombre) if estado.nombre else ""
            observaciones = str(estado.observaciones) if estado.observaciones else ""
            tipo = str(estado.tipo) if estado.tipo else ""
            orden = estado.orden if estado.orden else ""
            serialized_estados.append({
                'empresa': empresa,
                'cod_modelo': cod_modelo,
                'cod_item': cod_item,
                'nombre': nombre,
                'observaciones': observaciones,
                'tipo': tipo,
                'orden': orden
            })
        return jsonify(serialized_estados)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_track')
@jwt_required()
@cross_origin()
def obtener_orden_compra_track():
    try:
        query = StOrdenCompraTracking.query()
        seguimientos = query.all()
        serialized_seguimientos = []
        for seguimiento in seguimientos:
            cod_po = seguimiento.cod_po if seguimiento.cod_po else ""
            tipo_comprobante = seguimiento.tipo_comprobante if seguimiento.tipo_comprobante else ""
            empresa = seguimiento.empresa if seguimiento.empresa else ""
            observaciones = seguimiento.observaciones if seguimiento.observaciones else ""
            fecha_pedido = datetime.strftime(seguimiento.fecha_pedido,"%d/%m/%Y") if seguimiento.fecha_pedido else ""
            fecha_transito = datetime.strftime(seguimiento.fecha_transito,"%d/%m/%Y") if seguimiento.fecha_transito else ""
            fecha_puerto = datetime.strftime(seguimiento.fecha_puerto,"%d/%m/%Y") if seguimiento.fecha_puerto else ""
            fecha_llegada = datetime.strftime(seguimiento.fecha_llegada,"%d/%m/%Y") if seguimiento.fecha_llegada else ""
            fecha_en_bodega = seguimiento.fecha_en_bodega if seguimiento.fecha_en_bodega else ""
            estado = seguimiento.estado if seguimiento.estado else ""
            buque = seguimiento.buque if seguimiento.buque else ""
            naviera = seguimiento.naviera if seguimiento.naviera else ""
            flete = seguimiento.flete if seguimiento.flete else ""
            agente_aduanero = seguimiento.agente_aduanero if seguimiento.agente_aduanero else ""
            puerto_origen = seguimiento.puerto_origen if seguimiento.puerto_origen else ""
            usuario_crea = seguimiento.usuario_crea if seguimiento.usuario_crea else ""
            fecha_crea = datetime.strftime(seguimiento.fecha_crea,"%d/%m/%Y") if seguimiento.fecha_crea else ""
            usuario_modifica = seguimiento.usuario_modifica if seguimiento.usuario_modifica else ""
            fecha_modifica = datetime.strftime(seguimiento.fecha_modifica,"%d/%m/%Y") if seguimiento.fecha_modifica else ""
            serialized_seguimientos.append({
                'cod_po': cod_po,
                'tipo_comprobante': tipo_comprobante,
                'empresa': empresa,
                'observaciones': observaciones,
                'fecha_pedido': fecha_pedido,
                'fecha_transito': fecha_transito,
                'fecha_puerto': fecha_puerto,
                'fecha_llegada': fecha_llegada,
                'feche_en_bodega': fecha_en_bodega,
                'estado': estado,
                'buque': buque,
                'naviera': naviera,
                'flete': flete,
                'agente_aduanero': agente_aduanero,
                'puerto_origen': puerto_origen,
                'usuario_crea': usuario_crea,
                'fecha_crea': fecha_crea,
                'usuario_modifica': usuario_modifica,
                'fecha_modifica': fecha_modifica,
            })
        return jsonify(serialized_seguimientos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/packinglist')
@jwt_required()
@cross_origin()
def obtener_packinlist():
    try:
        query = StPackinglist.query()
        packings = query.all()
        serialized_packing = []
        for packing in packings:
            cod_po = packing.cod_po if packing.cod_po else ""
            tipo_comprobante = packing.tipo_comprobante if packing.tipo_comprobante else ""
            empresa = packing.empresa if packing.empresa else ""
            secuencia = packing.secuencia if packing.secuencia else ""
            cod_producto = packing.cod_producto if packing.cod_producto else ""
            cantidad = packing.cantidad if packing.cantidad else ""
            fob = packing.fob if packing.fob else ""
            cod_producto_modelo = packing.cod_producto_modelo if packing.cod_producto_modelo else ""
            unidad_medida = packing.unidad_medida if packing.unidad_medida else ""
            usuario_crea = packing.usuario_crea if packing.usuario_crea else ""
            fecha_crea = datetime.strftime(packing.fecha_crea,"%d/%m/%Y") if packing.fecha_crea else ""
            usuario_modifica = packing.usuario_modifica if packing.usuario_modifica else ""
            fecha_modifica = datetime.strftime(packing.fecha_modifica,"%d/%m/%Y") if packing.fecha_modifica else ""
            serialized_packing.append({
                'cod_po': cod_po,
                'tipo_comprobante': tipo_comprobante,
                'empresa': empresa,
                'secuencia': secuencia,
                'cod_producto': cod_producto,
                'cantidad': cantidad,
                'fob': fob,
                'cod_producto_modelo': cod_producto_modelo,
                'unidad_medida': unidad_medida,
                'usuario_crea': usuario_crea,
                'fecha_crea': fecha_crea,
                'usuario_modifica': usuario_modifica,
                'fecha_modifica': fecha_modifica,
            })
        return jsonify(serialized_packing)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/nombre_productos')
@jwt_required()
@cross_origin()
def obtener_nombre_productos():
    try:
        query = StDespiece.query()
        nom_productos = query.all()
        serialized_nomproductos = []
        for nombres in nom_productos:
            cod_despiece = nombres.cod_despiece if nombres.cod_despiece else ""
            empresa = nombres.empresa if nombres.empresa else ""
            nombre_c = nombres.nombre_c if nombres.nombre_c else ""
            nombre_i = nombres.nombre_i if nombres.nombre_i else ""
            nombre_e = nombres.nombre_e if nombres.nombre_e else ""
            serialized_nomproductos.append({
                'cod_despiece': cod_despiece,
                'empresa': empresa,
                'nombre_c': nombre_c,
                'nombre_i': nombre_i,
                'nombre_e': nombre_e
            })
        return jsonify(serialized_nomproductos)

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/prod_despiece')
@jwt_required()
@cross_origin()
def obtener_producto_despiece():
    try:
        query = StProductoDespiece.query()
        prod_despiece = query.all()
        serialized_prodespiece = []
        for prod in prod_despiece:
            cod_despiece = prod.cod_despiece if prod.cod_despiece else ""
            secuencia = prod.secuencia if prod.secuencia else ""
            cod_color = prod.cod_color if prod.cod_color else ""
            empresa = prod.empresa if prod.empresa else ""
            cod_producto = prod.cod_producto if prod.cod_producto else ""
            fecha_creacion = prod.fecha_creacion if prod.fecha_creacion else ""
            serialized_prodespiece.append({
                'cod_despiese': cod_despiece,
                'secuencia': secuencia,
                'cod_color': cod_color,
                'empresa': empresa,
                'cod_producto': cod_producto,
                'fecha_creacion': fecha_creacion,
            })
        return jsonify(serialized_prodespiece)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/tgmodelo')
@jwt_required()
@cross_origin()
def obtener_tgmodelo():
    try:
        query = TgModelo.query()
        tgmodels = query.all()
        #print(estados)
        serialized_tgmodelo = []
        for tgmodelo in tgmodels:
            serialized_tgmodelo.append({
                'empresa': tgmodelo.empresa,
                'cod_modelo': tgmodelo.cod_modelo,
                'nombre': tgmodelo.nombre
            })
        return jsonify(serialized_tgmodelo)
    
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
#METODOS POST

@bp.route('/orden_compra_cab', methods = ['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_cab():
    try:
        data = request.get_json()
        fecha_crea = date.today()#funcion para que se asigne la fecha actual al momento de crear la oden de compra
        fecha_modifica = datetime.strptime(data['fecha_modifica'], '%d/%m/%Y').date()

        #busqueda para que se asigne de forma automatica la ciudad al buscarla por el cod_proveedor
        busq_ciudad = TcCoaProveedor.query().filter_by(ruc=data['cod_proveedor']).first()
        ciudad = busq_ciudad.ciudad_matriz

        #busqueda para obtener el nombre del estado para la orden de compra
        estado = TgModeloItem.query().filter_by(cod_modelo=data['cod_modelo'], cod_item=data['cod_item']).first()
        estado_nombre = estado.nombre if estado else ''
       
        # Generate the cod_po using the asigna_cod_comprobante function
        cod_po = asigna_cod_comprobante(data['empresa'], data['tipo_comprobante'], data['cod_agencia'])

        orden = StOrdenCompraCab(
            empresa=data['empresa'],
            cod_po=cod_po,
            bodega=data['bodega'],
            cod_agencia=data['cod_agencia'],
            tipo_comprobante=data['tipo_comprobante'],
            cod_proveedor=data['cod_proveedor'],
            nombre=data['nombre'],
            cod_po_padre=data['cod_po_padre'],
            usuario_crea=data['usuario_crea'].upper(),
            fecha_crea=fecha_crea,
            usuario_modifica=data['usuario_modifica'].upper(),
            fecha_modifica=fecha_modifica,
            cod_modelo=data['cod_modelo'],
            cod_item=data['cod_item'],
            ciudad = ciudad if ciudad else "",
            estado = estado_nombre,
        )
        db.session.add(orden)
        db.session.commit()
        return jsonify({'mensaje': cod_po})

    except ValueError as ve:
        # Capturar y manejar el error específico de ValueError
        error_message = str(ve)
        return jsonify({'error': error_message}), 500

    except Exception as e:
        # Manejar otros errores y proporcionar un mensaje personalizado
        error_message = f"Se produjo un error: {str(e)}"
        return jsonify({'error': error_message}), 500
    
def asigna_cod_comprobante(p_cod_empresa, p_cod_tipo_comprobante, p_cod_agencia):
    # Realizar las operaciones de base de datos necesarias para generar el código comprobante
    # Ejecutar consultas SQL sin formato usando la función `texto` de SQLAlchemy

    # Encuentra el registro en la tabla 'orden'
    sql = text("SELECT * FROM contabilidad.orden WHERE empresa=:empresa AND bodega=:bodega AND tipo_comprobante=:tipo_comprobante")
    result = db.session.execute(sql, {'empresa': p_cod_empresa, 'bodega': p_cod_agencia, 'tipo_comprobante': p_cod_tipo_comprobante})
    print(result)
    orden = result.fetchone()
    print(orden)

    if orden is None:
        # Generar una excepción si no se encuentra el registro
        raise ValueError('Secuencia de comprobante no existe')

    # Actualizar la secuencia comprobante
    sql = text("UPDATE contabilidad.orden SET numero_comprobante=numero_comprobante+1 WHERE empresa=:empresa AND bodega=:bodega AND tipo_comprobante=:tipo_comprobante")
    db.session.execute(sql, {'empresa': p_cod_empresa, 'bodega': p_cod_agencia, 'tipo_comprobante': p_cod_tipo_comprobante})

    print(sql)
    # Acceder a los valores de las columnas por su índice en la tupla
    sigla_comprobante = orden[3]
    numero_comprobante = orden[4]

    # Convertir el número de comprobante a cadena de texto y generar el código comprobante
    comprobante_code = sigla_comprobante + str(numero_comprobante + 1).zfill(6)
    print(comprobante_code)

    return comprobante_code


@bp.route('/orden_compra_det', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_det():
    try:
        data = request.get_json()
        #print(data)
        fecha_crea = date.today()#funcion para que se asigne la fecha actual al momento de crear el detalle de la oden de compra
        #fecha_modifica = date.today()

        empresa = data['empresa']
        cod_po = data['cod_po']
        usuario_crea=data['usuario_crea'].upper()
        
        # Verificar si el usuario existe en la base de datos
        usuario = Usuario.query().filter_by(usuario_oracle=usuario_crea).first()
        if not usuario:
            return jsonify({'mensaje': 'El usuario no existe.'}), 404

        cod_po_no_existe = [] #Lista para almacenar los codigo de productos que no existen
        print(data)
        for order in data['orders']:
            print(order)
            cod_producto = order['COD_PRODUCTO']

            #Verificar si el producto existe en la tabla de Productos
            query = Producto.query().filter_by(cod_producto = cod_producto).first()
            if query:
                secuencia = obtener_secuencia(cod_po)
                costo_sistema = query.costo
                unidad_medida = query.cod_unidad

                # Consultar la tabla StDespiece para obtener los valores correspondientes
                despiece = StProductoDespiece.query().filter_by(cod_producto=order['COD_PRODUCTO'], empresa = empresa).first() #usar la empresa
                if despiece is not None:
                    nombre_busq = StDespiece.query().filter_by(cod_despiece =despiece.cod_despiece).first()
                    nombre = nombre_busq.nombre_e
                    nombre_i = nombre_busq.nombre_i
                    nombre_c = nombre_busq.nombre_c
                else:
                    nombre_busq = Producto.query().filter_by(cod_producto = order['COD_PRODUCTO']).first()
                    nombre = nombre_busq.nombre
                    nombre_i = nombre_busq.nombre
                    nombre_c = nombre_busq.nombre

                detalle = StOrdenCompraDet(
                    exportar=order['AGRUPADO'],
                    cod_po=cod_po,
                    tipo_comprobante ='PO',
                    secuencia=secuencia,
                    empresa=empresa,
                    cod_producto=order['COD_PRODUCTO'],
                    cod_producto_modelo=order['COD_MODELO'],
                    nombre=nombre if nombre else None,
                    nombre_i=nombre_i if nombre_i else None,
                    nombre_c=nombre_c if nombre_c else None,
                    nombre_mod_prov = order['NOMBRE_PROVEEDOR'],
                    nombre_comercial = order['NOMBRE_COMERCIAL'],
                    costo_sistema=costo_sistema if costo_sistema else 0,
                    #fob=order['FOB'] if order['FOB'] else "",
                    cantidad_pedido=order['PEDIDO'],
                    #saldo_producto=order['SALDO_PRODUCTO'] if order['SALDO_PRODUCTO'] else order['PEDIDO'],
                    unidad_medida=unidad_medida,
                    usuario_crea=usuario_crea,
                    fecha_crea=fecha_crea,
                    #usuario_modifica=order['usuario_modifica'].upper(),
                    #fecha_modifica=fecha_modifica,
                )
                #detalle.fob_total = order['FOB'] * order['CANTIDAD_PEDIDO']
                db.session.add(detalle)
                db.session.commit()
                #secuencia = obtener_secuencia(order['COD_PO'])
            else:
                cod_po_no_existe.append(cod_producto)
        if cod_po_no_existe:
            return jsonify({'mensaje': 'Productos no generados.', 'cod_producto_no_existe': cod_po_no_existe})
        else:
            return jsonify({'mensaje': 'Detalle(s) de orden de compra creados exitosamente', 'cod_po': cod_po})
            
    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
def obtener_secuencia(cod_po):
    # Verificar si el cod_po existe en la tabla StOrdenCompraCab
    existe_cod_po_cab = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po).first()

    if existe_cod_po_cab is not None:
        print('EXISTE',existe_cod_po_cab.cod_po)
        # Si el cod_po existe en la tabla StOrdenCompraCab, verificar si existe en la tabla StOrdenCompraDet
        existe_cod_po_det = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po).first()

        if existe_cod_po_det is not None:
            print('EXISTE2',existe_cod_po_det.cod_po)
            # Si el cod_po existe en la tabla StOrdenCompraDet, obtener el último número de secuencia
            max_secuencia = db.session.query(func.max(StOrdenCompraDet.secuencia)).filter_by(cod_po=cod_po).distinct().scalar()
            print('MAXIMO',max_secuencia)
            nueva_secuencia = int(max_secuencia) + 1
            print('PROXIMO',nueva_secuencia)
            return nueva_secuencia
        else:
            # Si el cod_po no existe en la tabla StOrdenCompraDet, generar secuencia desde 1
            nueva_secuencia = 1
            print('Secuencia de inicio', nueva_secuencia)
            return nueva_secuencia
    else:
        # Si el cod_po no existe en la tabla StOrdenCompraCab, mostrar mensaje de error
        raise ValueError('La Orden de Compra no existe.')
    
@bp.route('/packinglist', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_packinglist():
    try:
        data = request.get_json()
        fecha_crea = date.today()
        fecha_modifica = datetime.strptime(data['fecha_modifica'], '%d/%m/%Y').date()
        packinlist = StPackinglist(
            cod_po = data['cod_po'],
            tipo_comprobante = data['tipo_comprobante'],
            empresa = data['empresa'],
            secuencia = data['secuencia'],
            cod_producto = data['cod_producto'],
            cantidad = data['cantidad'],
            fob = data['fob'],
            cod_producto_modelo = data['cod_producto_modelo'],
            unidad_medida = data['unidad_medida'],
            usuario_crea = data['usuario_crea'].upper(),
            fecha_crea = fecha_crea,
            usuario_modifica = data['usuario_modifica'].upper(),
            fecha_modifica = fecha_modifica
        )
        db.session.add(packinlist)
        db.session.commit()
        return jsonify({'mensaje': 'Packinglist de orden de compra creado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_track', methods=['POST'])
@jwt_required()
@cross_origin()
def crear_orden_compra_track():
    try:
        data = request.get_json()
        fecha_pedido = datetime.strptime(data['fecha_pedido'], '%d/%m/%Y').date()         #datetime.datetime.strptime(data['fecha_pedido'], '%d%m%Y') if data['fecha_pedido'] else None
        fecha_transito = datetime.strptime(data['fecha_transito'], '%d/%m/%Y').date() 
        fecha_puerto = datetime.strptime(data['fecha_puerto'], '%d/%m/%Y').date() 
        fecha_llegada = datetime.strptime(data['fecha_llegada'], '%d/%m/%Y').date() 
        fecha_en_bodega = datetime.strptime(data['fecha_en_bodega'], '%d/%m/%Y').date() 
        fecha_crea = date.today() #funcion para que se asigne la fecha actual al momento de crear el detalle de la oden de compra
        fecha_modifica = datetime.strptime(data['fecha_modifica'], '%d/%m/%Y').date()
        tracking = StOrdenCompraTracking(
            cod_po = data['cod_po'],
            empresa = data['empresa'],
            tipo_comprobante = data['tipo_comprobante'],
            observaciones = data['observaciones'],
            fecha_pedido = fecha_pedido,
            fecha_transito = fecha_transito,
            fecha_puerto = fecha_puerto,
            fecha_llegada = fecha_llegada,
            fecha_en_bodega = fecha_en_bodega,
            estado = data['estado'],
            buque = data['buque'],
            naviera = data['naviera'],
            flete = data['flete'],
            agente_aduanero = data['agente_aduanero'],
            puerto_origen = data['puerto_origen'],
            usuario_crea = data['usuario_crea'].upper(),
            fecha_crea = fecha_crea,
            usuario_modifica = data['usuario_modifica'].upper(),
            fecha_modifica = fecha_modifica

        )
        db.session.add(tracking)
        db.session.commit()
        return jsonify({'mensaje': 'Tracking de orden de compra creado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500

# METODOS UPDATE DE TABLAS DE ORDEN DE COMPRA

@bp.route('/orden_compra_cab/<cod_po>/<empresa>/<tipo_comprobante>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_cab(cod_po,empresa,tipo_comprobante):
    try:
        orden = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po,empresa = empresa, tipo_comprobante = tipo_comprobante).first()
        if not orden:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404

        data = request.get_json()
        orden.empresa = data.get('empresa', orden.empresa)
        orden.cod_po = data.get('cod_po', orden.cod_po)
        orden.tipo_comprobante = data.get('tipo_comprobante', orden.tipo_comprobante)
        orden.cod_agencia = data.get('cod_agencia',orden.cod_agencia)
        orden.cod_proveedor = data.get('cod_proveedor', orden.cod_proveedor)
        orden.nombre = data.get('nombre', orden.nombre)
        orden.proforma = data.get('proforma', orden.proforma)
        orden.invoice = data.get('invoice', orden.invoice)
        orden.bl_no = data.get('bl_no', orden.bl_no)
        orden.cod_po_padre = data.get('cod_po_padre', orden.cod_po_padre)
        orden.usuario_crea = data.get('usuario_crea', orden.usuario_crea).upper()
        orden.fecha_crea = datetime.strptime(data.get('fecha_crea', str(orden.fecha_crea)), '%d/%m/%Y').date()
        orden.usuario_modifica = data.get('usuario_modifica', orden.usuario_modifica).upper()
        orden.fecha_modifica = datetime.strptime(data.get('fecha_modifica', str(orden.fecha_modifica)), '%d/%m/%Y').date()
        orden.cod_modelo = data.get('cod_modelo', orden.cod_modelo)
        orden.cod_item = data.get('cod_item', orden.cod_item)
        orden.bodega = data.get('bodega', orden.bodega)
        orden.ciudad = data.get('ciudad', orden.ciudad)
        orden.estado = data.get('estado', orden.estado)

        db.session.commit()

        return jsonify({'mensaje': 'Orden de compra actualizada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_det/<cod_po>/<empresa>/<secuencia>/<tipo_comprobante>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_det(cod_po,empresa,secuencia,tipo_comprobante):
    try:
        orden = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po,empresa = empresa,secuencia = secuencia, tipo_comprobante = tipo_comprobante).first()
        if not orden:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404
        
        data = request.get_json()
        # Consultar la tabla StDespiece para obtener los valores correspondientes
        '''despiece = StProductoDespiece.query().filter_by(cod_producto=data['cod_producto'], empresa = data['empresa']).first() #usar la empresa
        if despiece is not None:
            nombre_busq = StDespiece.query().filter_by(cod_despiece =despiece.cod_despiece).first()
            nombre = nombre_busq.nombre_e
            nombre_i = nombre_busq.nombre_i
            nombre_c = nombre_busq.nombre_c
        else:
            nombre_busq = Producto.query().filter_by(cod_producto = data['cod_producto']).first()
            nombre = nombre_busq.nombre
            nombre_i = nombre_busq.nombre
            nombre_c = nombre_busq.nombre'''
        
        #orden.exportar = data.get('exportar',orden.exportar)
        #orden.cod_po = data.get('cod_po', orden.cod_po)
        #orden.tipo_comprobante = data.get('tipo_comprobante',orden.tipo_comprobante)
        orden.secuencia = data.get('secuencia', orden.secuencia)
        orden.empresa = data.get('empresa', orden.empresa)
        orden.cod_producto = data.get('cod_producto', orden.cod_producto)
        orden.cod_producto_modelo = data.get('cod_producto_modelo', orden.cod_producto_modelo)
        #orden.nombre = nombre if nombre else None
        #orden.nombre_i = nombre_i if nombre_i else None
        #orden.nombre_c = nombre_c if nombre_c else None
        orden.nombre_mod_prov = data.get('nombre_mod_prov', orden.nombre_mod_prov)
        orden.nombre_comercial = data.get('nombre_comercial', orden.nombre_comercial)
        orden.costo_sistema = data.get('costo_sistema', orden.costo_sistema)
        orden.fob = data.get('fob', orden.fob)
        orden.fob_total = data.get('fob_total', orden.fob_total)
        #orden.cantidad_pedido = data.get('cantidad_pedido', orden.cantidad_pedido)
        orden.saldo_producto = data.get('saldo_producto', orden.saldo_producto)
        orden.unidad_medida = data.get('unidad_medida', orden.unidad_medida)
        orden.usuario_crea = data.get('usuario_crea', orden.usuario_crea).upper()
        orden.usuario_modifica = data.get('usuario_modifica', orden.usuario_modifica).upper()
        orden.fecha_modifica = datetime.strptime(data.get('fecha_modifica', str(orden.fecha_modifica)), '%d/%m/%Y').date()

        # Calcula el valor de fob_total
        orden.fob_total = orden.fob * float(orden.cantidad_pedido)

        if 'costo_cotizado' in data:
            orden.costo_cotizado = data['costo_cotizado']
            if orden.costo_cotizado is not None:
                orden.fecha_costo = date.today()

        db.session.commit()

        return jsonify({'mensaje': 'Detalle de Orden de compra actualizada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_tracking/<cod_po>/<empresa>/<tipo_comprobante>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_trancking(cod_po,empresa,tipo_comprobante):
    try:
        tracking = db.session.query(StOrdenCompraTracking).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).first()
        if not tracking:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404
        
        fecha_modifica = date.today()
        
        data = request.get_json()
        tracking.cod_po = data.get('cod_po', tracking.cod_po)
        tracking.tipo_comprobante = data.get('tipo_comprobante', tracking.tipo_comprobante)
        tracking.empresa = data.get('empresa', tracking.empresa)
        tracking.observaciones = data.get('observaciones', tracking.observaciones)
        tracking.fecha_pedido = datetime.strptime(data.get('fecha_pedido', str(tracking.fecha_pedido)), '%d/%m/%Y').date()
        tracking.fecha_transito = datetime.strptime(data.get('fecha_transito', str(tracking.fecha_transito)), '%d/%m/%Y').date()
        tracking.fecha_puerto = datetime.strptime(data.get('fecha_puerto', str(tracking.fecha_puerto)), '%d/%m/%Y').date()
        tracking.fecha_llegada = datetime.strptime(data.get('fecha_llegada', str(tracking.fecha_llegada)), '%d/%m/%Y').date()
        tracking.fecha_en_bodega = datetime.strptime(data.get('fecha_en_bodega', str(tracking.fecha_en_bodega)), '%d/%m/%Y').date()
        tracking.estado = data.get('estado', tracking.estado)
        tracking.buque = data.get('buque', tracking.buque)
        tracking.naviera = data.get('naviera', tracking.naviera)
        tracking.flete = data.get('flete', tracking.flete)
        tracking.agente_aduanero = data.get('agente_aduanero', tracking.agente_aduanero)
        tracking.puerto_origen = data.get('puerto_origen', tracking.puerto_origen)
        tracking.fecha_crea = datetime.strptime(data.get('fecha_crea', str(tracking.fecha_crea)), '%d/%m/%Y').date()
        tracking.usuario_modifica = data.get('usuario_modifica', tracking.usuario_modifica).upper()
        tracking.fecha_modifica = fecha_modifica

        db.session.commit()

        return jsonify({'mensaje': 'Tracking de Orden de compra actualizada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_packinglist/<cod_po>/<empresa>', methods=['PUT'])
@jwt_required()
@cross_origin()
def actualizar_orden_compra_packinlist(cod_po,empresa):
    try:
        packinglist = db.session.query(StPackinglist).filter_by(cod_po=cod_po,empresa=empresa).first()
        if not packinglist:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404
        
        data = request.get_json()
        packinglist.cod_po = data.get('cod_po', packinglist.cod_po)
        packinglist.empresa = data.get('empresa', packinglist.empresa)
        packinglist.secuencia = data.get('secuencia', packinglist.secuencia)
        packinglist.cod_producto = data.get('cod_producto', packinglist.cod_producto)
        packinglist.cantidad = data.get('cantidad', packinglist.cantidad)
        packinglist.fob = data.get('fob', packinglist.fob)
        packinglist.cod_producto_modelo = data.get('cod_producto_modelo', packinglist.cod_producto_modelo)
        packinglist.unidad_medida = data.get('unidad_medida', packinglist.unidad_medida)
        packinglist.usuario_crea = data.get('usuario_crea', packinglist.usuario_crea).upper()
        packinglist.fecha_crea = datetime.strptime(data.get('fecha_crea', str(packinglist.fecha_crea)), '%d/%m/%Y').date()
        packinglist.usuario_modifica = data.get('usuario_modifica', packinglist.usuario_modifica).upper()
        packinglist.fecha_modifica = datetime.strptime(data.get('fecha_modifica', str(packinglist.fecha_modifica)), '%d/%m/%Y').date()

        db.session.commit()

        return jsonify({'mensaje': 'Packinglist de Orden de compra actualizada exitosamente.'})
    
    except Exception as e:
        logger.exception(f"Error al actualizar: {str(e)}")
        #logging.error('Ocurrio un error: %s',e)
        return jsonify({'error': str(e)}), 500
    
#METODOS DELETE PARA ORDENES DE COMPRA

@bp.route('/orden_compra_cab/<cod_po>/<empresa>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_cab(cod_po, empresa,tipo_comprobante):
    try:
        orden = db.session.query(StOrdenCompraCab).filter_by(cod_po=cod_po, empresa=empresa,tipo_comprobante=tipo_comprobante).first()
        if not orden:
            return jsonify({'mensaje': 'La orden de compra no existe.'}), 404

        db.session.delete(orden)
        db.session.commit()

        return jsonify({'mensaje': 'Orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_det/<cod_po>/<empresa>/<secuencia>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_det(cod_po, empresa, secuencia,tipo_comprobante):
    try:
        detalle = db.session.query(StOrdenCompraDet).filter_by(cod_po=cod_po, empresa=empresa, secuencia = secuencia, tipo_comprobante = tipo_comprobante).first()
        if not detalle:
            return jsonify({'mensaje': 'Detalle de orden de compra no existe.'}), 404

        db.session.delete(detalle)
        db.session.commit()

        return jsonify({'mensaje': 'Detalle de orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_tracking/<cod_po>/<empresa>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_tracking(cod_po, empresa, tipo_comprobante):
    try:
        tracking = db.session.query(StOrdenCompraTracking).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante=tipo_comprobante).first()
        if not tracking:
            return jsonify({'mensaje': 'Tracking de orden de compra no existe.'}), 404

        db.session.delete(tracking)
        db.session.commit()

        return jsonify({'mensaje': 'Tracking de orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@bp.route('/orden_compra_packinglist/<cod_po>/<empresa>/<tipo_comprobante>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def eliminar_orden_compra_packinglist(cod_po, empresa, tipo_comprobante):
    try:
        packing = db.session.query(StPackinglist).filter_by(cod_po=cod_po, empresa=empresa, tipo_comprobante = tipo_comprobante).first()
        if not packing:
            return jsonify({'mensaje': 'Packinglist de orden de compra no existe.'}), 404

        db.session.delete(packing)
        db.session.commit()

        return jsonify({'mensaje': 'Packinglist de orden de compra eliminada exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al eliminar: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/doc_elect_sri', methods=['POST'])
@jwt_required()
@cross_origin()
def cargaLote():
    try:
        data = request.get_json()
        print(data)
        tracking = StOrdenCompraTracking(
            #cod_po = data['cod_po'],
            #empresa = data['empresa'],
            #tipo_comprobante = data['tipo_comprobante'],
        )
       # db.session.add(kingtrac)
        #db.session.commit()
        return jsonify({'mensaje': 'Tracking de orden de compra creado exitosamente.'})

    except Exception as e:
        logger.exception(f"Error al consultar: {str(e)}")
        return jsonify({'error': str(e)}), 500

