\c progetto

GRANT INSERT, SELECT ON utenti, acquirente, venditore TO amministratore;

GRANT ALL PRIVILEGES ON SEQUENCE utenti_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE acquirente_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE venditore_id_seq TO amministratore;
