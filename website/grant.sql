GRANT INSERT, SELECT ON utenti, acquirente, venditore TO amministratore;

GRANT ALL PRIVILEGES ON SEQUENCE utenti_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE acquirente_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE venditore_id_seq TO amministratore;

GRANT SELECT, INSERT, UPDATE, DELETE ON prodotto TO venditore;
GRANT SELECT, UPDATE(spedito) ON ordine_prodotto TO venditore;
GRANT SELECT, UPDATE(stato) ON ordine TO venditore;

GRANT SELECT, UPDATE(quantita) ON prodotto TO acquirente;
GRANT SELECT, DELETE ON carrello TO acquirente;
GRANT SELECT, INSERT, UPDATE, DELETE ON carrello_prodotto TO acquirente;
GRANT SELECT, INSERT  ON ordine TO acquirente;
GRANT SELECT, INSERT ON ordine_prodotto TO acquirente;
GRANT SELECT, INSERT, UPDATE ON recensione TO acquirente;