ukoly = []

def hlavni_menu():
    while True:
        print()
        print("Správce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Odstranit úkol")
        print("4. Konec programu")
        print()

        volba = input("Vyberte možnost (1-4): ")

        if volba in ["1", "2", "3", "4"]:
            return volba
        
        else:
            print()
            print("Neplatná volba! Znovu vyberte možnost (1-4).")

def pridat_ukol():
    while True:
        print()
        nazev = input("Zadejte název úkolu: ").strip()
        if not nazev:
            print()
            print("Název úkolu nemůže být prázdný! Zkuste to znovu.")
            continue
        break

    while True:
        popis = input("Zadejte popis úkolu: ").strip()
        if not popis:
            print()
            print("Popis úkolu nemůže být prázdný! Zkuste to znovu.")
            continue
        break

    ukoly.append({"nazev": nazev, "popis": popis})
    print()
    print(f'Úkol "{nazev}" byl přidán.')
    
def zobrazit_ukoly():
    print()
    if not ukoly:
        print("Seznam úkolů je prázdný.")
    else:
        print("Seznam úkolů:")
        for i, u in enumerate(ukoly, start=1):
            print(f"{i}. {u['nazev']} - {u['popis']}")

def odstranit_ukol():
    print()
    if not ukoly:
        print("Seznam úkolů je prázdný.")
        return

    print("Seznam úkolů:")
    for i, u in enumerate(ukoly, start=1):
        print(f"{i}. {u['nazev']} - {u['popis']}")
    print()

    while True:
        try:
            cislo = int(input("Zadejte číslo úkolu, který chcete odstranit: "))
            if 1 <= cislo <= len(ukoly):
                smazany = ukoly.pop(cislo - 1)
                print()
                print(f"Úkol '{smazany['nazev']}' byl odstraněn.")
                break
            else:
                print()
                print(f"Úkol se zvoleným číslem {cislo} neexistuje! Zkuste to znovu.")
                print()
        except ValueError:
            print()
            print("Musíte zadat číslo! Zkuste to znovu.")
            print()

while True:
    volba = hlavni_menu()

    if volba == "1":
        pridat_ukol()
    elif volba == "2":
        zobrazit_ukoly()
    elif volba == "3":
        odstranit_ukol()
    elif volba == "4":
        print()
        print("Konec programu.")
        break