# models/personagem.py
from dataclasses import dataclass
from typing import Optional
import sqlite3

@dataclass
class Personagem:
    id: int = 1
    nome: str = "Korga"
    classe: str = "Bárbaro"
    nivel: int = 1
    ca: int = 10
    hp_max: int = 10
    hp_atual: int = 10
    forca: int = 10
    destreza: int = 10
    constituicao: int = 10
    inteligencia: int = 10
    sabedoria: int = 10
    carisma: int = 10

    @staticmethod
    def carregar(conn: sqlite3.Connection, id: int = 1) -> "Personagem":
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, classe, nivel, ca, hp_max, hp_atual,
                   forca, destreza, constituicao, inteligencia, sabedoria, carisma
            FROM personagem
            WHERE id = ?
        """, (id,))
        row = cur.fetchone()
        if row:
            return Personagem(
                id=row[0], nome=row[1], classe=row[2], nivel=row[3], ca=row[4],
                hp_max=row[5], hp_atual=row[6],
                forca=row[7], destreza=row[8], constituicao=row[9],
                inteligencia=row[10], sabedoria=row[11], carisma=row[12]
            )
        # Se não existir, retorna um default (não grava ainda)
        return Personagem(id=id)

    def salvar(self, conn: sqlite3.Connection):
        cur = conn.cursor()
        # upsert simples: tenta update; se não atualizar, faz insert
        cur.execute("""
            UPDATE personagem
            SET nome=?, classe=?, nivel=?, ca=?, hp_max=?, hp_atual=?,
                forca=?, destreza=?, constituicao=?, inteligencia=?, sabedoria=?, carisma=?
            WHERE id=?
        """, (self.nome, self.classe, self.nivel, self.ca, self.hp_max, self.hp_atual,
              self.forca, self.destreza, self.constituicao,
              self.inteligencia, self.sabedoria, self.carisma, self.id))
        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO personagem
                (id, nome, classe, nivel, ca, hp_max, hp_atual,
                 forca, destreza, constituicao, inteligencia, sabedoria, carisma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.id, self.nome, self.classe, self.nivel, self.ca, self.hp_max, self.hp_atual,
                  self.forca, self.destreza, self.constituicao,
                  self.inteligencia, self.sabedoria, self.carisma))
        conn.commit()
