import pytest
import mysql.connector
from improved_task_manager import pridat_ukol, aktualizovat_ukol, odstranit_ukol, vytvoreni_tabulky

# Fixture pro připojení k testovací databázi
@pytest.fixture
def test_db():
    """
    Fixture, která vytvoří testovací databázi, připojí se k ní,
    připraví tabulku 'ukoly' a po dokončení testů databázi vyčistí.
    """
    try:
        # Připojení bez volby konkrétní databáze
        root_conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111"
        )
        root_cursor = root_conn.cursor()

        # Vytvoření testovací databáze, pokud ještě neexistuje
        root_cursor.execute("CREATE DATABASE IF NOT EXISTS improved_task_manager_test")
        root_cursor.close()
        root_conn.close()

        # Připojení přímo k testovací databázi
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="improved_task_manager_test"
        )

        # Vytvoření tabulky, pokud neexistuje
        vytvoreni_tabulky(conn)

        # Předání spojení testům
        yield conn

    finally:
        # Po testech se smažou testovací data a připojení se uzavře
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ukoly")
            conn.commit()
            cursor.close()
            conn.close()
    
# 1️. Testy pro přidání úkolu
def test_pridat_ukol_pozitivni(test_db, monkeypatch):
    """
    Ověří, že lze úspěšně přidat nový úkol pomocí simulovaného vstupu uživatele.
    """
    inputs = iter(["Testovací úkol", "Popis testovacího úkolu"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    pridat_ukol(test_db)

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM ukoly WHERE nazev='Testovací úkol'")
    vysledek = cursor.fetchone()
    assert vysledek is not None
    cursor.close()

def test_pridat_ukol_negativni(test_db, monkeypatch, capsys):
    """
    Ověří, že program nedovolí přidat úkol s prázdným názvem a vypíše chybové hlášení.
    """
    inputs = iter(["", "Testovací název", "Popis"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    pridat_ukol(test_db)
    captured = capsys.readouterr()
    assert "Název úkolu nemůže být prázdný" in captured.out

# 2️. Testy pro aktualizaci úkolu
def test_aktualizovat_ukol_pozitivni(test_db, monkeypatch):
    """
    Ověří, že lze úkol úspěšně aktualizovat na stav 'hotovo'.
    Test vytváří nový úkol, simuluje vstup uživatele a ověřuje aktualizaci v databázi.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES ('Úkol k aktualizaci', 'Test')")
    test_db.commit()
    id_ukolu = cursor.lastrowid

    inputs = iter([str(id_ukolu), "hotovo"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    aktualizovat_ukol(test_db)

    cursor.execute("SELECT stav FROM ukoly WHERE id=%s", (id_ukolu,))
    stav = cursor.fetchone()[0]
    assert stav == "hotovo"
    cursor.close()

def test_aktualizovat_ukol_negativni(test_db, monkeypatch, capsys):
    """
    Ověří, že program správně reaguje, pokud uživatel zadá neexistující ID úkolu.
    """
    inputs = iter(["9999", "hotovo"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    aktualizovat_ukol(test_db)

    captured = capsys.readouterr()
    assert "Úkol s tímto ID neexistuje" in captured.out

# 3️. Testy pro odstranění úkolu
def test_odstranit_ukol_pozitivni(test_db, monkeypatch):
    """
    Ověří, že úkol lze úspěšně odstranit. Test uloží nový úkol,
    simuluje zadání jeho ID a poté kontroluje, že již není v databázi.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES ('Úkol ke smazání', 'Test')")
    test_db.commit()
    id_ukolu = cursor.lastrowid

    inputs = iter([str(id_ukolu)])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    odstranit_ukol(test_db)

    cursor.execute("SELECT * FROM ukoly WHERE id=%s", (id_ukolu,))
    vysledek = cursor.fetchone()
    assert vysledek is None
    cursor.close()

def test_odstranit_ukol_negativni(test_db, monkeypatch, capsys):
    """
    Ověří, že program vypíše chybu, pokud se uživatel pokusí odstranit
    úkol s neexistujícím ID.
    """
    inputs = iter(["9999"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    odstranit_ukol(test_db)
    captured = capsys.readouterr()
    assert "Úkol s tímto ID neexistuje!" in captured.out