import sqlite3

DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Tabela de Serviços
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            duracao_minutos INTEGER NOT NULL
        )
    ''')

    # Tabela de Agendamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            nome_cliente TEXT NOT NULL,
            telefone_cliente TEXT,
            FOREIGN KEY (servico_id) REFERENCES servicos (id)
        )
    ''')

    # Inserir alguns serviços de exemplo se o banco estiver vazio
    cursor.execute("SELECT COUNT(*) FROM servicos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO servicos (nome, duracao_minutos) VALUES (?, ?)", ('Corte de Cabelo', 60))
        cursor.execute("INSERT INTO servicos (nome, duracao_minutos) VALUES (?, ?)", ('Manicure', 45))
        cursor.execute("INSERT INTO servicos (nome, duracao_minutos) VALUES (?, ?)", ('Pedicure', 60))
        cursor.execute("INSERT INTO servicos (nome, duracao_minutos) VALUES (?, ?)", ('Coloração', 120))
        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    print("Banco de dados inicializado com sucesso!")