# Importazione moduli
from flask import Blueprint, render_template
from flask_login import current_user, login_required

# Definisce la Blueprint
acquirente = Blueprint('acquirente', __name__)

# Definisce la pagina del venditore
@acquirente.route('/', methods=['GET', 'POST'])
@login_required   # Decoratore per verifica autenticazione
def home():
    return render_template("acquirente.html", user=current_user)
