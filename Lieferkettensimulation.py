import simpy
import random
import matplotlib.pyplot as plt
import pandas as pd
import os

# Parameter
lieferant1 = 10
lieferant2 = 5
batchSize1 = 12
batchSize2 = 8
randomNachfrage = False
tage = 100

# Diagramme
diagramStockUP = True
diagramStockEmpfaenger = True
diagramDemand = True
diagramMiss = True

# Ergebnis in csv schreiben
save_result = True

# Pfade

# Windows
# base_path = ""
# data_path = ""
# result_path = os.path.join(base_path, "simulation_results.csv")

# Mac
base_path = "/Volumes/Samsung T7 /Module/BI2/python/Lieferkettensimulation/Ausgabedateien/"
data_path = "/Volumes/Samsung T7 /Module/BI2/python/Lieferkettensimulation/Order Vorlagen-20231115-2/Order_History - 1.csv"
result_path = os.path.join(base_path, "simulation_results.csv")

# Prognosen
lineare_Regression = True
lr_Tage = 100
lr_Diagramm = True
lr_path = "linear_regression_demand_forecast.csv"

exponentielle_Glaettung = True
alpha = 0.05  # Anpassen des Glättungsparameters nach Bedarf (zwischen 0 und 1)
eg_Tage = 100
eg_Diagramm = True
eg_path = "exponential_smoothing_demand_forecast.csv"

konstante = True
k_Tage = 100
k_Diagramm = True
k_path = "constant_demand_forecast.csv"

# Ressourcen
stock1 = 0
stock2 = 0
miss1 = 0
miss2 = 0
cstock1 = 0
cstock2 = 0
nachfrage1 = 0
nachfrage2 = 0

#########################################################
# Prozesse in Lieferkette
#########################################################
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
    global stock1, stock2, cstock1, cstock2, batchSize1, batchSize2
    while True:
        yield env.timeout(1)
        if stock1 >= batchSize1:
            stock1 -= batchSize1
            cstock1 += batchSize1

        if stock2 >= batchSize2:
            stock2 -= batchSize2
            cstock2 += batchSize2

def Empfaenger(env):
    global nachfrage1, nachfrage2, miss1, miss2, cstock1, cstock2, randomNachfrage

    if not randomNachfrage and demand_data is None:
        raise ValueError("If randomNachfrage is False, demand_data must be provided.")

    while True:
        yield env.timeout(1)

        if randomNachfrage:
            nachfrage1 = random.randint(1, 4)
            nachfrage2 = random.randint(2, 8)
        else:
            # Read demand data from the CSV file
            demand_row = demand_data.iloc[env.now - 1]
            # ohne Datenfüllung
            # nachfrage1 = demand_row['Order1']
            # nachfrage2 = demand_row['Order2']
            # mit Datenfüllung
            nachfrage1 = demand_row['Order1'] if not pd.isna(demand_row['Order1']) else demand_data.loc[:env.now-1, 'Order1'].mean()
            nachfrage2 = demand_row['Order2'] if not pd.isna(demand_row['Order2']) else demand_data.loc[:env.now-1, 'Order2'].mean()

        miss1 = 0
        miss2 = 0

        if cstock1 >= nachfrage1:
            cstock1 -= nachfrage1
        else:
            miss1 = nachfrage1

        if cstock2 >= nachfrage2:
            cstock2 -= nachfrage2
        else:
            miss2 = nachfrage2

#########################################################
# Ergebnisse festhalten & random Nachfrage
#########################################################

# Read demand data from CSV if not using random demand
demand_data = None
if not randomNachfrage:
    demand_data = pd.read_csv(data_path, delimiter=';')

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


#########################################################
# Simulation
#########################################################

# Simulationsumgebung
env = simpy.Environment()

# Prozesse zur Umgebung hinzufügen
env.process(Lieferant1(env))
env.process(Lieferant2(env))
env.process(Umschlagspunkt(env))
env.process(Empfaenger(env))
env.process(update_ressourcen_liste(env))

# starten mit bestimmter Anzahl an Ticks (in Tagen)
env.run(until=tage+1)


#########################################################
# Diagramme
#########################################################

# Funktion zur Erstellung von Matplotlib-Diagrammen
def plot_diagrams(ressourcen_liste):
    if diagramStockUP:
        plot_stock_diagram(ressourcen_liste)

    if diagramStockEmpfaenger:
        plot_cstock_diagram(ressourcen_liste)

    if diagramDemand:
        plot_demand_diagram(ressourcen_liste)

    if diagramMiss:
        plot_miss_diagram(ressourcen_liste)

# Funktion zur Erstellung von Lagerbestandsdiagrammen
def plot_stock_diagram(ressourcen_liste):
    plt.figure(figsize=(12, 6))
    stock1_liste = [(zeitpunkt, stock1) for zeitpunkt, stock1, _, _, _, _, _, _, _ in ressourcen_liste]
    plt.plot(*zip(*stock1_liste), label='Lager stock1', linestyle='-')

    stock2_liste = [(zeitpunkt, stock2) for zeitpunkt, _, stock2, _, _, _, _, _, _ in ressourcen_liste]
    plt.plot(*zip(*stock2_liste), label='Lager stock2', linestyle='-')

    plt.title('Lagerbestand von stock1 und stock2')
    plt.xlabel('Zeit')
    plt.ylabel('Lagerbestand')
    plt.legend()

    plt.grid()
    plt.show()

# Funktion zur Erstellung von Lagerbestandsdiagrammen für Empfänger
def plot_cstock_diagram(ressourcen_liste):
    plt.figure(figsize=(12, 6))
    cstock1_liste = [(zeitpunkt, cstock1) for zeitpunkt, _, _, _, _, _, _, cstock1, _ in ressourcen_liste]
    plt.plot(*zip(*cstock1_liste), label='Lager cstock1', linestyle='-')

    cstock2_liste = [(zeitpunkt, cstock2) for zeitpunkt, _, _, _, _, _, _, _, cstock2 in ressourcen_liste]
    plt.plot(*zip(*cstock2_liste), label='Lager cstock2', linestyle='-')

    plt.title('Lagerbestand von cstock1 und cstock2')
    plt.xlabel('Zeit')
    plt.ylabel('Lagerbestand')
    plt.legend()

    plt.grid()
    plt.show()

# Funktion zur Erstellung von Nachfragendiagrammen
def plot_demand_diagram(ressourcen_liste):
    plt.figure(figsize=(12, 6))
    nachfrage1_liste = [(zeitpunkt, nachfrage1) for zeitpunkt, _, _, nachfrage1, _, _, _, _, _ in ressourcen_liste]
    plt.scatter(*zip(*nachfrage1_liste), label='Nachfrage G1')

    nachfrage2_liste = [(zeitpunkt, nachfrage2) for zeitpunkt, _, _, _, nachfrage2, _, _, _, _ in ressourcen_liste]
    plt.scatter(*zip(*nachfrage2_liste), label='Nachfrage G2')

    plt.title('Nachfrage von G1 und G2')
    plt.xlabel('Zeit')
    plt.ylabel('Nachfrage')
    plt.legend()

    plt.show()

# Funktion zur Erstellung von Missed Demand Diagrammen
def plot_miss_diagram(ressourcen_liste):
    plt.figure(figsize=(12, 6))
    miss1_liste = [(zeitpunkt, miss1) for zeitpunkt, _, _, _, _, miss1, _, _, _ in ressourcen_liste]
    plt.bar(*zip(*miss1_liste), label='Verpasste Nachfrage G1', color='blue', alpha=0.7)

    miss2_liste = [(zeitpunkt, miss2) for zeitpunkt, _, _, _, _, _, miss2, _, _ in ressourcen_liste]
    plt.bar(*zip(*miss2_liste), label='Verpasste Nachfrage G2', color='orange', alpha=0.7)

    plt.title('Verpasste Nachfrage von G1 und G2')
    plt.xlabel('Zeit')
    plt.ylabel('Verpasste Nachfrage')
    plt.legend()

    plt.show()

# Diagramme erstellen
plot_diagrams(ressourcen_liste)

#########################################################
# Ergebnis in csv / xlsx
#########################################################

def save_results(ressourcen_liste, result_path):
    columns = ['Zeitpunkt', 'Stock1', 'Stock2', 'Nachfrage1', 'Nachfrage2', 'Miss1', 'Miss2', 'CStock1', 'CStock2']
    df = pd.DataFrame(ressourcen_liste, columns=columns)

    if result_path.endswith('.xlsx'):
        df.to_excel(result_path, index=False)
    elif result_path.endswith('.csv'):
        df.to_csv(result_path, index=False)
    else:
        raise ValueError("Unsupported file format. Please use either .xlsx or .csv.")

if save_result:
    save_results(ressourcen_liste, result_path)


#########################################################
# Prognosen
#########################################################

#-------------------------------------------------------#
# lineare Regression
#-------------------------------------------------------#
def linear_regression(x, y):
    n = len(x)

    # Berechnung der benötigten Summen
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_squared = sum(xi ** 2 for xi in x)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))

    # Berechnung der Steigung (m) und des Achsenschnitts (b)
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
    b = (sum_y - m * sum_x) / n

    return m, b

def forecast_linear_regression(ressourcen_liste, forecast_days):
    # Extrahiere Zeitpunkte und Nachfrage von G1 und G2
    zeitpunkte = [zeitpunkt for zeitpunkt, _, _, _, _, _, _, _, _ in ressourcen_liste]
    nachfrage1 = [nachfrage1 for _, _, _, nachfrage1, _, _, _, _, _ in ressourcen_liste]
    nachfrage2 = [nachfrage2 for _, _, _, _, nachfrage2, _, _, _, _ in ressourcen_liste]

    # Führe lineare Regression für G1 durch
    m1, b1 = linear_regression(zeitpunkte, nachfrage1)
    # Prognostiziere Nachfrage für G1 für die nächsten Tage
    prognose_nachfrage1 = [int(m1 * zeitpunkt + b1) for zeitpunkt in range(max(zeitpunkte) + 1, max(zeitpunkte) + forecast_days + 1)]

    # Führe lineare Regression für G2 durch
    m2, b2 = linear_regression(zeitpunkte, nachfrage2)
    # Prognostiziere Nachfrage für G2 für die nächsten Tage
    prognose_nachfrage2 = [int(m2 * zeitpunkt + b2) for zeitpunkt in range(max(zeitpunkte) + 1, max(zeitpunkte) + forecast_days + 1)]

    # Erstelle Pandas DataFrame für die Prognose
    forecast_df = pd.DataFrame({
        'Zeitpunkt': range(max(zeitpunkte) + 1, max(zeitpunkte) + forecast_days + 1),
        'Prognose_Nachfrage1': prognose_nachfrage1,
        'Prognose_Nachfrage2': prognose_nachfrage2
    })

    # Anzeigen der Prognose im Konsolenausdruck
    # print("Prognose Nachfrage:")
    # print(forecast_df)

    # Speichern der Prognose in einer CSV-Datei
    forecast_path = os.path.join(base_path, lr_path)
    forecast_df.to_csv(forecast_path, index=False)



# Beispielaufruf für die Prognose mit linearer Regression
if lineare_Regression:
    forecast_days = lr_Tage
    forecast_linear_regression(ressourcen_liste, forecast_days)

#-------------------------------------------------------#
# exponentielle_Glaettung
#-------------------------------------------------------#

def exponential_smoothing(series, alpha):
    smoothed = [series[0]]  # Der erste Wert bleibt gleich
    for i in range(1, len(series)):
        smoothed.append(alpha * series[i] + (1 - alpha) * smoothed[i - 1])
    return smoothed

def forecast_exponential_smoothing(ressourcen_liste, forecast_days, alpha):
    # Extrahiere Zeitpunkte und Nachfrage von G1 und G2
    zeitpunkte = [zeitpunkt for zeitpunkt, _, _, _, _, _, _, _, _ in ressourcen_liste]
    nachfrage1 = [nachfrage1 for _, _, _, nachfrage1, _, _, _, _, _ in ressourcen_liste]
    nachfrage2 = [nachfrage2 for _, _, _, _, nachfrage2, _, _, _, _ in ressourcen_liste]

    # Wende exponentielle Glättung auf die Nachfrage von G1 an
    smoothed_nachfrage1 = exponential_smoothing(nachfrage1, alpha)
    # Prognostiziere Nachfrage für G1 für die nächsten Tage
    prognose_nachfrage1 = [max(0, int(smoothed_nachfrage1[-1] + alpha * (i + 1 - len(zeitpunkte)))) for i in
                           range(forecast_days)]

    # Wende exponentielle Glättung auf die Nachfrage von G2 an
    smoothed_nachfrage2 = exponential_smoothing(nachfrage2, alpha)
    # Prognostiziere Nachfrage für G2 für die nächsten Tage
    prognose_nachfrage2 = [max(0, int(smoothed_nachfrage2[-1] + alpha * (i + 1 - len(zeitpunkte)))) for i in
                           range(forecast_days)]

    # Erstelle Pandas DataFrame für die Prognose
    forecast_df = pd.DataFrame({
        'Zeitpunkt': range(max(zeitpunkte) + 1, max(zeitpunkte) + forecast_days + 1),
        'Prognose_Nachfrage1': prognose_nachfrage1,
        'Prognose_Nachfrage2': prognose_nachfrage2
    })

    # Speichern der Prognose in einer CSV-Datei
    forecast_path = os.path.join(base_path, eg_path)
    forecast_df.to_csv(forecast_path, index=False)

# Beispielaufruf für die Prognose
if exponentielle_Glaettung:
    forecast_days = eg_Tage
    forecast_exponential_smoothing(ressourcen_liste, forecast_days, alpha)

# -------------------------------------------------------#
# konstante
# -------------------------------------------------------#
def forecast_constant(ressourcen_liste, forecast_days, output_path):
    # Extrahiere Zeitpunkte
    zeitpunkte = [zeitpunkt for zeitpunkt, _, _, _, _, _, _, _, _ in ressourcen_liste]

    # Extrahiere Nachfrage-Daten
    nachfrage1_data = [nachfrage1 for _, _, _, nachfrage1, _, _, _, _, _ in ressourcen_liste]
    nachfrage2_data = [nachfrage2 for _, _, _, _, nachfrage2, _, _, _, _ in ressourcen_liste]

    # Berechne den Durchschnitt der bisherigen Nachfrage
    durchschnitt_nachfrage1 = sum(nachfrage1_data) / len(nachfrage1_data)
    durchschnitt_nachfrage2 = sum(nachfrage2_data) / len(nachfrage2_data)

    # Prognostiziere die konstante Nachfrage für die nächsten Tage
    prognose_nachfrage1 = [int(durchschnitt_nachfrage1)] * forecast_days
    prognose_nachfrage2 = [int(durchschnitt_nachfrage2)] * forecast_days

    # Erstelle eine Liste mit Zeitpunkten für die Prognose
    prognose_zeitpunkte = list(range(max(zeitpunkte) + 1, max(zeitpunkte) + forecast_days + 1))

    # Speichere die Prognose in eine DataFrame
    prognose_data = {
        'Zeitpunkt': prognose_zeitpunkte,
        'Prognose_Nachfrage1': prognose_nachfrage1,
        'Prognose_Nachfrage2': prognose_nachfrage2
    }
    df_prognose = pd.DataFrame(prognose_data)

    # Speichere die Prognose in eine CSV-Datei
    df_prognose.to_csv(output_path, index=False)

    return prognose_nachfrage1, prognose_nachfrage2


# ...

# Prognose für konstante Nachfrage
if konstante:
    output_path_konstante = os.path.join(base_path, k_path)
    prognose_nachfrage1_const, prognose_nachfrage2_const = forecast_constant(ressourcen_liste, k_Tage,
                                                                             output_path_konstante)


def visualize_forecasts(ressourcen_liste, forecast_df, title, xlabel, ylabel):
    # Matplotlib-Diagramm erstellen
    plt.figure(figsize=(12, 6))

    # Nachfrage G1 darstellen als Streudiagramm für die ersten 75 Tage
    nachfrage1_liste = [(zeitpunkt, nachfrage1) for zeitpunkt, _, _, nachfrage1, _, _, _, _, _ in ressourcen_liste]
    plt.scatter(*zip(*nachfrage1_liste), label='Nachfrage G1 (75 Tage)', color='blue')

    # Nachfrage G2 darstellen als Streudiagramm für die ersten 75 Tage
    nachfrage2_liste = [(zeitpunkt, nachfrage2) for zeitpunkt, _, _, _, nachfrage2, _, _, _, _ in ressourcen_liste]
    plt.scatter(*zip(*nachfrage2_liste), label='Nachfrage G2 (75 Tage)', color='orange')

    # Prognostizierte Nachfrage G1 darstellen als Linie für die folgenden Tage
    plt.plot(forecast_df['Zeitpunkt'], forecast_df['Prognose_Nachfrage1'], label='Prognose Nachfrage G1', linestyle='--', color='blue')

    # Prognostizierte Nachfrage G2 darstellen als Linie für die folgenden Tage
    plt.plot(forecast_df['Zeitpunkt'], forecast_df['Prognose_Nachfrage2'], label='Prognose Nachfrage G2', linestyle='--', color='orange')

    # Diagramm beschriften
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()

    # Diagramm anzeigen
    plt.grid()
    plt.show()

# Visualisierung der linearen Regression
if lineare_Regression and lr_Diagramm:
    forecast_days = lr_Tage
    forecast_linear_regression(ressourcen_liste, forecast_days)
    forecast_path_linear = os.path.join(base_path, lr_path)
    forecast_df_linear = pd.read_csv(forecast_path_linear)
    visualize_forecasts(ressourcen_liste, forecast_df_linear, 'Nachfrage Prognose mit Linearer Regression', 'Zeit', 'Nachfrage')

# Visualisierung der exponentiellen Glättung
if exponentielle_Glaettung and eg_Diagramm:
    forecast_days = eg_Tage
    forecast_exponential_smoothing(ressourcen_liste, forecast_days, alpha)
    forecast_path_exp_smooth = os.path.join(base_path, eg_path)
    forecast_df_exp_smooth = pd.read_csv(forecast_path_exp_smooth)
    visualize_forecasts(ressourcen_liste, forecast_df_exp_smooth, 'Nachfrage Prognose mit Exponentieller Glättung', 'Zeit', 'Nachfrage')

# Visualisierung der konstanten Nachfrage
if konstante and k_Diagramm:
    forecast_days = k_Tage
    output_path_konstante = os.path.join(base_path, k_path)
    prognose_nachfrage1_const, prognose_nachfrage2_const = forecast_constant(ressourcen_liste, forecast_days, output_path_konstante)
    forecast_df_constant = pd.read_csv(output_path_konstante)
    visualize_forecasts(ressourcen_liste, forecast_df_constant, 'Konstante Nachfrage Prognose', 'Zeit', 'Nachfrage')


#########################################################
# weitere Funktionen
#########################################################

def print_statistics(ressourcen_liste):
    def calculate_average(column_index):
        values = [entry[column_index] for entry in ressourcen_liste]
        return sum(values) / len(ressourcen_liste)

    def calculate_sum(column_index):
        return sum([entry[column_index] for entry in ressourcen_liste])

    def calculate_average_demand(column_index, ressourcen_liste):
        values = [entry[column_index] for entry in ressourcen_liste if
                  column_index in [3, 4]]  # Filtere nach Spalten 3 (Nachfrage1) und 4 (Nachfrage2)
        return sum(values) / len(values) if values else 0  # Vermeide Division durch Null

    stock1_durchschnitt = calculate_average(1)
    stock2_durchschnitt = calculate_average(2)
    cstock1_durchschnitt = calculate_average(7)
    cstock2_durchschnitt = calculate_average(8)

    miss1_summe = calculate_sum(5)
    miss2_summe = calculate_sum(6)
    gesamt_miss = miss1_summe + miss2_summe

    durchschnitt_nachfrage1 = calculate_average_demand(3, ressourcen_liste)
    durchschnitt_nachfrage2 = calculate_average_demand(4, ressourcen_liste)

    print(f"Durchschnitt Stock1: {stock1_durchschnitt}")
    print(f"Durchschnitt Stock2: {stock2_durchschnitt}")
    print(f"Durchschnitt CStock1: {cstock1_durchschnitt}")
    print(f"Durchschnitt CStock2: {cstock2_durchschnitt}")
    print(f"Summe Miss1: {miss1_summe}")
    print(f"Summe Miss2: {miss2_summe}")
    print(f"Gesamte Summe der verpassten Nachfrage: {gesamt_miss}")
    print(f"Durchschnitt Nachfrage1: {durchschnitt_nachfrage1}")
    print(f"Durchschnitt Nachfrage2: {durchschnitt_nachfrage2}")

# Aufruf der Funktion
print_statistics(ressourcen_liste)