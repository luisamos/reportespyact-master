from markupsafe import Markup

ROJO    = '#FF2424'
AMARILLO = '#FFE527'
VERDE   = '#4EF22C'

P_AMARILLO = 50
P_VERDE    = 80


class FuncionesPY:

    def barra(self, value) -> Markup:
        try:
            v = round(float(value), 2)
        except (TypeError, ValueError):
            v = 0.0

        if v < P_AMARILLO:
            color = ROJO
        elif v < P_VERDE:
            color = AMARILLO
        else:
            color = VERDE

        html = (
            f'{v}'
            f'<br>'
            f'<div style="width:50px;min-height:10px;background-color:#fff;border:1px solid black">'
            f'<div style="width:{v}%;min-height:10px;background-color:{color};border:1px solid {color}">'
            f'</div></div>'
        )
        return Markup(html)

    def formatMoneda(self, amount) -> str:
        try:
            return '{:20,.2f}'.format(float(amount))
        except (TypeError, ValueError):
            return '0.00'
