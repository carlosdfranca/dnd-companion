# models/item.py
import sqlite3
from dataclasses import dataclass

@dataclass
class Item:
    id: int
    personagem_id: int
    nome: str
    descricao: str
    bonus_atributo: str  # "FOR", "DES", "CON", "INT", "SAB", "CAR" ou ""
    valor_bonus: int
    bonus_ca: int
    equipado: bool
    bonus_ataque: int = 0
    bonus_dano: int = 0
    efeito_especial: str = ""

    # ===============================
    # 🧾 Listar todos os itens do personagem
    # ===============================
    @staticmethod
    def listar(conn: sqlite3.Connection, personagem_id=1):
        cur = conn.cursor()
        cur.execute("""
            SELECT id, personagem_id, nome, descricao, bonus_atributo, valor_bonus,
                   bonus_ca, equipado, bonus_ataque, bonus_dano, efeito_especial
            FROM item
            WHERE personagem_id=?
            ORDER BY id DESC
        """, (personagem_id,))
        items = []
        for row in cur.fetchall():
            items.append(Item(
                id=row[0],
                personagem_id=row[1],
                nome=row[2] or "",
                descricao=row[3] or "",
                bonus_atributo=(row[4] or "").upper(),
                valor_bonus=int(row[5] or 0),
                bonus_ca=int(row[6] or 0),
                equipado=bool(row[7]),
                bonus_ataque=int(row[8] or 0),
                bonus_dano=int(row[9] or 0),
                efeito_especial=row[10] or ""
            ))
        return items

    # ===============================
    # 🔍 Obter item específico
    # ===============================
    @staticmethod
    def obter(conn: sqlite3.Connection, item_id: int):
        cur = conn.cursor()
        cur.execute("""
            SELECT id, personagem_id, nome, descricao, bonus_atributo, valor_bonus,
                   bonus_ca, equipado, bonus_ataque, bonus_dano, efeito_especial
            FROM item WHERE id=?
        """, (item_id,))
        row = cur.fetchone()
        if not row:
            return None
        return Item(
            id=row[0],
            personagem_id=row[1],
            nome=row[2] or "",
            descricao=row[3] or "",
            bonus_atributo=(row[4] or "").upper(),
            valor_bonus=int(row[5] or 0),
            bonus_ca=int(row[6] or 0),
            equipado=bool(row[7]),
            bonus_ataque=int(row[8] or 0),
            bonus_dano=int(row[9] or 0),
            efeito_especial=row[10] or ""
        )

    # ===============================
    # 💾 Inserir novo item
    # ===============================
    def inserir(self, conn: sqlite3.Connection):
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO item (
                personagem_id, nome, descricao, bonus_atributo, valor_bonus,
                bonus_ca, equipado, bonus_ataque, bonus_dano, efeito_especial
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.personagem_id, self.nome, self.descricao, self.bonus_atributo,
            self.valor_bonus, self.bonus_ca, int(self.equipado),
            self.bonus_ataque, self.bonus_dano, self.efeito_especial
        ))
        conn.commit()
        self.id = cur.lastrowid
        return self.id

    # ===============================
    # 🔄 Atualizar item existente
    # ===============================
    def atualizar(self, conn: sqlite3.Connection):
        cur = conn.cursor()
        cur.execute("""
            UPDATE item
            SET nome=?, descricao=?, bonus_atributo=?, valor_bonus=?, bonus_ca=?,
                equipado=?, bonus_ataque=?, bonus_dano=?, efeito_especial=?
            WHERE id=?
        """, (
            self.nome, self.descricao, self.bonus_atributo, self.valor_bonus,
            self.bonus_ca, int(self.equipado), self.bonus_ataque,
            self.bonus_dano, self.efeito_especial, self.id
        ))
        conn.commit()

    # ===============================
    # ❌ Deletar item
    # ===============================
    @staticmethod
    def deletar(conn: sqlite3.Connection, item_id: int):
        cur = conn.cursor()
        cur.execute("DELETE FROM item WHERE id=?", (item_id,))
        conn.commit()

    # ===============================
    # ⚔️ Alternar equipado/desarmado
    # ===============================
    @staticmethod
    def alternar_equipado(conn: sqlite3.Connection, item_id: int):
        cur = conn.cursor()
        cur.execute("""
            UPDATE item
            SET equipado = CASE WHEN equipado = 1 THEN 0 ELSE 1 END
            WHERE id=?
        """, (item_id,))
        conn.commit()
