GRANT INSERT, SELECT ON utenti, acquirente, venditore TO amministratore;

GRANT ALL PRIVILEGES ON SEQUENCE utenti_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE acquirente_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE venditore_id_seq TO amministratore;

GRANT SELECT, INSERT, UPDATE, DELETE ON Prodotto TO Venditore;
GRANT SELECT, UPDATE(spedito) ON OrdineProdotto TO Venditore;
GRANT SELECT, UPDATE(stato) ON Ordine TO Venditore;

GRANT SELECT, UPDATE(quantita) ON Prodotto TO Acquirente;
GRANT SELECT, DELETE ON Carrello TO Acquirente;
GRANT SELECT, INSERT, UPDATE, DELETE ON CarrelloProdotto TO Acquirente;
GRANT SELECT, INSERT  ON Ordine TO Acquirente;
GRANT SELECT, INSERT,  ON Ordine TO Acquirente;
GRANT SELECT, INSERT ON OrdineProdotto TO Acquirente;
GRANT SELECT, INSERT, UPDATE ON Recensione TO Acquirente;