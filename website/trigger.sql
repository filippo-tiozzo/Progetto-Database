
-- Crea o sostituisci la funzione di trigger
CREATE OR REPLACE FUNCTION applica_sconto()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se la quantità è maggiore di 1 e se lo sconto non è già stato applicato
    IF NEW.quantita > 1 AND NOT NEW.sconto THEN
        -- Imposta il flag dello sconto su TRUE
        NEW.sconto := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crea un trigger che usa la funzione 'applica_sconto'
CREATE TRIGGER trigger_applica_sconto
BEFORE INSERT OR UPDATE ON carrello_prodotto
FOR EACH ROW
EXECUTE FUNCTION applica_sconto();
