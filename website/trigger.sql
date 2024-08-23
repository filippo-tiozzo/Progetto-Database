
-- Crea o sostituisci la funzione di trigger per applicare lo sconto
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



-- Crea o sostituisci la funzione di trigger per togliere lo sconto
CREATE OR REPLACE FUNCTION rimuovi_sconto()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se la quantità è diventata minore di 2 per rimuovere lo sconto
    IF NEW.quantita < 2 THEN
        -- Imposta il flag dello sconto su FALSE
        NEW.sconto := FALSE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crea un trigger che usa la funzione 'rimuovi_sconto'
CREATE TRIGGER trigger_rimuovi_sconto
BEFORE UPDATE ON carrello_prodotto
FOR EACH ROW
WHEN (OLD.quantita >= 2 AND NEW.quantita < 2)
EXECUTE FUNCTION rimuovi_sconto();
