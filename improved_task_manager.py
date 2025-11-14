import mysql.connector
from mysql.connector import Error

# 1. Připojení k databázi
def pripojeni_db():
    """
    Připojí se k MySQL serveru, vytvoří databázi 'improved_task_manager',
    pokud neexistuje, a vrátí spojení k této databázi.
    """
    try:
        # První připojení bez konkrétní databáze (umožní vytvoření databáze, pokud ještě neexistuje)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111"
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS improved_task_manager")
        cursor.close()
        conn.close()

        # Připojení přímo k existující databázi
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="improved_task_manager"
        )
        print("Připojení k databázi proběhlo úspěšně.")
        return conn

    except Error as e:
        print(f"Chyba při připojení k databázi: {e}")
        return None

# 2. Vytvoření tabulky 'ukoly'
def vytvoreni_tabulky(conn):
    """
    Vytvoří tabulku 'ukoly' s poli: 
    id, nazev, popis, stav, datum_vytvoreni - pokud ještě neexistuje.
    """
    try:
        cursor = conn.cursor()

        # SQL definice tabulky s typy a výchozími hodnotami
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('nezahájeno','probíhá','hotovo') NOT NULL DEFAULT 'nezahájeno',
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        print("Tabulka 'ukoly' byla vytvořena (nebo již existuje).")

    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")

# 3. Hlavní menu
def hlavni_menu() -> int:
    """
    Zobrazí hlavní nabídku programu a vrátí volbu uživatele (1-5).
    """
    while True:
        print("\nSprávce úkolů - Hlavní menu")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        try:
            volba = int(input("Vyberte možnost (1-5): "))
            if 1 <= volba <= 5:
                return volba
            else:
                print("\nNeplatná volba! Znovu vyberte možnost (1-5).")
        except ValueError:
            print("\nMusíte zadat číslo! Zkuste to znovu.")

# 4. Přidat úkol
def pridat_ukol(conn):
    """
    Přidá nový úkol do databáze. Uživatel zadá název a popis, které nesmí být prázdné.
    """
    # Získání platného názvu
    while True:
        nazev = input("\nZadejte název úkolu: ").strip()
        if not nazev:
            print("\nNázev úkolu nemůže být prázdný! Zkuste to znovu.")
        else:
            break

    # Získání platného popisu
    while True:
        popis = input("Zadejte popis úkolu: ").strip()
        if not popis:
            print("\nPopis úkolu nemůže být prázdný! Zkuste to znovu.")
        else:
            break

    # Uložení do databáze
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
            (nazev, popis)
        )
        conn.commit()
        cursor.close()
        print("Úkol byl úspěšně přidán.")
    except Error as e:
        print(f"Chyba při přidávání úkolu: {e}")

# 5. Zobrazit úkoly
def zobrazit_ukoly(conn):
    """
    Zobrazí všechny úkoly ve stavu 'nezahájeno' nebo 'probíhá'. 
    Pokud nejsou žádné úkoly, zobrazí odpovídající informaci.
    """
    try:
        cursor = conn.cursor()

        # SQL dotaz — filtrovaný výpis jen aktivních úkolů
        cursor.execute("""
            SELECT id, nazev, popis, stav
            FROM ukoly 
            WHERE stav IN ('nezahájeno','probíhá')
        """)
        vysledky = cursor.fetchall()
        cursor.close()

        if not vysledky:
            print("Seznam úkolů je prázdný.")
            return

        print("\n============ AKTIVNÍ ÚKOLY ============")
        for u in vysledky:
            print("-" * 40)
            print(f"{'ID:'} {u[0]}")
            print(f"{'Název:'} {u[1]}")
            print(f"{'Popis:'} {u[2]}")
            print(f"{'Stav:'} {u[3]}")
        print("-" * 40)

    except Error as e:
        print(f"Chyba při zobrazování úkolů: {e}")

# 6. Aktualizovat úkol
def aktualizovat_ukol(conn):
    """
    Aktualizuje stav úkolu podle zadaného ID. 
    Kontroluje existenci ID a platnost zadaného stavu.
    """
    # Zobrazení aktivních úkolů
    zobrazit_ukoly(conn)

    try:
        # Načtení ID úkolu a ověření, zda existuje
        id_ukolu = int(input("\nZadejte ID úkolu k aktualizaci: "))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ukoly WHERE id=%s", (id_ukolu,))

        if not cursor.fetchone():
            print("Úkol s tímto ID neexistuje!")
            cursor.close()
            return
        
        # Načtení nového stavu úkolu
        novy_stav = input("Zadejte nový stav (probíhá/hotovo): ").strip().lower()

        # Validace hodnoty ENUM
        if novy_stav not in ['probíhá','hotovo']:
            print("Neplatný stav!")
            cursor.close()
            return

        # Aktualizace stavu v databázi
        cursor.execute("UPDATE ukoly SET stav=%s WHERE id=%s", (novy_stav, id_ukolu))
        conn.commit()
        cursor.close()
        print("Úkol byl aktualizován.")

    except ValueError:
        print("ID musí být číslo!")
    except Error as e:
        print(f"Chyba při aktualizaci úkolu: {e}")

# 7. Odstranit úkol
def odstranit_ukol(conn):
    """
    Odstraní úkol podle zadaného ID. Kontroluje existenci ID v databázi.
    """
    # Zobrazení aktivních úkolů
    zobrazit_ukoly(conn)

    try:
        # Načtení ID a ověření existence
        id_ukolu = int(input("Zadejte ID úkolu, který chcete odstranit: "))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ukoly WHERE id=%s", (id_ukolu,))

        if not cursor.fetchone():
            print("Úkol s tímto ID neexistuje!")
            cursor.close()
            return

        # SQL DELETE dotaz
        cursor.execute("DELETE FROM ukoly WHERE id=%s", (id_ukolu,))
        conn.commit()
        cursor.close()
        print(f"Úkol s ID {id_ukolu} byl odstraněn.")

    except ValueError:
        print("ID musí být číslo.")
    except Error as e:
        print(f"Chyba při odstraňování úkolu: {e}")

# 8. Hlavní běh programu
def main():
    """
    Hlavní funkce programu - připojí se k databázi,
    vytvoří tabulku a spustí hlavní menu.
    """
    conn = pripojeni_db()
    if conn is None:
        return

    vytvoreni_tabulky(conn)

    while True:
        volba = hlavni_menu()

        if volba == 1:
            pridat_ukol(conn)
        elif volba == 2:
            zobrazit_ukoly(conn)
        elif volba == 3:
            aktualizovat_ukol(conn)
        elif volba == 4:
            odstranit_ukol(conn)
        elif volba == 5:
            print("\nProgram ukončen.")
            break
        else:
            print("Neplatná volba! Zkuste to znovu.")

    conn.close()

# Spuštění programu
if __name__ == "__main__":
    main()