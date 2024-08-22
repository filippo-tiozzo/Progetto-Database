# Importazione moduli
from flask import current_app, flash
from flask_login import login_user, UserMixin
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from . import db

# Definizione classe (tabella) Utenti
class Utenti(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    ruolo = db.Column(db.String(10), index=True)

# Definizione classe (tabella) Acquirente
class Acquirente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), index=True)
    user = db.relationship('Utenti', backref='acquirenti')

# Definizione classe (tabella) Venditore
class Venditore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), index=True)
    user = db.relationship('Utenti', backref='venditori')
    prodotti = db.relationship("Prodotto", back_populates="venditore")

# Definizione classe (tabella) Prodotto
class Prodotto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descrizione = db.Column(db.String, nullable=False)
    prezzo = db.Column(db.Float, nullable=False)
    quantita = db.Column(db.Integer, nullable=False)
    data_inserimento = db.Column(db.DateTime, default=datetime.now)
    venditore_id = db.Column(db.Integer, db.ForeignKey('venditore.id'), index=True)
    venditore = db.relationship("Venditore", back_populates="prodotti")
    def media_voti(self):
        recensioni = Recensione.query.filter_by(prodotto_id=self.id).all()
        if recensioni:
            return sum(r.voto for r in recensioni) / len(recensioni)
        return None
    
class Carrello(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    prodotti = db.relationship('CarrelloProdotto', back_populates='carrello')

class CarrelloProdotto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrello_id = db.Column(db.Integer, db.ForeignKey('carrello.id'), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotto.id'), nullable=False)
    quantita = db.Column(db.Integer, nullable=False)
    carrello = db.relationship('Carrello', back_populates='prodotti')
    prodotto = db.relationship('Prodotto')

class Acquisto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotto.id'), nullable=False)
    quantita = db.Column(db.Integer, nullable=False)
    data_acquisto = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user = db.relationship('Utenti', backref='acquisti')
    prodotto = db.relationship('Prodotto', backref='acquisti')
    def ha_recensione(self):
        return Recensione.query.filter_by(prodotto_id=self.prodotto_id, user_id=self.user_id).first() is not None

class Ordine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    data_ordine = db.Column(db.DateTime, default=datetime.now)
    prodotti = db.relationship('OrdineProdotto', backref='ordine', lazy=True)
    stato = db.Column(db.String(20), nullable=False, default='acquistato')

class OrdineProdotto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordine_id = db.Column(db.Integer, db.ForeignKey('ordine.id'), nullable=False)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotto.id'), nullable=False)
    quantita = db.Column(db.Integer, nullable=False)
    spedito = db.Column(db.Boolean, default=False) 
    prodotto = db.relationship('Prodotto')

class Recensione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prodotto_id = db.Column(db.Integer, db.ForeignKey('prodotto.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    voto = db.Column(db.Integer, nullable=False)
    data_recensione = db.Column(db.DateTime, default=datetime.now, nullable=False)

    prodotto = db.relationship('Prodotto', backref='recensioni')
    user = db.relationship('Utenti', backref='recensioni')
    
# Creazione engine e sessione collegati al database 'amministratore'
def get_autho_session():
    db_autho_uri = current_app.config['SQLALCHEMY_BINDS']['amministratore']
    db_autho = create_engine(db_autho_uri)
    Session = sessionmaker(bind=db_autho)
    return Session()

# Creazione venditore
def crea_venditore(nome, cognome, email, password):
    try:
        session = get_autho_session()
        user = Utenti(username=email, password=password, ruolo='Venditore')
        venditore = Venditore(nome=nome, cognome=cognome, user=user)
        session.add(user)
        session.add(venditore)
        session.commit()     # Salva le modifiche nel database
        return venditore.user
    except IntegrityError:
        session.rollback()   # In caso di errori la sessione viene annullata
    return None

# Creazione acquirente
def crea_acquirente(nome, cognome, email, password):
    try:
        session = get_autho_session()
        user = Utenti(username=email, password=password, ruolo='Acquirente')
        acquirente = Acquirente(nome=nome, cognome=cognome, user=user)
        session.add(user)
        session.add(acquirente)
        session.commit()     # Salva le modifiche nel database
        return acquirente.user
    except IntegrityError:
        session.rollback()   # In caso di errori la sessione viene annullata
    return None

# Definizione login utente
def login_utente(username, password):
    session = get_autho_session()
    user = session.query(Utenti).filter_by(username=username).first()   # Query per ottenere l'utente dallo username
    if user and check_password_hash(user.password, password):           # Verifica se l'utente esiste e la password è corretta
        login_user(user, remember=True)                                 # Esegue login e memorizza utente
        flash('Login completato', category='success')
        if user.ruolo == 'Venditore': 
            return 'venditore.home'                                     # Reindirizza venditore alla pagina dei venditori
        elif user.ruolo == 'Acquirente':
            return 'acquirente.home'                                    # Reindirizza acquirente alla pagina degli acquirenti
    else:
        flash('Mail o password non corretti', category='error')
    return None

# Definizione registrazione utente
def registrazione_utente(nome, cognome, email, password1, password2, ruolo):
    session = get_autho_session()
    user = session.query(Utenti).filter_by(username=email).first()   # Query per ottenere l'utente dallo username
    if user:                                                         # Verifica se l'utente è già presente nel database
        flash('Mail già utilizzata', category='error')
        return None
    elif len(email) < 4:
        flash('Mail troppo corta', category='error')
        return None
    elif password1 != password2:
        flash('Le password non sono uguali', category='error')
        return None
    elif len(password1) < 7:
        flash('La password deve essere di almeno 7 caratteri', category='error')
        return None
    else:
        if not user and ruolo == 'Venditore':
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            venditore = crea_venditore(nome, cognome, email, hashed_password)
            if venditore:
                login_user(venditore, remember=True)                 # Esegue login e memorizza venditore
                flash('Creato account (Venditore)', category='success')
                return 'venditore.home'
            else:
                flash('Errore nella creazione dell\'utente', category='error')
                return None
        elif not user and ruolo == 'Acquirente':
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            acquirente = crea_acquirente(nome, cognome, email, hashed_password)
            if acquirente:
                login_user(acquirente, remember=True)                # Esegue login e memorizza acquirente
                flash('Creato account (Acquirente)', category='success')
                return 'acquirente.home'
            else:
                flash('Errore nella creazione utente', category='error')
                return None
        else:
            flash('Errore nella registrazione utente', category='error')
            return None

# Definizone sessione venditore
def get_venditore_session():
    db_doc_uri = current_app.config['SQLALCHEMY_BINDS']['venditore']   # Ottiene URI di connessione
    db_doc = create_engine(db_doc_uri)                                 # Creazione engine collegato al database 'venditore' 
    Session = sessionmaker(bind=db_doc)                                # Creazione sessione collegata al database 'venditore'
    return Session()

# Definizione sessione acquirente
def get_acquirente_session():
    db_stu_uri = current_app.config['SQLALCHEMY_BINDS']['acquirente']   # Ottiene URI di connessione
    db_stu = create_engine(db_stu_uri)                                  # Creazione engine collegato al database 'acquirente'
    Session = sessionmaker(bind=db_stu)                                 # Creazione sessione collegata al database 'acquirente'
    return Session()
