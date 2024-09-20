from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from models import db, Credor, ContaPagar
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', show_menu=True)

@app.route('/credores', methods =['GET', 'POST'])
def handle_credores():
    if request.method == 'POST':
        # Verificar o tipo de conteúdo
        if request.is_json:
            data = request.json
            novo_credor = Credor(nome=data['nome'], cnpj=data['cnpj'], contato=data.get('contato', ''))
            db.session.add(novo_credor)
            db.session.commit()
            return jsonify({"message": "Credor criado com sucesso"}), 201
        else:
            # Dados do formulário HTML
            nome = request.form.get('nome')
            cnpj = request.form.get('cnpj')
            contato = request.form.get('contato', '')
            novo_credor = Credor(nome=nome, cnpj=cnpj, contato=contato)
            db.session.add(novo_credor)
            db.session.commit()
            return redirect(url_for('handle_credores'))
    else:
        credores = Credor.query.all()
        return render_template('credores.html', credores=credores, show_menu=False)
    
@app.route('/listar_credores')
def list_credores():
       credores = Credor.query.all()
       return render_template('listar_credores.html', credores=credores, show_menu=False)

@app.route('/excluir_credor/<int:id>', methods=['POST'])
def excluir_credor(id):
    credor = Credor.query.get_or_404(id)
    try:
        db.session.delete(credor)
        db.session.commit()
        flash('Credor excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir credor: {e}', 'danger')
    return redirect(url_for('routes.list_credores'))

    
@app.route('/contas-a-pagar', methods=['GET', 'POST'])
def handle_contas_a_pagar():
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.json
                credor_id = data['credor_id']
                valor = float(data['valor'])
                data_vencimento = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
                status = data.get('status', 'a pagar')
            else:
                credor_id = request.form.get('credor_id')
                valor = float(request.form.get('valor', 0))
                data_vencimento = datetime.strptime(request.form.get('data_vencimento'), '%Y-%m-%d').date()
                status = request.form.get('status', 'a pagar')

            # Verificar se o credor_id é válido
            credor = Credor.query.get(credor_id)
            if not credor:
                return jsonify({"error": "Credor não encontrado"}), 404

            nova_conta = ContaPagar(
                credor_id=credor_id,
                valor=valor,
                data_vencimento=data_vencimento,
                status=status
            )
            db.session.add(nova_conta)
            db.session.commit()
            
            if request.is_json:
                return jsonify({"message": "Conta a pagar criada com sucesso"}), 201
            else:
                return redirect(url_for('handle_contas_a_pagar'))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    else:
        # Filtrar pelo ID do credor, se fornecido
        credor_id = request.args.get('credor_id')
        status = request.args.get('status')
        
        query = ContaPagar.query
        if credor_id and status:
            contas = ContaPagar.query.filter_by(credor_id=credor_id, status=status).all()
        elif credor_id:
            contas = ContaPagar.query.filter_by(credor_id=credor_id).all()
        else:
            contas = ContaPagar.query.all()

        credores = Credor.query.all()
        return render_template('contas_a_pagar.html', contas=contas, credores=credores, show_menu=False)

@app.route('/filtro-contas', methods=['GET', 'POST'])
def filtrar_contas_por_credor_status():
    if request.method == 'POST':
        # Usar request.form.get() para capturar dados enviados por formulário no POST
        credor_id = request.form.get('credor_id')
        status = request.form.get('status')

        query = ContaPagar.query
        if credor_id and status:
            contas = query.filter_by(credor_id=credor_id, status=status).all()
        elif credor_id:
            contas = query.filter_by(credor_id=credor_id).all()
        else:
            contas = query.all()

        credores = Credor.query.all()

        return render_template('filtro_contas.html', contas=contas, credores=credores, show_menu=False)
 
    credores = Credor.query.all()
    return render_template('filtro_contas.html', contas=[], credores=credores, show_menu=False)

@app.route('/excluir_conta/<int:id>', methods=['POST'])
def excluir_conta(id):
    # Buscar a conta pelo ID
    conta = ContaPagar.query.get_or_404(id)

    try:
        # Remover a conta do banco de dados
        db.session.delete(conta)
        db.session.commit()
        flash('Conta excluída com sucesso!', 'success')
    except Exception as e:
        # Reverter a transação em caso de erro
        db.session.rollback()
        flash(f'Erro ao excluir conta: {e}', 'danger')

    # Redirecionar para a lista de contas ou outra página apropriada
    return redirect(url_for('filtrar_contas_por_credor_status'))
   

from datetime import datetime


if __name__ == '__main__':
    app.run(debug=True)

