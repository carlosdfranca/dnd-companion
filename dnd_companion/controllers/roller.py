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

def roll(expression: str, context: dict, manual_value: int | None = None, advantage: str = "normal") -> RollResult:
    """
    Interpreta e executa uma expressão de rolagem (ex: '1d20 + FOR + PROF + 2')
    """
    tokens = re.findall(r"(\d*d\d+|[A-Z]+|\+?-?\d+)", expression.replace(" ", ""))
    total = 0
    detalhes = []
    valores = []
    critico = False

    for token in tokens:
        if "d" in token:  # rolagem de dado
            qtd, faces = token.split("d")
            qtd = int(qtd) if qtd else 1
            faces = int(faces)

            # vantagem/desvantagem só vale para d20 único
            if faces == 20 and qtd == 1 and advantage in ["advantage", "disadvantage"]:
                r1, r2 = (random.randint(1, 20), random.randint(1, 20)) if manual_value is None else (manual_value, manual_value)
                escolhido = max(r1, r2) if advantage == "advantage" else min(r1, r2)
                detalhes.append(f"d20({r1},{r2}) → {advantage} → usou {escolhido}")
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
                pass  # ignora tokens inválidos

    return RollResult(total, " + ".join(detalhes), valores, critico)
