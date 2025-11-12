# models/pericia.py
import sqlite3
from dataclasses import dataclass

@dataclass
class Pericia:
    id: int
    personagem_id: int
    nome: str
    atributo_base: str
    proficiente: bool = False

    @staticmethod
    def listar(conn: sqlite3.Connection, personagem_id: int = 1):
        cur = conn.cursor()
        cur.execute("SELECT id, personagem_id, nome, atributo_base, proficiente FROM pericia WHERE personagem_id=?", (personagem_id,))
        pericias = [Pericia(*row) for row in cur.fetchall()]
        return pericias

    @staticmethod
    def alternar_proficiencia(conn: sqlite3.Connection, pericia_id: int):
        cur = conn.cursor()
        cur.execute("UPDATE pericia SET proficiente = CASE WHEN proficiente = 1 THEN 0 ELSE 1 END WHERE id=?", (pericia_id,))
        conn.commit()
