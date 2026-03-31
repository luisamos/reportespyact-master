"""
Servicio de consultas basado íntegramente en el modelo GastoAnual.

Todo el drill-down (nivel → sector → pliego → ejecutora → proyecto),
los dropdowns de filtros y los gráficos se resuelven contra
ide.gasto_anual via SQLAlchemy — sin stored procedures ni tablas separadas.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import requests
from decimal import Decimal

from sqlalchemy import Numeric as SANumeric
from sqlalchemy import and_, case, cast, func, literal, select, text
from sqlalchemy import String as SAString

from ..extensions import db, cache
from ..models.gasto import GastoAnual


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _rows(result) -> list[dict]:
    return [dict(row) for row in result.mappings()]


def _ubigeo_parts(ubigeo: str) -> tuple[str, str, str]:
    dept = ubigeo[:2] if len(ubigeo) >= 2 else ''
    prov = ubigeo[2:4] if len(ubigeo) >= 4 else ''
    dist = ubigeo[4:6] if len(ubigeo) >= 6 else ''
    return dept, prov, dist


def _avance():
    """
    Expresión SQLAlchemy: devengado * 100 / pim, redondeado a 2 decimales.
    Usa cast explícito a Numeric para evitar división entera en PostgreSQL.
    """
    _zero = literal(Decimal('0'), type_=SANumeric(18, 2))
    pim = func.coalesce(func.sum(GastoAnual.monto_pim), _zero)
    dev = func.coalesce(func.sum(GastoAnual.monto_devengado), _zero)
    return case(
        (pim > 0, func.round(dev * 100 / pim, 2)),
        else_=_zero,
    ).label('avance')


def _add_id(rows: list[dict]) -> list[dict]:
    """Agrega id secuencial y convierte avance a float para el template."""
    result = []
    for i, r in enumerate(rows):
        row = dict(r)
        row['id'] = i + 1
        row['avance'] = float(row.get('avance') or 0)
        result.append(row)
    return result


def _build_filters(params: tuple) -> list:
    """
    Construye la lista de filtros SQLAlchemy a partir de los parámetros
    del ObjConsulta: (anio, ubigeo, _, act, fun, nivel, sector, pliego, ejecutora, cat, amb)
    """
    p = list(params) + [''] * max(0, 11 - len(params))
    anio, ubigeo, _, act, fun, nivel_gov, sector, pliego, ejecutora, cat, amb = p[:11]

    dept, prov, dist = _ubigeo_parts(str(ubigeo))
    filters = []

    if anio:
        filters.append(GastoAnual.ano_eje == int(anio))
    if dept:
        filters.append(GastoAnual.departamento_ejecutora == dept)
    if prov:
        filters.append(GastoAnual.provincia_ejecutora == prov)
    if dist:
        filters.append(GastoAnual.distrito_ejecutora == dist)
    if act and act != '1':
        filters.append(GastoAnual.tipo_act_proy == act)
    if fun:
        filters.append(GastoAnual.funcion == fun)
    if nivel_gov:
        filters.append(GastoAnual.nivel_gobierno == nivel_gov)
    if sector:
        filters.append(GastoAnual.sector == sector)
    if pliego:
        filters.append(GastoAnual.pliego == pliego)
    if ejecutora:
        filters.append(GastoAnual.sec_ejec == ejecutora)
    if cat:
        filters.append(GastoAnual.programa_ppto == cat)

    return filters


# ---------------------------------------------------------------------------
# Drill-down: nivel → sector → pliego → ejecutora → proyecto
# ---------------------------------------------------------------------------

@cache.memoize(timeout=300)
def get_nivel(params: tuple) -> list[dict]:
    filters = _build_filters(params)
    stmt = (
        select(
            GastoAnual.nivel_gobierno.label('idnivelgobierno'),
            GastoAnual.nivel_gobierno_nombre.label('nombre'),
            func.coalesce(func.sum(GastoAnual.monto_pia), 0).label('pia'),
            func.coalesce(func.sum(GastoAnual.monto_pim), 0).label('pim'),
            func.coalesce(func.sum(GastoAnual.monto_devengado), 0).label('devengado'),
            func.coalesce(func.sum(GastoAnual.monto_girado), 0).label('girado'),
            _avance(),
        )
        .where(and_(*filters) if filters else True)
        .group_by(GastoAnual.nivel_gobierno, GastoAnual.nivel_gobierno_nombre)
        .order_by(
            # Orden fijo: Nacional(E) → Regional(R) → Local(M)
            case(
                (GastoAnual.nivel_gobierno == 'E', 1),
                (GastoAnual.nivel_gobierno == 'R', 2),
                (GastoAnual.nivel_gobierno == 'M', 3),
                else_=4,
            )
        )
    )
    return _add_id(_rows(db.session.execute(stmt)))


@cache.memoize(timeout=300)
def get_sector(params: tuple) -> list[dict]:
    filters = _build_filters(params)
    stmt = (
        select(
            GastoAnual.sector.label('idsector'),
            GastoAnual.sector_nombre.label('nombre'),
            func.coalesce(func.sum(GastoAnual.monto_pia), 0).label('pia'),
            func.coalesce(func.sum(GastoAnual.monto_pim), 0).label('pim'),
            func.coalesce(func.sum(GastoAnual.monto_devengado), 0).label('devengado'),
            func.coalesce(func.sum(GastoAnual.monto_girado), 0).label('girado'),
            _avance(),
        )
        .where(and_(*filters) if filters else True)
        .group_by(GastoAnual.sector, GastoAnual.sector_nombre)
        .order_by(GastoAnual.sector)
    )
    return _add_id(_rows(db.session.execute(stmt)))


@cache.memoize(timeout=300)
def get_pliego(params: tuple) -> list[dict]:
    filters = _build_filters(params)
    stmt = (
        select(
            GastoAnual.pliego.label('idpliego'),
            GastoAnual.pliego_nombre.label('nombre'),
            func.coalesce(func.sum(GastoAnual.monto_pia), 0).label('pia'),
            func.coalesce(func.sum(GastoAnual.monto_pim), 0).label('pim'),
            func.coalesce(func.sum(GastoAnual.monto_devengado), 0).label('devengado'),
            func.coalesce(func.sum(GastoAnual.monto_girado), 0).label('girado'),
            _avance(),
        )
        .where(and_(*filters) if filters else True)
        .group_by(GastoAnual.pliego, GastoAnual.pliego_nombre)
        .order_by(GastoAnual.pliego)
    )
    return _add_id(_rows(db.session.execute(stmt)))


@cache.memoize(timeout=300)
def get_ejecutora(params: tuple) -> list[dict]:
    filters = _build_filters(params)
    stmt = (
        select(
            GastoAnual.sec_ejec.label('secejec'),
            GastoAnual.sector.label('idsector'),
            GastoAnual.pliego.label('idpliego'),
            GastoAnual.ejecutora_nombre.label('nombre'),
            func.coalesce(func.sum(GastoAnual.monto_pia), 0).label('pia'),
            func.coalesce(func.sum(GastoAnual.monto_pim), 0).label('pim'),
            func.coalesce(func.sum(GastoAnual.monto_devengado), 0).label('devengado'),
            func.coalesce(func.sum(GastoAnual.monto_girado), 0).label('girado'),
            _avance(),
        )
        .where(and_(*filters) if filters else True)
        .group_by(
            GastoAnual.sec_ejec, GastoAnual.sector,
            GastoAnual.pliego, GastoAnual.ejecutora_nombre,
        )
        .order_by(GastoAnual.sector, GastoAnual.pliego, GastoAnual.sec_ejec)
    )
    return _add_id(_rows(db.session.execute(stmt)))


@cache.memoize(timeout=300)
def get_proyecto(params: tuple) -> list[dict]:
    filters = _build_filters(params)
    stmt = (
        select(
            GastoAnual.producto_proyecto.label('idproy'),
            GastoAnual.producto_proyecto_nombre.label('proyecto'),
            GastoAnual.funcion_nombre.label('funcionnombre'),
            GastoAnual.nivel_gobierno.label('tipo_gobierno'),
            GastoAnual.sector,
            GastoAnual.pliego,
            func.coalesce(func.sum(GastoAnual.monto_pia), 0).label('pia'),
            func.coalesce(func.sum(GastoAnual.monto_pim), 0).label('pim'),
            func.coalesce(func.sum(GastoAnual.monto_devengado), 0).label('devengado'),
            func.coalesce(func.sum(GastoAnual.monto_girado), 0).label('girado'),
            _avance(),
        )
        .where(and_(*filters) if filters else True)
        .group_by(
            GastoAnual.producto_proyecto,
            GastoAnual.producto_proyecto_nombre,
            GastoAnual.funcion_nombre,
            GastoAnual.nivel_gobierno,
            GastoAnual.sector,
            GastoAnual.pliego,
        )
        .order_by(GastoAnual.nivel_gobierno, GastoAnual.sector, GastoAnual.pliego)
    )
    return _add_id(_rows(db.session.execute(stmt)))


# ---------------------------------------------------------------------------
# Dropdowns de filtros
# ---------------------------------------------------------------------------

@cache.memoize(timeout=300)
def get_funcion(anio: str, ubigeo: str, act: str) -> list[dict]:
    dept, prov, dist = _ubigeo_parts(ubigeo)
    filters = [GastoAnual.funcion.isnot(None)]
    if anio:
        filters.append(GastoAnual.ano_eje == int(anio))
    if dept:
        filters.append(GastoAnual.departamento_ejecutora == dept)
    if prov:
        filters.append(GastoAnual.provincia_ejecutora == prov)
    if dist:
        filters.append(GastoAnual.distrito_ejecutora == dist)
    if act and act != '1':
        filters.append(GastoAnual.tipo_act_proy == act)

    stmt = (
        select(
            GastoAnual.funcion.label('cod'),
            GastoAnual.funcion_nombre.label('desc'),
        )
        .where(and_(*filters))
        .distinct()
        .order_by(GastoAnual.funcion_nombre)
    )
    return [{'cod': '', 'desc': 'Todos'}] + _rows(db.session.execute(stmt))


@cache.memoize(timeout=300)
def get_ppto(anio: str, ubigeo: str, act: str, fun: str) -> list[dict]:
    dept, prov, dist = _ubigeo_parts(ubigeo)
    filters = [GastoAnual.programa_ppto.isnot(None)]
    if anio:
        filters.append(GastoAnual.ano_eje == int(anio))
    if dept:
        filters.append(GastoAnual.departamento_ejecutora == dept)
    if prov:
        filters.append(GastoAnual.provincia_ejecutora == prov)
    if dist:
        filters.append(GastoAnual.distrito_ejecutora == dist)
    if act and act != '1':
        filters.append(GastoAnual.tipo_act_proy == act)
    if fun:
        filters.append(GastoAnual.funcion == fun)

    stmt = (
        select(
            GastoAnual.programa_ppto.label('cod'),
            GastoAnual.programa_ppto_nombre.label('desc'),
        )
        .where(and_(*filters))
        .distinct()
        .order_by(GastoAnual.programa_ppto)
    )
    return [{'cod': '', 'desc': 'Todos'}] + _rows(db.session.execute(stmt))


@cache.memoize(timeout=300)
def get_nom_py(anio: str, ubigeo: str, nom: str, cod: str) -> list[dict]:
    dept, prov, dist = _ubigeo_parts(ubigeo)
    filters = []
    if anio:
        filters.append(GastoAnual.ano_eje == int(anio))
    if dept:
        filters.append(GastoAnual.departamento_ejecutora == dept)
    if prov:
        filters.append(GastoAnual.provincia_ejecutora == prov)
    if dist:
        filters.append(GastoAnual.distrito_ejecutora == dist)
    if nom:
        filters.append(GastoAnual.producto_proyecto_nombre.ilike(f'%{nom}%'))
    if cod:
        filters.append(GastoAnual.producto_proyecto == cod)

    stmt = (
        select(
            GastoAnual.producto_proyecto.label('idproy'),
            GastoAnual.producto_proyecto_nombre.label('proyecto'),
            GastoAnual.funcion_nombre.label('funcionnombre'),
            GastoAnual.nivel_gobierno.label('tipo_gobierno'),
            GastoAnual.sector,
            GastoAnual.pliego,
            func.coalesce(func.sum(GastoAnual.monto_pia), 0).label('pia'),
            func.coalesce(func.sum(GastoAnual.monto_pim), 0).label('pim'),
            func.coalesce(func.sum(GastoAnual.monto_devengado), 0).label('devengado'),
            func.coalesce(func.sum(GastoAnual.monto_girado), 0).label('girado'),
            _avance(),
        )
        .where(and_(*filters) if filters else True)
        .group_by(
            GastoAnual.producto_proyecto,
            GastoAnual.producto_proyecto_nombre,
            GastoAnual.funcion_nombre,
            GastoAnual.nivel_gobierno,
            GastoAnual.sector,
            GastoAnual.pliego,
        )
        .order_by(GastoAnual.nivel_gobierno, GastoAnual.sector, GastoAnual.pliego)
    )
    return _add_id(_rows(db.session.execute(stmt)))


# ---------------------------------------------------------------------------
# Ubigeo: nombres de departamento/provincia/distrito desde el mismo modelo
# ---------------------------------------------------------------------------

@cache.memoize(timeout=3600)
def get_ubigeo(ubigeo: str) -> list[dict]:
    dept, prov, dist = _ubigeo_parts(ubigeo)
    filters = []
    if dept:
        filters.append(GastoAnual.departamento_ejecutora == dept)

    if len(ubigeo) > 4 and dist:
        filters += [
            GastoAnual.provincia_ejecutora == prov,
            GastoAnual.distrito_ejecutora == dist,
        ]
        stmt = (
            select(
                GastoAnual.departamento_ejecutora_nombre.label('nom_dpto'),
                GastoAnual.provincia_ejecutora_nombre.label('nom_prov'),
                GastoAnual.distrito_ejecutora_nombre.label('nom_dist'),
            )
            .where(and_(*filters))
            .limit(1)
        )
    elif len(ubigeo) > 2 and prov:
        filters.append(GastoAnual.provincia_ejecutora == prov)
        stmt = (
            select(
                GastoAnual.departamento_ejecutora_nombre.label('nom_dpto'),
                GastoAnual.provincia_ejecutora_nombre.label('nom_prov'),
            )
            .where(and_(*filters))
            .limit(1)
        )
    else:
        stmt = (
            select(
                GastoAnual.departamento_ejecutora_nombre.label('nom_dpto'),
            )
            .where(and_(*filters) if filters else True)
            .limit(1)
        )

    return _rows(db.session.execute(stmt))


# ---------------------------------------------------------------------------
# Fecha de última actualización
# ---------------------------------------------------------------------------

@cache.memoize(timeout=3600)
def get_fecha() -> list[dict]:
    """Obtiene el año máximo disponible en gasto_anual como fecha referencial."""
    stmt = select(
        cast(func.max(GastoAnual.ano_eje), SAString).label('fec')
    )
    result = db.session.execute(stmt).fetchone()
    return [{'fec': result.fec if result and result.fec else ''}]


# ---------------------------------------------------------------------------
# Gráficos históricos (Highcharts)
# ---------------------------------------------------------------------------

@cache.memoize(timeout=1800)
def get_grafico(tipo: str, ubigeo: str) -> dict:
    dept, prov, dist = _ubigeo_parts(ubigeo)
    geo = []
    if dept:
        geo.append(GastoAnual.departamento_ejecutora == dept)
    if prov:
        geo.append(GastoAnual.provincia_ejecutora == prov)
    if dist:
        geo.append(GastoAnual.distrito_ejecutora == dist)

    base = [GastoAnual.ano_eje >= 2012] + geo

    ano_col = cast(GastoAnual.ano_eje, SAString).label('ano_eje')
    pim_col = func.sum(GastoAnual.monto_pim).label('sum')
    dev_col = func.round(func.sum(GastoAnual.monto_devengado)).label('dev')
    tip_col = GastoAnual.tipo_act_proy.label('tip_act_proy')

    if tipo == 'sector':
        stmt = (
            select(ano_col, GastoAnual.sector_nombre.label('name'), tip_col, pim_col, dev_col)
            .where(and_(*base))
            .group_by(GastoAnual.ano_eje, GastoAnual.sector_nombre, GastoAnual.tipo_act_proy)
        )
    elif tipo == 'funcion':
        stmt = (
            select(ano_col, GastoAnual.nivel_gobierno.label('tipo_gobierno'),
                   GastoAnual.funcion_nombre.label('name'), tip_col, pim_col, dev_col)
            .where(and_(*base))
            .group_by(GastoAnual.ano_eje, GastoAnual.nivel_gobierno,
                      GastoAnual.funcion_nombre, GastoAnual.tipo_act_proy)
        )
    elif tipo == 'cat_pre':
        stmt = (
            select(ano_col, GastoAnual.nivel_gobierno.label('tipo_gobierno'),
                   GastoAnual.programa_ppto_nombre.label('name'), tip_col, pim_col, dev_col)
            .where(and_(*base))
            .group_by(GastoAnual.ano_eje, GastoAnual.nivel_gobierno,
                      GastoAnual.programa_ppto_nombre, GastoAnual.tipo_act_proy)
        )
    else:
        return {}

    rows = _rows(db.session.execute(stmt))
    return _build_grafico_series(rows, tipo)


@cache.memoize(timeout=1800)
def get_grafico_violencia(ubigeo: str) -> dict:
    dept, prov, dist = _ubigeo_parts(ubigeo)
    filters = [GastoAnual.ano_eje >= 2012, GastoAnual.programa_ppto == '0080']
    if dept:
        filters.append(GastoAnual.departamento_ejecutora == dept)
    if prov:
        filters.append(GastoAnual.provincia_ejecutora == prov)
    if dist:
        filters.append(GastoAnual.distrito_ejecutora == dist)

    stmt = (
        select(
            cast(GastoAnual.ano_eje, SAString).label('ano_eje'),
            GastoAnual.nivel_gobierno.label('tipo_gobierno'),
            GastoAnual.programa_ppto_nombre.label('name'),
            GastoAnual.tipo_act_proy.label('tip_act_proy'),
            func.sum(GastoAnual.monto_pim).label('sum'),
            func.round(func.coalesce(func.sum(GastoAnual.monto_devengado), 0)).label('dev'),
        )
        .where(and_(*filters))
        .group_by(GastoAnual.ano_eje, GastoAnual.nivel_gobierno,
                  GastoAnual.programa_ppto_nombre, GastoAnual.tipo_act_proy)
    )
    rows = _rows(db.session.execute(stmt))
    return _build_violencia_series(rows)


# ---------------------------------------------------------------------------
# Reporte municipal (gobierno local) — raw SQL por joins a tablas geo
# ---------------------------------------------------------------------------

@cache.memoize(timeout=300)
def get_reporte_muni(tip: str, ubigeo: str) -> list[dict]:
    tip_filter = '' if tip == '1' else f"AND pimp.rubro = '{tip}'"
    cod_prov = ubigeo[:4]
    q = text(f"""
        SELECT ROW_NUMBER() OVER (ORDER BY cod_dist) AS id,
               cod_dist, nom_dist, nom_prov, nom_dpto,
               secejec, nombre,
               COALESCE(SUM(a), 0) a, COALESCE(SUM(p), 0) p, COALESCE(SUM(t), 0) t
        FROM (
            SELECT b.cod_dist, b.nom_dist, b.nom_prov, b.nom_dpto,
                   u.ubigeo, e.secejec, e.nombre,
                   pima.monto_pim AS a, pimp.monto_pim AS p, pimt.monto_pim AS t
            FROM mef_ejecutora_ubigeo u
            INNER JOIN mef_ejecutoraxanio e ON u.secejec = e.secejec AND anioeje = 2020
            INNER JOIN peru_distritos b     ON b.cod_dist = u.ubigeo AND b.cod_prov = :cod_prov
            LEFT JOIN (SELECT sec_ejec, SUM(monto_pim) monto_pim
                       FROM ide.gasto_anual WHERE tipo_act_proy = '2' {tip_filter}
                         AND nivel_gobierno = 'M' AND ano_eje = 2020 GROUP BY sec_ejec) pimp
                   ON pimp.sec_ejec = e.secejec
            LEFT JOIN (SELECT sec_ejec, SUM(monto_pim) monto_pim
                       FROM ide.gasto_anual WHERE tipo_act_proy = '3' {tip_filter}
                         AND nivel_gobierno = 'M' AND ano_eje = 2020 GROUP BY sec_ejec) pima
                   ON pima.sec_ejec = e.secejec
            LEFT JOIN (SELECT sec_ejec, SUM(monto_pim) monto_pim
                       FROM ide.gasto_anual WHERE nivel_gobierno = 'M' {tip_filter}
                         AND ano_eje = 2020 GROUP BY sec_ejec) pimt
                   ON pimt.sec_ejec = e.secejec
        ) t3
        GROUP BY cod_dist, nom_dist, nom_prov, nom_dpto, secejec, nombre
    """)
    return _rows(db.session.execute(q, {'cod_prov': cod_prov}))


# ---------------------------------------------------------------------------
# API externa MEF (sin cambios)
# ---------------------------------------------------------------------------

@cache.memoize(timeout=600)
def get_pip_general(codigo: str) -> dict:
    from flask import current_app
    url_dev = current_app.config['MEF_DEV_URL']
    url_det = current_app.config['MEF_DET_URL']

    try:
        historico_mef = requests.post(url_dev, data={'id': codigo, 'tipo': 'DEV2'}, timeout=10).json()
        mef_ssi       = requests.post(url_det, data={'id': codigo, 'tipo': 'SIAF'}, timeout=10).json()
    except Exception:
        return {'general': [{'codigounico': 0, 'monto_dev_acumulado': 0,
                             'monto_inversion_actual': 0, 'monto_viable': 0}], 'detalle': []}

    detalle: Any = []
    if historico_mef:
        df = pd.DataFrame(historico_mef)
        anios = list(df['NUM_ANIO'].unique())
        l_pim = [float(df.loc[df['NUM_ANIO'] == a, 'MTO_PIM'].values[0])   for a in anios]
        l_dev = [float(df.loc[df['NUM_ANIO'] == a, 'MTO_DEVEN'].values[0]) for a in anios]
        detalle = {
            'categories': anios,
            'series': [
                {'name': 'PIM',       'data': l_pim, 'color': '#002060'},
                {'name': 'DEVENGADO', 'data': l_dev, 'color': '#c00000'},
            ],
        }

    general = [{'codigounico': 0, 'monto_dev_acumulado': 0,
                'monto_inversion_actual': 0, 'monto_viable': 0}]
    if mef_ssi:
        g = mef_ssi[0]
        general = [{
            'codigounico':            g.get('CODIGO_UNICO', 0),
            'monto_dev_acumulado':    g.get('DEV_ACUMULADO', 0),
            'monto_inversion_actual': g.get('COSTO_ACTUALIZADO', 0),
            'monto_viable':           g.get('MTO_VIABLE', 0),
        }]

    return {'general': general, 'detalle': detalle}


# ---------------------------------------------------------------------------
# Builders de series Highcharts
# ---------------------------------------------------------------------------

_ANOS     = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
_ANOS_DF  = pd.DataFrame({'ano_eje': _ANOS})
_GOB_LABEL = {'E': 'Gobierno Nacional', 'R': 'Gobierno Regional', 'M': 'Gobierno Local'}
_GOB_COLOR = {'E': '#9b59b6',           'R': '#6F1E51',           'M': '#ED4C67'}


def _make_series(subset: pd.DataFrame, name_col: str) -> list[dict]:
    names = list(subset[name_col].unique())
    series = []
    for i, name in enumerate(names):
        df_n    = subset.loc[subset[name_col] == name]
        grouped = df_n.groupby([name_col, 'ano_eje']).sum(numeric_only=True)
        merged  = pd.merge(_ANOS_DF, grouped.reset_index(), how='left', on='ano_eje').fillna(0)
        entry: dict = {'name': name, 'data': merged['sum'].tolist(), 'dev': merged['dev'].tolist()}
        if i > 4:
            entry['visible'] = False
        series.append(entry)
    return series


def _build_grafico_series(rows: list[dict], tipo: str) -> dict:
    if not rows:
        return {'act': {'total': []}, 'proy': {'total': []}, 'tot': {'total': []}}

    data = pd.DataFrame(rows)

    list_t = _make_series(data, 'name')
    list_p = _make_series(data.loc[data['tip_act_proy'] == '2'], 'name')
    list_a = _make_series(data.loc[data['tip_act_proy'] == '3'], 'name')

    if tipo == 'sector':
        return {'act': {'total': list_a}, 'proy': {'total': list_p}, 'tot': {'total': list_t}}

    # funcion / cat_pre: desglose por nivel de gobierno
    result: dict = {k: {} for k in ('act', 'proy', 'tot')}
    gob_key = {'E': 'nacional', 'R': 'regional', 'M': 'local'}

    for gob, key in gob_key.items():
        for tipo_key, tip_val in [('tot', None), ('proy', '2'), ('act', '3')]:
            sub = (data.loc[data['tipo_gobierno'] == gob] if tip_val is None
                   else data.loc[(data['tip_act_proy'] == tip_val) & (data['tipo_gobierno'] == gob)])
            result[tipo_key][key] = _make_series(sub, 'name')

    result['tot']['total']  = list_t
    result['proy']['total'] = list_p
    result['act']['total']  = list_a
    return result


def _build_violencia_series(rows: list[dict]) -> dict:
    if not rows:
        return {'act': {'total': []}, 'proy': {'total': []}, 'tot': {'total': []}}

    data  = pd.DataFrame(rows)
    lists = {'tot': [], 'proy': [], 'act': []}

    for gob in ('E', 'R', 'M'):
        for tipo_key, tip_val in [('tot', None), ('proy', '2'), ('act', '3')]:
            sub = (data.loc[data['tipo_gobierno'] == gob] if tip_val is None
                   else data.loc[(data['tip_act_proy'] == tip_val) & (data['tipo_gobierno'] == gob)])
            sub = sub.sort_values('ano_eje')
            grouped = sub.groupby(['tipo_gobierno', 'ano_eje']).sum(numeric_only=True)
            merged  = pd.merge(_ANOS_DF, grouped.reset_index(), how='left', on='ano_eje').fillna(0)
            lists[tipo_key].append({
                'name':  _GOB_LABEL[gob],
                'data':  merged['sum'].tolist(),
                'dev':   merged['dev'].tolist(),
                'color': _GOB_COLOR[gob],
            })

    return {k: {'total': v} for k, v in lists.items()}
