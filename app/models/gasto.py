from sqlalchemy import Integer, Numeric, Text, PrimaryKeyConstraint
from ..extensions import db
from ..config import SCHEMA_IDE

PRIMARY_KEY_COLUMNS = (
    "ano_eje",
    "mes_eje",
    "sec_ejec",
    "sec_func",
    "meta",
    "fuente_financiamiento",
    "generica",
    "subgenerica",
    "subgenerica_det",
    "especifica",
    "especifica_det",
)


class GastoBase(db.Model):
    __abstract__ = True

    ano_eje = db.Column(Integer)
    mes_eje = db.Column(Integer)

    nivel_gobierno = db.Column(Text)
    nivel_gobierno_nombre = db.Column(Text)

    sector = db.Column(Text)
    sector_nombre = db.Column(Text)

    pliego = db.Column(Text)
    pliego_nombre = db.Column(Text)

    sec_ejec = db.Column(Text)
    ejecutora = db.Column(Text)
    ejecutora_nombre = db.Column(Text)

    departamento_ejecutora = db.Column(Text)
    departamento_ejecutora_nombre = db.Column(Text)
    provincia_ejecutora = db.Column(Text)
    provincia_ejecutora_nombre = db.Column(Text)
    distrito_ejecutora = db.Column(Text)
    distrito_ejecutora_nombre = db.Column(Text)

    sec_func = db.Column(Text)
    programa_ppto = db.Column(Text)
    programa_ppto_nombre = db.Column(Text)

    tipo_act_proy = db.Column(Text)
    tipo_act_proy_nombre = db.Column(Text)

    producto_proyecto = db.Column(Text)
    producto_proyecto_nombre = db.Column(Text)

    actividad_accion_obra = db.Column(Text)
    actividad_accion_obra_nombre = db.Column(Text)

    funcion = db.Column(Text)
    funcion_nombre = db.Column(Text)

    division_funcional = db.Column(Text)
    division_funcional_nombre = db.Column(Text)

    grupo_funcional = db.Column(Text)
    grupo_funcional_nombre = db.Column(Text)

    meta = db.Column(Text)
    finalidad = db.Column(Text)
    meta_nombre = db.Column(Text)

    departamento_meta = db.Column(Text)
    departamento_meta_nombre = db.Column(Text)

    fuente_financiamiento = db.Column(Text)
    fuente_financiamiento_nombre = db.Column(Text)

    rubro = db.Column(Text)
    rubro_nombre = db.Column(Text)

    tipo_recurso = db.Column(Text)
    tipo_recurso_nombre = db.Column(Text)

    categoria_gasto = db.Column(Text)
    categoria_gasto_nombre = db.Column(Text)

    tipo_transaccion = db.Column(Text)

    generica = db.Column(Text)
    generica_nombre = db.Column(Text)

    subgenerica = db.Column(Text)
    subgenerica_nombre = db.Column(Text)

    subgenerica_det = db.Column(Text)
    subgenerica_det_nombre = db.Column(Text)

    especifica = db.Column(Text)
    especifica_nombre = db.Column(Text)

    especifica_det = db.Column(Text)
    especifica_det_nombre = db.Column(Text)

    monto_pia = db.Column(Numeric(18, 2))
    monto_pim = db.Column(Numeric(18, 2))
    monto_certificado = db.Column(Numeric(18, 2))
    monto_comprometido_anual = db.Column(Numeric(18, 2))
    monto_comprometido = db.Column(Numeric(18, 2))
    monto_devengado = db.Column(Numeric(18, 2))
    monto_girado = db.Column(Numeric(18, 2))


class GastoDiario(GastoBase):
    __tablename__ = 'gasto_diario'
    __table_args__ = (
        PrimaryKeyConstraint(*PRIMARY_KEY_COLUMNS),
        {'schema': SCHEMA_IDE},
    )


class GastoAnual(GastoBase):
    __tablename__ = 'gasto_anual'
    __table_args__ = (
        PrimaryKeyConstraint(*PRIMARY_KEY_COLUMNS),
        {'schema': SCHEMA_IDE},
    )
