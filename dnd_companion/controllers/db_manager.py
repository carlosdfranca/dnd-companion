# controllers/db_manager.py
import os
import sqlite3

DB_PATH = os.path.join("data", "dnd_companion.db")

def inicializar_banco():
    """Cria o banco de dados se não existir e garante as tabelas desta etapa."""
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Meta-info (reservado para uso futuro)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meta_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            valor TEXT
        )
    """)

    # ===============================
    # Tabela de PERSONAGEM (ETAPA 2)
    # ===============================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personagem (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            classe TEXT,
            nivel INTEGER,
            ca INTEGER,
            hp_max INTEGER,
            hp_atual INTEGER,
            forca INTEGER,
            destreza INTEGER,
            constituicao INTEGER,
            inteligencia INTEGER,
            sabedoria INTEGER,
            carisma INTEGER
        )
    """)

    # ===============================
    # Tabela de PERICIAS (ETAPA 3)
    # ===============================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pericia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personagem_id INTEGER,
            nome TEXT,
            atributo_base TEXT,
            proficiente INTEGER DEFAULT 0
        )
    """)

    # Se ainda não existirem, insere a lista padrão
    cursor.execute("SELECT COUNT(*) FROM pericia")
    if cursor.fetchone()[0] == 0:
        lista_pericias = [
            ("Atletismo", "FOR"),
            ("Acrobacia", "DES"),
            ("Furtividade", "DES"),
            ("Prestidigitação", "DES"),
            ("Arcanismo", "INT"),
            ("História", "INT"),
            ("Investigação", "INT"),
            ("Natureza", "INT"),
            ("Religião", "INT"),
            ("Intuição", "SAB"),
            ("Medicina", "SAB"),
            ("Percepção", "SAB"),
            ("Sobrevivência", "SAB"),
            ("Manejo de Animais", "SAB"),
            ("Atuação", "CAR"),
            ("Enganação", "CAR"),
            ("Intimidação", "CAR"),
            ("Persuasão", "CAR")
        ]
        for nome, atributo in lista_pericias:
            cursor.execute("INSERT INTO pericia (personagem_id, nome, atributo_base) VALUES (1, ?, ?)", (nome, atributo))

    # Garante uma linha default (id=1) se ainda não existir
    cursor.execute("SELECT COUNT(*) FROM personagem WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO personagem
            (id, nome, classe, nivel, ca, hp_max, hp_atual,
             forca, destreza, constituicao, inteligencia, sabedoria, carisma)
            VALUES
            (1, 'Korga', 'Bárbaro', 6, 16, 85, 85,
             20, 14, 20, 10, 12, 10)
        """)

    conn.commit()
    conn.close()

def conectar():
    """Retorna uma conexão ativa com o banco."""
    return sqlite3.connect(DB_PATH)
