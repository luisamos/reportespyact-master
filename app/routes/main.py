from __future__ import annotations

import json
from datetime import datetime

from flask import Blueprint, abort, jsonify, make_response, render_template, request

from ..services import query_service as qs

main_bp = Blueprint('main', __name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _obj_consulta(anio, ubigeo, act, fun='', nivel='', sector='',
                  pliego='', ejecutora='', cat='', amb='') -> tuple:
    """Devuelve tupla hasheable para el cache del servicio."""
    return (anio, str(ubigeo), 'P', act, fun, nivel, sector, pliego, ejecutora, cat, amb)


def _normalize_base_url(raw: str) -> str:
  if not raw:
    return ''
  url = raw.strip()
  if url and not url.startswith(('http://', 'https://')):
    url = f'http://{url}'
  return url.rstrip('/')


def _base_url() -> str:
  from flask import current_app
  cfg = current_app.config
  raw = cfg['BASE_URL']
  return _normalize_base_url(raw)


def _checked(act: str) -> dict:
  return {
    'pchecked': 'checked' if act in ('1', '2') else '',
    'achecked': 'checked' if act in ('1', '3') else '',
  }

def _is_valid_ubigeo(ubigeo: str) -> bool:
  """Valida formato de ubigeo permitido por el reporte (2, 4 o 6 dígitos)."""
  return ubigeo.isdigit() and len(ubigeo) in (2, 4, 6)


# ---------------------------------------------------------------------------
# Rutas principales
# ---------------------------------------------------------------------------

@main_bp.route('/ping', methods=['GET'])
def ping():
    """Endpoint de salud para validar que el contenedor recibe tráfico."""
    return jsonify({'status': 'ok'}), 200


@main_bp.route('/diag/request', methods=['GET'])
def diag_request():
    """
    Diagnóstico de ruteo/proxy.
    Permite verificar qué path está recibiendo Flask detrás del orquestador.
    """
    forwarded_headers = {
        k: request.headers.get(k, '')
        for k in (
            'Host',
            'X-Forwarded-For',
            'X-Forwarded-Host',
            'X-Forwarded-Proto',
            'X-Forwarded-Port',
            'X-Forwarded-Prefix',
            'X-Original-URI',
            'X-Rewrite-URL',
        )
    }
    return jsonify({
        'method': request.method,
        'url': request.url,
        'base_url': request.base_url,
        'host_url': request.host_url,
        'path': request.path,
        'full_path': request.full_path,
        'script_root': request.script_root,
        'url_root': request.url_root,
        'headers': forwarded_headers,
    }), 200

@main_bp.route('/<int:anio>/<ubigeo>', defaults={'act': '1', 'sec': ''}, methods=['GET'], strict_slashes=False)
@main_bp.route('/<int:anio>/<ubigeo>/<act>/', defaults={'sec': ''}, methods=['GET'], strict_slashes=False)
@main_bp.route('/<int:anio>/<ubigeo>/<act>/<sec>/', methods=['GET'], strict_slashes=False)
def home(anio, ubigeo, act, sec):
  if not _is_valid_ubigeo(str(ubigeo)):
    abort(404)

  anio = str(anio)  # normalizar a string para templates y servicios
  demo = request.args.get('ppto', '')
  amb  = request.args.get('amb', '')
  base = _base_url()

  nivel   = qs.get_nivel(_obj_consulta(anio, ubigeo, act, sector=sec, cat=demo, amb=amb))
  funcion = qs.get_funcion(anio, ubigeo, act)
  ppto    = qs.get_ppto(anio, ubigeo, act, '')
  ubigeo_ = qs.get_ubigeo(ubigeo)
  if not ubigeo_:
    abort(404)
  fecha   = qs.get_fecha()

  link_comp = (
      base + '%2F' + anio + '%2F' + ubigeo + '%2F' + act
      if not sec else
      base + '%2F' + anio + '%2F' + ubigeo + '%2F' + act + '%2F' + sec
  )

  return render_template(
      '/reporte-proy-act/index.html',
      act=act, sec=sec, amb=amb, anio=anio,
      cod_ubigeo=ubigeo, fecha=fecha,
      title='Consulta de Reporte de Inversión Pública',
      cat=demo, nivel=nivel, funcion=funcion, ppto=ppto,
      base=base, ubigeo=ubigeo_, checked=_checked(act), link=link_comp,
  )


@main_bp.route('/violencia-familiar/<int:anio>/<ubigeo>/<act>')
def home_violencia(anio, ubigeo, act):
    anio = str(anio)
    base    = _base_url()
    nivel   = qs.get_nivel(_obj_consulta(anio, ubigeo, act, cat='0080'))
    funcion = qs.get_funcion(anio, ubigeo, act)
    ppto    = qs.get_ppto(anio, ubigeo, act, '')
    ubigeo_ = qs.get_ubigeo(ubigeo)
    fecha   = qs.get_fecha()

    link_comp = (
        'https%3A%2F%2Fvisor.geoperu.gob.pe%2Freportespyact%2Fviolencia-familiar%2F'
        + anio + '%2F' + ubigeo + '%2F' + act
    )

    return render_template(
        '/reporte-proy-act/index-violencia.html',
        act=act, sec='', cat='0080', anio=anio,
        cod_ubigeo=ubigeo,
        title='Consulta de Reporte de Inversión Pública',
        nivel=nivel, fecha=fecha, funcion=funcion, ppto=ppto,
        base=base, ubigeo=ubigeo_, checked=_checked(act), link=link_comp,
    )


# ---------------------------------------------------------------------------
# Endpoints AJAX (POST)
# ---------------------------------------------------------------------------

@main_bp.route('/nivel/', methods=['GET', 'POST'])
def home_sector():
    d = request.get_json()
    nivel = qs.get_nivel(_obj_consulta(
        d['anio'], d['ubigeo'], d['act'],
        fun=d['fun'], sector=d['sec'], cat=d['cat'], amb=d['amb'],
    ))
    return render_template(
        '/reporte-proy-act/data.html',
        nivel=nivel, anio=d['anio'], cod_ubigeo=str(d['ubigeo']),
        act=d['act'], fun=d['fun'], cat=d['cat'], sec=d['sec'], amb=d['amb'],
    )


@main_bp.route('/sector', methods=['GET', 'POST'])
def home_nivel():
    d = request.get_json()
    a = _obj_consulta(d['anio'], d['ubigeo'], d['act'],
                      fun=d['fun'], nivel=d['nivel'], sector=d['sec'],
                      cat=d['cat'], amb=d['amb'])
    sector = qs.get_sector(a)
    return render_template('/reporte-proy-act/sector.html',
                           sector=sector, a=a, orden=d['orden'])


@main_bp.route('/pliego', methods=['GET', 'POST'])
def home_pliego():
    d = request.get_json()
    a = _obj_consulta(d['anio'], d['ubigeo'], d['act'],
                      fun=d['fun'], nivel=d['nivel'], sector=d['sector'],
                      cat=d['cat'], amb=d['amb'])
    pliego = qs.get_pliego(a)
    return render_template('/reporte-proy-act/pliego.html',
                           pliego=pliego, a=a, orden=d['orden'])


@main_bp.route('/ejecutora', methods=['GET', 'POST'])
def home_ejecutora():
    d = request.get_json()
    a = _obj_consulta(d['anio'], d['ubigeo'], d['act'],
                      fun=d['fun'], nivel=d['nivel'], sector=d['sector'],
                      pliego=d['pliego'], cat=d['cat'], amb=d['amb'])
    ejecutora = qs.get_ejecutora(a)
    return render_template('/reporte-proy-act/ejecutora.html',
                           ejecutora=ejecutora, a=a, orden=d['orden'])


@main_bp.route('/proyecto', methods=['GET', 'POST'])
def home_proyecto():
    d = request.get_json()
    a = _obj_consulta(d['anio'], d['ubigeo'], d['act'],
                      fun=d['fun'], nivel=d['nivel'], sector=d['sector'],
                      pliego=d['pliego'], ejecutora=d['ejecutora'],
                      cat=d['cat'], amb=d['amb'])
    proyecto = qs.get_proyecto(a)
    return render_template('/reporte-proy-act/data-proyecto.html',
                           proyecto=proyecto, anio=d['anio'])


@main_bp.route('/funcion', methods=['GET', 'POST'])
def home_funcion():
    d = request.get_json()
    funcion = qs.get_ppto(d['anio'], str(d['ubigeo']), d['act'], d['fun'])
    return render_template('reporte-proy-act/cboppto.html', ppto=funcion)


@main_bp.route('/nom-py', methods=['GET', 'POST'])
def home_nom_py():
    d = request.get_json()
    proyecto = qs.get_nom_py(d['anio'], str(d['ubigeo']), d['nom'], d['cod'])
    return render_template('/reporte-proy-act/data-proyecto.html',
                           proyecto=proyecto, anio=d['anio'])


# ---------------------------------------------------------------------------
# Reportes / iframes
# ---------------------------------------------------------------------------

@main_bp.route('/reporte_geoperu/<rptfile>/<layer>/<ocampo>/<valor>')
def geoperu_reporte(rptfile, layer, ocampo, valor):
    return render_template('geoperu_reporte.html',
                           rptfile=rptfile, olayer=layer,
                           ocampo=ocampo, valor=valor)


@main_bp.route('/reporte_geoperu/gobierno_local/<ubigeo>/<tip>')
@main_bp.route('/reporte_geoperu/gobierno_local/<ubigeo>/', defaults={'tip': '1'})
def report_muni(tip, ubigeo):
    _titles = {
        '18': ('DEL CANON MUNICIPAL 2020',
               'RECURSOS TOTALES DEL CANON Y SOBRECANON'),
        '07': ('DEL FONDO DE COMPENSACIÓN MUNICIPAL (FONCOMUN) 2020',
               'RECURSOS TOTALES DEL FONCOMÚN. PROYECTOS Y ACTIVIDADES'),
    }
    titulo, titulo2 = _titles.get(tip, (
        'DE LOS RECURSOS MUNICIPALES 2020',
        'RECURSOS MUNICIPALES. PROYECTOS Y ACTIVIDADES (NUEVOS SOLES)',
    ))
    g = qs.get_reporte_muni(tip, ubigeo)
    p = [x for x in g if x['cod_dist'] == ubigeo]
    return render_template(
        '/reporte-gobiernos-locales/layout.html',
        titulo=titulo, titulo2=titulo2,
        data_ubigeo=p, ubigeo=ubigeo, data=g,
    )


# ---------------------------------------------------------------------------
# Gráficos JSON
# ---------------------------------------------------------------------------

@main_bp.route('/grafico/<tipo>/<ubigeo>')
def graficos(tipo, ubigeo):
    return jsonify(qs.get_grafico(tipo, ubigeo))


@main_bp.route('/grafico-violencia/<ubigeo>')
def grafiviolencia(ubigeo):
    return jsonify(qs.get_grafico_violencia(ubigeo))


# ---------------------------------------------------------------------------
# PIP / proyectos especiales
# ---------------------------------------------------------------------------

@main_bp.route('/data-mef/cabecera/<codigo>')
def condorcanquipip(codigo):
    return jsonify(qs.get_pip_general(codigo))


@main_bp.route('/condorcanqui-proyectos/<codigo>')
def condorcanquiview(codigo):
    result = qs.get_pip_general(codigo)
    return render_template('grafico-pip-condorcanqui.html',
                           general=json.dumps(result))


@main_bp.route('/proyectos-historico/<codigo>')
def historicoview(codigo):
    result = qs.get_pip_general(codigo)
    now = datetime.now()
    fuente = ('Ministerio de Economía y Finanzas, información actualizada al '
              + now.strftime('%d/%m/%Y'))
    return render_template('grafico-pip-condorcanqui.html',
                           general=json.dumps(result), fuente=fuente)


@main_bp.route('/proyectos-satelite/<codigo>')
def pipsatelite(codigo):
    _images = {
        '2233960': ('2233960_a.jpeg', '2233960_b.jpeg'),
        '2089929': ('2089929_a.jpeg', '2089929_b.jpeg'),
        '2131095': ('2131095_a.jpeg', '2131095_b.jpeg'),
        '2131101': ('2131101_a.jpeg', '2131101_b.jpeg'),
    }
    i_antes, i_despues = _images.get(codigo, ('', ''))
    return render_template('pip-satelite.html',
                           base=_base_url(),
                           i_antes=i_antes, i_despues=i_despues)


# ---------------------------------------------------------------------------
# Páginas estáticas / extras
# ---------------------------------------------------------------------------

@main_bp.route('/observaciones')
def front():
    return render_template('front.html', base=_base_url())
