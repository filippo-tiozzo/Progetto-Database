# Importazione moduli
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from .modelli import Acquisto

# Definisce la Blueprint
acquirente = Blueprint('acquirente', __name__)

# Definisce la pagina del venditore
@acquirente.route('/', methods=['GET', 'POST'])
@login_required   # Decoratore per verifica autenticazione
def home():
    # Recupera tutti gli acquisti dell'utente corrente
    acquisti = Acquisto.query.filter_by(user_id=current_user.id).all()
    return render_template('acquirente.html', acquisti=acquisti)
