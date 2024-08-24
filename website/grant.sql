GRANT INSERT, SELECT ON utenti, acquirente, venditore TO amministratore;

GRANT ALL PRIVILEGES ON SEQUENCE utenti_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE acquirente_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE venditore_id_seq TO amministratore;

GRANT SELECT, INSERT, UPDATE, DELETE ON prodotto TO Venditore;
GRANT SELECT, UPDATE(spedito) ON ordine_prodotto TO Venditore;
GRANT SELECT, UPDATE(stato) ON ordine TO Venditore;

GRANT SELECT, UPDATE(quantita) ON prodotto TO Acquirente;
GRANT SELECT, DELETE ON carrello TO Acquirente;
GRANT SELECT, INSERT, UPDATE, DELETE ON carrello_prodotto TO Acquirente;
GRANT SELECT, INSERT  ON ordine TO Acquirente;
GRANT SELECT, INSERT ON ordine_prodotto TO Acquirente;
GRANT SELECT, INSERT, UPDATE ON recensione TO Acquirente;