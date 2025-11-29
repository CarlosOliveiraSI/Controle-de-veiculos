import sqlite3

NOME_BANCO = "controle_veiculos.db"

def conectar():
    return sqlite3.connect(NOME_BANCO)

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    # Tabela de veículos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            tipo_veiculo TEXT NOT NULL,   -- carro ou moto
            tipo_uso TEXT NOT NULL,       -- particular ou oficial
            marcado INTEGER DEFAULT 0,    -- 0 = normal, 1 = não autorizado / com ocorrência
            observacao TEXT
        );
    """)

    # Tabela de acessos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_veiculo INTEGER NOT NULL,
            data_hora_entrada TEXT NOT NULL,
            data_hora_saida TEXT,
            alerta TEXT,
            FOREIGN KEY (id_veiculo) REFERENCES veiculos(id)
        );
    """)

    conn.commit()
    conn.close()

# ---------- Funções de veículos ----------

def inserir_veiculo(placa, tipo_veiculo, tipo_uso, marcado=0, observacao=""):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO veiculos (placa, tipo_veiculo, tipo_uso, marcado, observacao)
        VALUES (?, ?, ?, ?, ?)
    """, (placa.upper(), tipo_veiculo, tipo_uso, marcado, observacao))
    conn.commit()
    conn.close()

def buscar_veiculo_por_placa(placa):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, placa, tipo_veiculo, tipo_uso, marcado, observacao
        FROM veiculos
        WHERE placa = ?
    """, (placa.upper(),))
    dado = cur.fetchone()
    conn.close()
    return dado

def listar_todos_veiculos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, placa, tipo_veiculo, tipo_uso, marcado FROM veiculos")
    dados = cur.fetchall()
    conn.close()
    return dados

def atualizar_marcacao(placa, marcado, observacao=""):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE veiculos
        SET marcado = ?, observacao = ?
        WHERE placa = ?
    """, (int(marcado), observacao, placa.upper()))
    conn.commit()
    conn.close()

# ---------- Funções de acessos ----------

def registrar_entrada_bd(id_veiculo, data_hora, alerta=None):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO acessos (id_veiculo, data_hora_entrada, alerta)
        VALUES (?, ?, ?)
    """, (id_veiculo, data_hora, alerta))
    conn.commit()
    conn.close()

def registrar_saida_bd(id_veiculo, data_hora_saida, alerta_extra=None):
    """
    Fecha o último acesso em aberto daquele veículo.
    """
    conn = conectar()
    cur = conn.cursor()

    # Busca o último acesso sem saída
    cur.execute("""
        SELECT id, alerta FROM acessos
        WHERE id_veiculo = ? AND data_hora_saida IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (id_veiculo,))
    linha = cur.fetchone()

    if linha is None:
        conn.close()
        return False  # não tinha entrada aberta

    id_acesso, alerta_antigo = linha

    # Junta o alerta antigo com o novo (se tiver)
    if alerta_antigo is None:
        alerta_final = alerta_extra
    elif alerta_extra:
        alerta_final = alerta_antigo + " | " + alerta_extra
    else:
        alerta_final = alerta_antigo

    cur.execute("""
        UPDATE acessos
        SET data_hora_saida = ?, alerta = ?
        WHERE id = ?
    """, (data_hora_saida, alerta_final, id_acesso))

    conn.commit()
    conn.close()
    return True

def listar_acessos_por_placa(placa):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, v.placa, a.data_hora_entrada, a.data_hora_saida, a.alerta
        FROM acessos a
        JOIN veiculos v ON a.id_veiculo = v.id
        WHERE v.placa = ?
        ORDER BY a.id DESC
    """, (placa.upper(),))
    dados = cur.fetchall()
    conn.close()
    return dados

def listar_veiculos_marcados():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, placa, tipo_veiculo, tipo_uso, observacao
        FROM veiculos
        WHERE marcado = 1
    """)
    dados = cur.fetchall()
    conn.close()
    return dados

def listar_veiculos_dentro():
    """
    Lista veículos que têm entrada sem saída.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.placa, v.tipo_veiculo, v.tipo_uso, a.data_hora_entrada
        FROM acessos a
        JOIN veiculos v ON a.id_veiculo = v.id
        WHERE a.data_hora_saida IS NULL
    """)
    dados = cur.fetchall()
    conn.close()
    return dados
