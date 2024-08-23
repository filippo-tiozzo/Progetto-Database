# Importazione moduli
#import subprocess
from flask import Flask, g
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from psycopg2 import OperationalError, ProgrammingError

# Creazione istanze SQLAlchemy e applicazione Flask
db = SQLAlchemy()
def create_app(): 
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'odkwkwpplkwkw'   # Configurazione chiave di configurazione
    app.config['SQLALCHEMY_DATABASE_URI'] = (    # Configurazione connessione al database
        'postgresql://postgres:statua9L@localhost:5432/progetto'
    )

    app.config['SQLALCHEMY_BINDS'] = {           # Configurazione collegamenti
        'acquirente': 'postgresql://acquirente:password@localhost:5432/progetto',
        'venditore': 'postgresql://venditore:password@localhost:5432/progetto',
        'amministratore': 'postgresql://amministratore:password@localhost:5432/progetto'
    }

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   # Disabilita monitoraggio modifiche oggetti database
    app.config['SESSION_COOKIE_SECURE'] = True             # Abilita cookie di sessione in modalità sicura
    db.init_app(app)                                       # Inizializza SQLAlchemy con istanza applicazione Flask

    # Importazione blueprint
    from .logica import logica
    from .acquirente import acquirente
    from .venditore import venditore

    # Registrazione blueprint
    app.register_blueprint(logica, url_prefix='/')
    app.register_blueprint(acquirente, url_prefix='/acquirente')
    app.register_blueprint(venditore, url_prefix='/venditore')
    
    with app.app_context():                                          # Gestisce contesto per creazione tabelle
        try:                  
            db.create_all()                                          # Creazione tabelle
        except (ProgrammingError, OperationalError) as e:
            print("Errore durante la creazione delle tabelle:", e)
            pass                                                     # Se viene catturata un'eccezione continua l'esecuzione
    from .modelli import Utenti                                      # Importazione classe (tabella) Utenti
    
    # Configurazione e inizializzazione autenticazione e rotta 'logica.login' definita nel blueprint 'logica' 
    login_manager = LoginManager()
    login_manager.login_view = 'logica.login'
    login_manager.init_app(app)

    # Utilizza decoratore per caricamento utente 
    @login_manager.user_loader
    def load_user(user_id):
        user = Utenti.query.get(int(user_id))
        return user
    
    @app.before_request
    def before_request():
        g.user = current_user

    return app
