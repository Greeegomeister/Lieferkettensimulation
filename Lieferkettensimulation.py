import simpy
import random
import matplotlib.pyplot as plt
import pandas as pd

lieferant1 = 10
lieferant2 = 5
tage = 75

# Direkte Definition der Ressourcen
stock1 = 0
stock2 = 0
miss1 = 0
miss2 = 0
cstock1 = 0
cstock2 = 0
nachfrage1 = 0
nachfrage2 = 0

# Prozesse
def Lieferant1(env):
    global stock1
    while True:
        yield env.timeout(2)
        stock1 += lieferant1

def Lieferant2(env):
    global stock2
    while True:
        yield env.timeout(1)
        stock2 += lieferant2

def Umschlagspunkt(env):
    global stock1, stock2, cstock1, cstock2
    while True:
        yield env.timeout(1)
        if stock1 >= 12:
            stock1 -= 12
            cstock1 += 12

        if stock2 >= 8:
            stock2 -= 8
            cstock2 += 8

def Empfaenger(env):
    global nachfrage1, nachfrage2, miss1, miss2, cstock1, cstock2
    while True:
        yield env.timeout(1)
        nachfrage_g1 = random.randint(1, 4)
        nachfrage_g2 = random.randint(2, 8)
        nachfrage1 = nachfrage_g1
        nachfrage2 = nachfrage_g2
        miss1 = 0
        miss2 = 0
        if cstock1 >= nachfrage_g1:
            cstock1 -= nachfrage_g1
        else:
            miss1 = nachfrage_g1

        if cstock2 >= nachfrage_g2:
            cstock2 -= nachfrage_g2
        else:
            miss2 = nachfrage_g2

# Liste für die Ressourcenwerte
ressourcen_liste = []

# Funktion zum Aktualisieren der Ressourcenwerte und Hinzufügen zur Liste
def update_ressourcen_liste(env):
    while True:
        yield env.timeout(1)
        ressourcen_liste.append((
            env.now,
            stock1,
            stock2,
            nachfrage1,
            nachfrage2,
            miss1,
            miss2,
            cstock1,
            cstock2
        ))

# Simulationsumgebung
env = simpy.Environment()

# Prozesse zur Umgebung hinzufügen
env.process(Lieferant1(env))
env.process(Lieferant2(env))
env.process(Umschlagspunkt(env))
env.process(Empfaenger(env))
env.process(update_ressourcen_liste(env))

# starten mit bestimmter Anzahl an Ticks (in Tagen)
env.run(until=tage)

# Restlicher Code bleibt unverändert...


# Matrix
print("Matrix der Ressourcenwerte:")
for zeitpunkt, stock1, stock2, nachfrage1, nachfrage2 ,miss1, miss2, cstock1, cstock2 in ressourcen_liste:
    print(f"Zeitpunkt: {zeitpunkt}, Stock1: {stock1}, Stock2: {stock2}, Nachfrage1: {nachfrage1}, Nachfrage2: {nachfrage2}, Miss1: {miss1}, Miss2: {miss2}, CStock1: {cstock1}, CStock2: {cstock2}")

# Berechne den Durchschnitt für stock1
stock1_durchschnitt = sum([stock1 for _, stock1, _, _, _, _, _, _, _ in ressourcen_liste]) / len(ressourcen_liste)

# Berechne den Durchschnitt für stock2
stock2_durchschnitt = sum([stock2 for _, _, stock2, _, _, _, _, _, _ in ressourcen_liste]) / len(ressourcen_liste)

# Gib die Durchschnittswerte aus
print(f"Durchschnitt Stock1: {stock1_durchschnitt}")
print(f"Durchschnitt Stock2: {stock2_durchschnitt}")

# Berechne den Durchschnitt für cstock1
cstock1_durchschnitt = sum([cstock1 for _, _, _, _, _, _, _, cstock1, _ in ressourcen_liste]) / len(ressourcen_liste)

# Berechne den Durchschnitt für cstock2
cstock2_durchschnitt = sum([cstock2 for _, _, _, _, _, _, _, _, cstock2 in ressourcen_liste]) / len(ressourcen_liste)

# Gib die Durchschnittswerte aus
print(f"Durchschnitt CStock1: {cstock1_durchschnitt}")
print(f"Durchschnitt CStock2: {cstock2_durchschnitt}")

# Berechne die Summe der verpassten Nachfrage für miss1 und miss2
miss1_summe = sum([miss1 for _, _, _, _, _, miss1, _, _, _ in ressourcen_liste])
miss2_summe = sum([miss2 for _, _, _, _, _, _, miss2, _, _ in ressourcen_liste])

# Berechne die Gesamtsumme der verpassten Nachfrage
gesamt_miss = miss1_summe + miss2_summe

# Gib die Summen aus
print(f"Summe Miss1: {miss1_summe}")
print(f"Summe Miss2: {miss2_summe}")
print(f"Gesamte Summe der verpassten Nachfrage: {gesamt_miss}")



# Matplotlib-Diagramm erstellen
plt.figure(figsize=(12, 6))

# Lagerbestand von stock1 darstellen
stock1_liste = [(zeitpunkt, stock1) for zeitpunkt, stock1, _, _, _, _, _, _, _ in ressourcen_liste]
plt.plot(*zip(*stock1_liste), label='Lager stock1', linestyle='-')

# Lagerbestand von stock2 darstellen
stock2_liste = [(zeitpunkt, stock2) for zeitpunkt, _, stock2, _, _, _, _, _, _ in ressourcen_liste]
plt.plot(*zip(*stock2_liste), label='Lager stock2', linestyle='-')

# Diagramm beschriften
plt.title('Lagerbestand von stock1 und stock2')
plt.xlabel('Zeit')
plt.ylabel('Lagerbestand')
plt.legend()

# Diagramm anzeigen
plt.grid()
plt.show()

# Matplotlib-Diagramm erstellen
plt.figure(figsize=(12, 6))

# Lagerbestand von cstock1 darstellen
cstock1_liste = [(zeitpunkt, cstock1) for zeitpunkt, _, _, _, _, _, _, cstock1, _ in ressourcen_liste]
plt.plot(*zip(*cstock1_liste), label='Lager cstock1', linestyle='-')

# Lagerbestand von cstock2 darstellen
cstock2_liste = [(zeitpunkt, cstock2) for zeitpunkt, _, _, _, _, _, _, _, cstock2 in ressourcen_liste]
plt.plot(*zip(*cstock2_liste), label='Lager cstock2', linestyle='-')

# Diagramm beschriften
plt.title('Lagerbestand von cstock1 und cstock2')
plt.xlabel('Zeit')
plt.ylabel('Lagerbestand')
plt.legend()

# Diagramm anzeigen
plt.grid()
plt.show()

# Matplotlib-Diagramme erstellen
plt.figure(figsize=(12, 6))

# Nachfrage G1 darstellen
nachfrage1_liste = [(zeitpunkt, nachfrage1) for zeitpunkt, _, _, nachfrage1, _, _, _, _, _ in ressourcen_liste]
plt.plot(*zip(*nachfrage1_liste), label='Nachfrage G1', linestyle='-')

# Nachfrage G2 darstellen
nachfrage2_liste = [(zeitpunkt, nachfrage2) for zeitpunkt, _, _, _, nachfrage2, _, _, _, _ in ressourcen_liste]
plt.plot(*zip(*nachfrage2_liste), label='Nachfrage G2', linestyle='-')

# Diagramm für Nachfrage beschriften
plt.title('Nachfrage von G1 und G2')
plt.xlabel('Zeit')
plt.ylabel('Nachfrage')
plt.legend()

# Zweites Diagramm erstellen
plt.figure(figsize=(12, 6))

# Verpasste Nachfrage G1 darstellen
miss1_liste = [(zeitpunkt, miss1) for zeitpunkt, _, _, _, _, miss1, _, _, _ in ressourcen_liste]
plt.plot(*zip(*miss1_liste), label='Verpasste Nachfrage G1', linestyle='-')

# Verpasste Nachfrage G2 darstellen
miss2_liste = [(zeitpunkt, miss2) for zeitpunkt, _, _, _, _, _, miss2, _, _ in ressourcen_liste]
plt.plot(*zip(*miss2_liste), label='Verpasste Nachfrage G2', linestyle='-')

# Diagramm für verpasste Nachfrage beschriften
plt.title('Verpasste Nachfrage von G1 und G2')
plt.xlabel('Zeit')
plt.ylabel('Verpasste Nachfrage')
plt.legend()

# Diagramme anzeigen
plt.grid()
plt.show()

# Matrix in Pandas DataFrame umwandeln
columns = ['Zeitpunkt', 'Stock1', 'Stock2', 'Nachfrage1', 'Nachfrage2', 'Miss1', 'Miss2', 'CStock1', 'CStock2']
df = pd.DataFrame(ressourcen_liste, columns=columns)

# Excel-Datei erstellen und DataFrame darin speichern
excel_path = '/Users/grego/Desktop/simulation_results.xlsx'
df.to_excel(excel_path, index=False)