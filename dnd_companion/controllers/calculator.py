# controllers/calculator.py
def modificador(atributo: int) -> int:
    """Retorna o modificador baseado em um valor de atributo."""
    return (atributo - 10) // 2

def calcular_bonus_pericia(pericia, personagem, prof_bonus=3):
    """
    Calcula o bônus total de uma perícia com base no atributo e proficiência.
    """
    atributo_valor = getattr(personagem, atributo_nome_para_campo(pericia.atributo_base).lower())
    base = modificador(atributo_valor)
    total = base + (prof_bonus if pericia.proficiente else 0)
    return total

def atributo_nome_para_campo(abrev: str):
    mapa = {
        "FOR": "forca",
        "DES": "destreza",
        "CON": "constituicao",
        "INT": "inteligencia",
        "SAB": "sabedoria",
        "CAR": "carisma"
    }
    return mapa.get(abrev.upper(), "")
