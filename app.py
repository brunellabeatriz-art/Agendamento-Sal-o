from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE = 'database.db'

# Funções para conexão com o banco de dados
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Para retornar linhas como dicionários
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Rota principal - lista serviços
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM servicos")
    servicos = cursor.fetchall()
    return render_template('index.html', servicos=servicos)

# Rota para agendar um serviço
@app.route('/agendar/<int:servico_id>', methods=['GET', 'POST'])
def agendar(servico_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
    servico = cursor.fetchone()

    if servico is None:
        return "Serviço não encontrado", 404

    if request.method == 'POST':
        data = request.form['data']
        hora = request.form['hora']
        nome_cliente = request.form['nome_cliente']
        telefone_cliente = request.form.get('telefone_cliente', '') # Opcional

        # Validação simples para evitar agendamentos no passado
        agendamento_dt = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
        if agendamento_dt < datetime.now():
            return render_template('agendar.html', servico=servico, error="Não é possível agendar no passado.")

        # Validação simples para evitar conflitos de horário (apenas para o mesmo serviço)
        # Em um sistema real, você precisaria de lógica mais complexa para considerar a duração do serviço
        # e a disponibilidade do profissional.
        cursor.execute(
            "SELECT * FROM agendamentos WHERE servico_id = ? AND data = ? AND hora = ?",
            (servico_id, data, hora)
        )
        if cursor.fetchone():
            return render_template('agendar.html', servico=servico, error="Horário já agendado para este serviço.")

        cursor.execute(
            "INSERT INTO agendamentos (servico_id, data, hora, nome_cliente, telefone_cliente) VALUES (?, ?, ?, ?, ?)",
            (servico_id, data, hora, nome_cliente, telefone_cliente)
        )
        db.commit()
        return redirect(url_for('index')) # Redireciona para a página inicial após o agendamento

    return render_template('agendar.html', servico=servico)

# Rota para o profissional visualizar agendamentos
@app.route('/profissional')
def profissional():
    db = get_db()
    cursor = db.cursor()

    # Busca todos os agendamentos e os serviços relacionados
    cursor.execute("""
        SELECT
            a.id, a.data, a.hora, a.nome_cliente, a.telefone_cliente,
            s.nome AS nome_servico, s.duracao_minutos
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        ORDER BY a.data, a.hora
    """)
    agendamentos = cursor.fetchall()

    # Agrupar agendamentos por data para melhor visualização
    agendamentos_por_data = {}
    for ag in agendamentos:
        data_str = ag['data']
        if data_str not in agendamentos_por_data:
            agendamentos_por_data[data_str] = []
        agendamentos_por_data[data_str].append(ag)

    # Ordenar as datas para exibição
    datas_ordenadas = sorted(agendamentos_por_data.keys())

    return render_template('profissional.html', agendamentos_por_data=agendamentos_por_data, datas_ordenadas=datas_ordenadas)

if __name__ == '__main__':
    # Inicializa o banco de dados antes de rodar o app Flask
    from database import init_db
    with app.app_context():
        init_db()
    app.run(debug=True) # debug=True para desenvolvimento (recarrega automaticamente)