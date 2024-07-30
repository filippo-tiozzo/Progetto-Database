# Importazione moduli
from flask import Blueprint, render_template
from flask_login import current_user, login_required

# Definisce la Blueprint
venditore = Blueprint('venditore', __name__)

# Definisce la pagina del venditore
@venditore.route('/', methods=['GET', 'POST'])
@login_required   # Decoratore per verifica autenticazione
def home():
    return render_template("venditore.html", user=current_user)
