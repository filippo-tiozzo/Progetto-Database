# Importazione moduli
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from .modelli import Prodotto

# Definisce la Blueprint
venditore = Blueprint('venditore', __name__)

# Definisce la pagina del venditore
@venditore.route('/', methods=['GET', 'POST'])
@login_required   # Decoratore per verifica autenticazione
def home():
    # Recupera gli oggetti in vendita per l'utente corrente
    prodotti = Prodotto.query.filter_by(venditore_id=current_user.id).all()
    return render_template("venditore.html", prodotti=prodotti)
