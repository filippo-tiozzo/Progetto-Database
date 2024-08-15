# Importazione moduli
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .modelli import login_utente, registrazione_utente, Prodotto
from .import db


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

# Definizione rotta '/vendi_prodotto'
@autorizzazioni.route('/vendi_prodotto', methods=['GET', 'POST'])
@login_required
def vendi_prodotto():
    if current_user.ruolo != 'Venditore':
        flash("Non hai i permessi necessari per mettere in vendita prodotti.", 'error')
        return redirect(url_for('autorizzazioni.home'))

    if request.method == 'POST':
        nome = request.form.get('nome')
        descrizione = request.form.get('descrizione')
        prezzo = request.form.get('prezzo')
        quantita = request.form.get('quantita')

        if not prezzo or float(prezzo) < 0:
            flash("Il prezzo deve essere un valore positivo.", 'error')
        elif not quantita or int(quantita) < 0:
            flash("La quantità deve essere un valore positivo.", 'error')
        elif not nome or not prezzo or not quantita:
            flash("Nome, prezzo e quantità sono obbligatori.", 'error')
            #return render_template('vendi_prodotto.html')

        try:
            nuovo_prodotto = Prodotto(
                nome=nome,
                descrizione=descrizione,
                prezzo=float(prezzo),
                quantita=int(quantita),
                venditore_id=current_user.id
            )
            db.session.add(nuovo_prodotto)
            db.session.commit()
            flash("Prodotto messo in vendita con successo!", 'success')
            return redirect(url_for('autorizzazioni.vendi_prodotto'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Errore durante l'inserimento del prodotto: {str(e)}", 'error')

    return render_template('vendi_prodotto.html')


# Rotta per eliminare un prodotto
@autorizzazioni.route('/elimina_prodotto/<int:prodotto_id>', methods=['POST'])
@login_required
def elimina_prodotto(prodotto_id):
    # Cerca il prodotto nel database
    prodotto = Prodotto.query.get_or_404(prodotto_id)
    
    # Controlla che il venditore corrente sia il proprietario del prodotto
    if prodotto.venditore_id != current_user.id:
        flash("Non sei autorizzato a rimuovere questo prodotto.", 'error')
        return redirect(url_for('venditore.home'))

    try:
        # Rimuove il prodotto dal database
        db.session.delete(prodotto)
        db.session.commit()
        flash("Prodotto rimosso con successo.", 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Errore durante la rimozione del prodotto: {str(e)}", 'error')

    return redirect(url_for('venditore.home'))

# Rotta per modificare un prodotto
@autorizzazioni.route('/modifica_prodotto/<int:prodotto_id>', methods=['GET', 'POST'])
@login_required
def modifica_prodotto(prodotto_id):
    prodotto = Prodotto.query.get_or_404(prodotto_id)

    # Verifica che l'utente sia il venditore del prodotto
    if prodotto.venditore_id != current_user.id:
        flash("Non sei autorizzato a modificare questo prodotto.", 'error')
        return redirect(url_for('venditore.home'))

    if request.method == 'POST':
        # Recupera i nuovi valori dal form
        nuovo_prezzo = request.form.get('prezzo')
        nuova_quantita = request.form.get('quantita')

        # Valida e aggiorna il prodotto
        if not nuovo_prezzo or float(nuovo_prezzo) < 0:
            flash("Il prezzo deve essere un valore positivo.", 'error')
        elif not nuova_quantita or int(nuova_quantita) < 0:
            flash("La quantità deve essere un valore positivo.", 'error')
        else:
            try:
                prodotto.prezzo = float(nuovo_prezzo)
                prodotto.quantita = int(nuova_quantita)
                db.session.commit()
                flash("Prodotto aggiornato con successo!", 'success')
                return redirect(url_for('venditore.home'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Errore durante l'aggiornamento del prodotto: {str(e)}", 'error')

    return render_template('modifica_prodotto.html', prodotto=prodotto)