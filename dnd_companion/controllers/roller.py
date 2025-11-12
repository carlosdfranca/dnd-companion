# controllers/roller.py
import random
import re

class RollResult:
    def __init__(self, total, detalhes, valores, critico=False):
        self.total = total
        self.detalhes = detalhes
        self.valores = valores
        self.critico = critico

    def __str__(self):
        return f"{self.detalhes} = {self.total}"

def modificador(atributo: int) -> int:
    return (atributo - 10) // 2

def roll(expression: str, context: dict, manual_value: int | None = None,
         advantage: str = "normal", bonus_ataque: int = 0, bonus_dano: int = 0) -> RollResult:
    """
    Rola expressões tipo 'd20 + FOR + PROF' ou '1d12 + FOR'.
    Regra: se tiver d20 (maiúsculo ou minúsculo) -> aplica bônus de ATAQUE;
    senão -> aplica bônus de DANO.
    """
    expr_clean = expression.replace(" ", "")
    expr_lower = expr_clean.lower()
    tokens = re.findall(r"(\d*d\d+|[A-Z]+|\+?-?\d+)", expr_clean)

    is_attack = "d20" in expr_lower  # agora é case-insensitive
    total = 0
    detalhes = []
    valores = []
    critico = False

    for token in tokens:
        if "d" in token.lower():
            qtd_s, faces_s = token.lower().split("d")
            qtd = int(qtd_s) if qtd_s else 1
            faces = int(faces_s)

            if faces == 20 and qtd == 1 and advantage in ["advantage", "disadvantage"]:
                r1, r2 = (random.randint(1, 20), random.randint(1, 20)) if manual_value is None else (manual_value, manual_value)
                escolhido = max(r1, r2) if advantage == "advantage" else min(r1, r2)
                detalhes.append(f"d20({r1},{r2}) → {advantage} → {escolhido}")
                valores.append(("d20", [r1, r2]))
                total += escolhido
                if escolhido == 20:
                    critico = True
            else:
                rolagens = [random.randint(1, faces) for _ in range(qtd)] if manual_value is None else [manual_value]
                soma = sum(rolagens)
                detalhes.append(f"{token}({','.join(map(str, rolagens))})")
                valores.append((token, rolagens))
                total += soma
                if faces == 20 and any(v == 20 for v in rolagens):
                    critico = True

        elif token in context:
            valor = context[token]
            detalhes.append(f"{token}({valor:+d})")
            total += valor
        else:
            try:
                num = int(token)
                total += num
                detalhes.append(f"{num:+d}")
            except ValueError:
                pass

    # aplica bônus do item conforme tipo
    if is_attack and bonus_ataque:
        total += bonus_ataque
        detalhes.append(f"Item(+{bonus_ataque} ATAQUE)")
    elif not is_attack and bonus_dano:
        total += bonus_dano
        detalhes.append(f"Item(+{bonus_dano} DANO)")

    return RollResult(total, " + ".join(detalhes), valores, critico)
