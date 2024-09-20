from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Credor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    contato = db.Column(db.String(255))

class ContaPagar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credor_id = db.Column(db.ForeignKey('credor.id'))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default ='a pagar')
    credor = db.relationship('Credor', back_populates='contas')

Credor.contas = db.relationship('ContaPagar', order_by=ContaPagar.id, back_populates='credor')    