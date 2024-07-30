CREATE DATABASE progetto;

CREATE ROLE amministratore WITH PASSWORD 'password';
CREATE ROLE acquirente WITH PASSWORD 'password';
CREATE ROLE venditore WITH PASSWORD 'password';

ALTER ROLE amministratore WITH LOGIN;
ALTER ROLE acquirente WITH LOGIN;
ALTER ROLE venditore WITH LOGIN;

\c progetto

GRANT INSERT, SELECT ON utenti, acquirente, venditore TO amministratore;

GRANT ALL PRIVILEGES ON SEQUENCE utenti_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE acquirente_id_seq TO amministratore;
GRANT ALL PRIVILEGES ON SEQUENCE venditore_id_seq TO amministratore;
