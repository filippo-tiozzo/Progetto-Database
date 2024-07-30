# Importazione moduli
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .modelli import login_utente, registrazione_utente

# Definizione blueprint
autorizzazioni = Blueprint('autorizzazioni', __name__)

# Creazione engine e sessione collegati al database 'amministratore'
def get_autho_session():
    db_autho_uri = current_app.config['SQLALCHEMY_BINDS']['amministratore']
    db_autho = create_engine(db_autho_uri)
    Session = sessionmaker(bind=db_autho)
    return Session()

# Definizione rotta '/'
@autorizzazioni.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:  
        return render_template("login.html", user=current_user)   # Visualizza template 'login.html' e passa utente autenticato
    else:
        return redirect(url_for('autorizzazioni.login'))          # Reindirizza alla pagina di login

# Definizione rotta '/logout'
@autorizzazioni.route('/logout')
@login_required                                          # Decoratore per verifica autenticazione
def logout():
    logout_user()                                        # Esegue logout
    flash('Logout effettuato con successo', 'success')
    return redirect(url_for('autorizzazioni.login'))     # Reindirizza alla pagina di login

# Definizione rotta '/login'
@autorizzazioni.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':

            # Passaggio campi dalla form HTML
            username = request.form.get('email')
            password = request.form.get('password')

            redirect_page = login_utente(username, password)              # Esegue login 
            if redirect_page:
                return redirect(url_for(redirect_page))
        return render_template("login.html", user=current_user)
    except Exception as e:
        flash('Error durante il login: {}'.format(e), category='error')
        return redirect(url_for('autorizzazioni.login'))                  # Reindirizza alla pagina di login

# Definizione rotta '/registrazione'
@autorizzazioni.route('/registrazione', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('venditore.home'))
    if request.method == 'POST':

        # Passaggio campi dalla form HTML
        nome = request.form.get('nome')
        cognome = request.form.get('cognome')
        email = request.form.get('email')
        password1 = request.form.get('password1') 
        password2 = request.form.get('password2')
        ruolo = request.form.get('ruolo')

        redirect_page = registrazione_utente(nome, cognome, email, password1, password2, ruolo)   # Esegue registrazione
        if redirect_page:
            return redirect(url_for(redirect_page))
    return render_template("registrazione.html", user=current_user)
