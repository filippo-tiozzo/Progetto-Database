# Importazione moduli
from website import create_app

app = create_app()           # Creazione applicazione Flask
if __name__ == '__main__':   # Esegue l'applicazione solo se lo script è stato avviato direttamente e non importato
    app.run(debug=True)      # Avvia l'applicazione in modalià debug
