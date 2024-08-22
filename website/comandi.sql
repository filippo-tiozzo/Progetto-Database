CREATE DATABASE progetto;

CREATE ROLE amministratore WITH PASSWORD 'password';
CREATE ROLE acquirente WITH PASSWORD 'password';
CREATE ROLE venditore WITH PASSWORD 'password';

ALTER ROLE amministratore WITH LOGIN;
ALTER ROLE acquirente WITH LOGIN;
ALTER ROLE venditore WITH LOGIN;

psql -U postgres -d progetto -f percorso/alla/cartella/del/progetto/trigger.sql