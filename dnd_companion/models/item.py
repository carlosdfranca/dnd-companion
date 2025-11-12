# models/item.py
from controllers.db_manager import conectar

class Item:
    def __init__(
        self,
        id=None,
        personagem_id=1,
        nome="",
        descricao="",
        bonus_atributo="",
        valor_bonus=0,
        bonus_ca=0,
        bonus_ataque=0,
        bonus_dano=0,
        efeito_especial="",
        equipado=False,
    ):
        self.id = id
        self.personagem_id = personagem_id
        self.nome = nome
        self.descricao = descricao
        self.bonus_atributo = bonus_atributo
        self.valor_bonus = valor_bonus
        self.bonus_ca = bonus_ca
        self.bonus_ataque = bonus_ataque
        self.bonus_dano = bonus_dano
        self.efeito_especial = efeito_especial
        self.equipado = bool(equipado)

    # ============================
    # 🔹 CRUD BÁSICO
    # ============================

    def salvar(self, conn=None):
        """Insere ou atualiza o item no banco."""
        fechar = False
        if conn is None:
            conn = conectar()
            fechar = True
        cursor = conn.cursor()

        if self.id is None:
            cursor.execute(
                """
                INSERT INTO item (
                    personagem_id, nome, descricao,
                    bonus_atributo, valor_bonus, bonus_ca,
                    bonus_ataque, bonus_dano, efeito_especial, equipado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.personagem_id,
                    self.nome,
                    self.descricao,
                    self.bonus_atributo,
                    self.valor_bonus,
                    self.bonus_ca,
                    self.bonus_ataque,
                    self.bonus_dano,
                    self.efeito_especial,
                    int(self.equipado),
                ),
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                """
                UPDATE item SET
                    personagem_id=?,
                    nome=?,
                    descricao=?,
                    bonus_atributo=?,
                    valor_bonus=?,
                    bonus_ca=?,
                    bonus_ataque=?,
                    bonus_dano=?,
                    efeito_especial=?,
                    equipado=?
                WHERE id=?
                """,
                (
                    self.personagem_id,
                    self.nome,
                    self.descricao,
                    self.bonus_atributo,
                    self.valor_bonus,
                    self.bonus_ca,
                    self.bonus_ataque,
                    self.bonus_dano,
                    self.efeito_especial,
                    int(self.equipado),
                    self.id,
                ),
            )

        conn.commit()
        if fechar:
            conn.close()

    def deletar(self, conn=None):
        fechar = False
        if conn is None:
            conn = conectar()
            fechar = True
        cursor = conn.cursor()
        cursor.execute("DELETE FROM item WHERE id=?", (self.id,))
        conn.commit()
        if fechar:
            conn.close()

    # ============================
    # 🔹 CONSULTAS
    # ============================

    @staticmethod
    def listar(conn=None):
        fechar = False
        if conn is None:
            conn = conectar()
            fechar = True
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, personagem_id, nome, descricao,
                   bonus_atributo, valor_bonus, bonus_ca,
                   bonus_ataque, bonus_dano, efeito_especial, equipado
            FROM item
            ORDER BY nome
            """
        )
        rows = cursor.fetchall()
        items = [
            Item(
                id=r[0],
                personagem_id=r[1],
                nome=r[2],
                descricao=r[3],
                bonus_atributo=r[4],
                valor_bonus=r[5],
                bonus_ca=r[6],
                bonus_ataque=r[7],
                bonus_dano=r[8],
                efeito_especial=r[9],
                equipado=bool(r[10]),
            )
            for r in rows
        ]
        if fechar:
            conn.close()
        return items

    @staticmethod
    def buscar_por_id(item_id, conn=None):
        fechar = False
        if conn is None:
            conn = conectar()
            fechar = True
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, personagem_id, nome, descricao,
                   bonus_atributo, valor_bonus, bonus_ca,
                   bonus_ataque, bonus_dano, efeito_especial, equipado
            FROM item
            WHERE id=?
            """,
            (item_id,),
        )
        row = cursor.fetchone()
        if fechar:
            conn.close()
        if row:
            return Item(
                id=row[0],
                personagem_id=row[1],
                nome=row[2],
                descricao=row[3],
                bonus_atributo=row[4],
                valor_bonus=row[5],
                bonus_ca=row[6],
                bonus_ataque=row[7],
                bonus_dano=row[8],
                efeito_especial=row[9],
                equipado=bool(row[10]),
            )
        return None
