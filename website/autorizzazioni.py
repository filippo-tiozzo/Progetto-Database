# Importazione moduli
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .modelli import login_utente, registrazione_utente, Prodotto, Carrello, CarrelloProdotto, Ordine, OrdineProdotto, Acquisto, Recensione, Venditore
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

@autorizzazioni.route('/gestisci_ordini', methods=['GET'])
@login_required
def gestisci_ordini():
    venditore = Venditore.query.filter_by(user_id=current_user.id).first()

    if not venditore:
        flash('Non sei autorizzato a gestire gli ordini', category='error')
        return redirect(url_for('home'))  # Reindirizza a una pagina di default o errore

    prodotti_venduti = Prodotto.query.filter_by(venditore_id=venditore.id).all()
    prodotti_venditori_ids = {p.id for p in prodotti_venduti}

    ordini_ids = set()
    for prodotto in prodotti_venduti:
        ordini_prodotti = OrdineProdotto.query.filter_by(prodotto_id=prodotto.id).all()
        for ordine_prodotto in ordini_prodotti:
            ordine = Ordine.query.get(ordine_prodotto.ordine_id)
            if ordine and any(op.prodotto_id in prodotti_venditori_ids for op in ordine.prodotti):
                ordini_ids.add(ordine.id)

    ordini = Ordine.query.filter(Ordine.id.in_(ordini_ids)).all()

    return render_template('gestisci_ordini.html', ordini=ordini, prodotti_venditore=prodotti_venditori_ids)

# Rotta per spedire i propri prodotti
@autorizzazioni.route('/spedisci_ordine/<int:ordine_id>', methods=['POST'])
@login_required
def spedisci_ordine(ordine_id):
    ordine = Ordine.query.get_or_404(ordine_id)
    
    # Trova tutti i prodotti dell'ordine
    prodotti_ordine = OrdineProdotto.query.filter_by(ordine_id=ordine_id).all()
    prodotti_venditore = {p.id for p in Prodotto.query.filter_by(venditore_id=current_user.id).all()}

    # Aggiorna lo stato di spedizione dei prodotti venduti dal venditore
    for op in prodotti_ordine:
        if op.prodotto_id in prodotti_venditore:
            op.spedito = True
   
    # Controlla se tutti i prodotti (di tutti i venditori) sono stati spediti
    tutti_spediti = all(op.spedito for op in prodotti_ordine)
    
    # Se tutti i prodotti dell'ordine sono spediti, aggiorna lo stato dell'ordine
    if tutti_spediti:
        ordine.stato = 'spedito'
    else:
        ordine.stato = 'in elaborazione'

    db.session.commit()
    flash("Ordine aggiornato!", 'success')

    return redirect(url_for('autorizzazioni.gestisci_ordini'))


# Rotta per aggiungere un prodotto al carrello
@autorizzazioni.route('/aggiungi_al_carrello/<int:prodotto_id>', methods=['POST'])
@login_required
def aggiungi_al_carrello(prodotto_id):
    prodotto = Prodotto.query.get_or_404(prodotto_id)
    carrello = Carrello.query.filter_by(user_id=current_user.id).first()
    
    if not carrello:
        carrello = Carrello(user_id=current_user.id)
        db.session.add(carrello)
    
    carrello_prodotto = CarrelloProdotto.query.filter_by(carrello_id=carrello.id, prodotto_id=prodotto.id).first()

    if carrello_prodotto:
        carrello_prodotto.quantita += 1
    else:
        carrello_prodotto = CarrelloProdotto(carrello_id=carrello.id, prodotto_id=prodotto.id, quantita=1)
        db.session.add(carrello_prodotto)

    db.session.commit()
    flash("Prodotto aggiunto al carrello!", 'success')
    #return render_template('risultati_ricerca.html', prodotto_id=prodotto)
    return redirect(url_for('acquirente.home'))

# Rotta per rimuovere un prodotto dal carrello
@autorizzazioni.route('/rimuovi_dal_carrello/<int:carrello_prodotto_id>', methods=['POST'])
@login_required
def rimuovi_dal_carrello(carrello_prodotto_id):   #rimuove il prodotto dal carrello o ne diminuisce la quantità di 1
    carrello_prodotto = CarrelloProdotto.query.get_or_404(carrello_prodotto_id)
    
    if carrello_prodotto.carrello.user_id != current_user.id:
        flash("Non sei autorizzato a rimuovere questo prodotto dal carrello.", 'error')
        return redirect(url_for('autorizzazioni.visualizza_carrello'))
    try:
        # Riduci la quantità di 1
        if carrello_prodotto.quantita > 1:
            carrello_prodotto.quantita -= 1
            flash("Quantità del prodotto diminuita di 1", 'success')
        else:
            # Se la quantità è 1, rimuovi il prodotto dal carrello
            db.session.delete(carrello_prodotto)
            flash("Prodotto rimosso dal carrello.", 'success')
        db.session.commit()
        return redirect(url_for('autorizzazioni.visualizza_carrello'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Errore durante la rimozione del prodotto: {str(e)}", 'error')

@autorizzazioni.route('/carrello', methods=['GET'])
@login_required
def visualizza_carrello():
    carrello = Carrello.query.filter_by(user_id=current_user.id).first()
    if not carrello:
        carrello = Carrello(user_id=current_user.id)
        db.session.add(carrello)
        db.session.commit()
    carrello_prodotti = CarrelloProdotto.query.filter_by(carrello_id=carrello.id).all()
    return render_template('carrello.html', prodotti=carrello_prodotti)

# Rotta per la ricerca dei prodotti 
@autorizzazioni.route('/ricerca_prodotto', methods=['GET', 'POST'])
def ricerca_prodotto():
    nome = request.form.get('nome')
    prezzo_min = request.form.get('prezzo_min')
    prezzo_max = request.form.get('prezzo_max')

    query = Prodotto.query
    
    if nome:
        query = query.filter(Prodotto.nome.ilike(f'%{nome}%'))
    if prezzo_min:
        query = query.filter(Prodotto.prezzo >= float(prezzo_min))
    if prezzo_max:
        query = query.filter(Prodotto.prezzo <= float(prezzo_max))

    prodotti = query.all()

    return render_template('risultati_ricerca.html', prodotti=prodotti)

@autorizzazioni.route('/ricerca_prodotti', methods=['GET'])
def mostra_form_ricerca():
    return render_template('ricerca_prodotti.html')

@autorizzazioni.route('/acquista', methods=['POST'])
@login_required
def acquista():
    # Ottieni il carrello dell'utente
    carrello = Carrello.query.filter_by(user_id=current_user.id).first_or_404()

    # Verifica se il carrello è vuoto
    if not carrello.prodotti:
        flash('Il carrello è vuoto.', 'error')
        return redirect(url_for('autorizzazioni.visualizza_carrello'))

    # Creazione di un nuovo ordine
    nuovo_ordine = Ordine(user_id=current_user.id)
    db.session.add(nuovo_ordine)
    db.session.flush()  # Flush per ottenere l'ID dell'ordine

    try:
        # Per ogni prodotto nel carrello, crea una riga in OrdineProdotto e aggiorna la quantità del prodotto
        for carrello_prodotto in carrello.prodotti:
            prodotto = Prodotto.query.get(carrello_prodotto.prodotto_id)
            
            if prodotto.quantita < carrello_prodotto.quantita:
                flash(f"Quantità insufficiente per il prodotto {prodotto.nome}.", 'error')
                return redirect(url_for('autorizzazioni.visualizza_carrello'))

            # Riduci la quantità del prodotto disponibile
            prodotto.quantita -= carrello_prodotto.quantita

            # Aggiungi il prodotto all'ordine
            ordine_prodotto = OrdineProdotto(
                ordine_id=nuovo_ordine.id,
                prodotto_id=prodotto.id,
                quantita=carrello_prodotto.quantita
            )
            db.session.add(ordine_prodotto)

            # Crea una nuova voce in Acquisto per tracciare la transazione
            nuovo_acquisto = Acquisto(
                user_id=current_user.id,
                prodotto_id=prodotto.id,
                quantita=carrello_prodotto.quantita
            )
            db.session.add(nuovo_acquisto)

             # Elimina il prodotto dal carrello
            db.session.delete(carrello_prodotto)

        # Svuota il carrello
        #db.session.query(CarrelloProdotto).filter_by(carrello_id=carrello.id).delete()
        db.session.delete(carrello)

        # Salva le modifiche
        db.session.commit()
        flash("Acquisto completato con successo!", 'success')
        return redirect(url_for('acquirente.home'))

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Errore durante l'acquisto: {str(e)}", 'error')
        return redirect(url_for('autorizzazioni.visualizza_carrello'))
    
@autorizzazioni.route('/recensione/<int:prodotto_id>', methods=['GET', 'POST'])
@login_required
def recensione_prodotto(prodotto_id):
    prodotto = Prodotto.query.get(prodotto_id)
    if not prodotto:
        flash("Prodotto non trovato.", 'error')
        return redirect(url_for('acquirente.home'))

    # Verifica se l'utente ha già inviato una recensione per questo prodotto
    recensione = Recensione.query.filter_by(prodotto_id=prodotto_id, user_id=current_user.id).first()

    if request.method == 'POST':
        voto = request.form.get('voto')
        if voto and voto.isdigit() and 1 <= int(voto) <= 5:
            if recensione:
                # Aggiorna la recensione esistente
                recensione.voto = int(voto)
                flash("Recensione modificata con successo!", 'success')
            else:
                # Crea una nuova recensione
                recensione = Recensione(
                    prodotto_id=prodotto_id,
                    user_id=current_user.id,
                    voto=int(voto)
                )
                db.session.add(recensione)
                flash("Recensione salvata con successo!", 'success')            
            db.session.commit()
            return redirect(url_for('acquirente.home'))

    # Passa la recensione esistente al template per precompilare il modulo
    return render_template('recensione_prodotto.html', prodotto=prodotto, recensione=recensione)
