import pandas as pd
import os
from datetime import datetime

# 1. UČITAVANJE ZADNJEG EXCELA
# Tražimo najnoviju datoteku koja počinje sa "supersport"
files = [f for f in os.listdir('.') if f.startswith('supersport') and f.endswith('.xlsx')]
if not files:
    print("❌ Nisam našao Excel datoteku! Prvo pokreni scraper.")
    exit()

latest_file = max(files, key=os.path.getctime)
print(f"📂 Učitavam podatke iz: {latest_file}")

df = pd.read_excel(latest_file)

# 2. ČIŠĆENJE PODATAKA (Pretvaranje teksta "1,50" u broj 1.50)
# Stupci s kvotama koje želimo analizirati
kvote_cols = ['1', 'X', '2', '1X', 'X2']

for col in kvote_cols:
    # Zamijeni zarez točkom, pretvori "-" u 0, i pretvori u broj
    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- OVDJE DEFINIRAMO SISTEME ---

print("\n" + "="*60)
print("📊 REZULTATI ANALIZE")
print("="*60)

# SISTEM 1: "Sigurice" (Favorit igra doma)
# Uvjet: Kvota na 1 je između 1.20 i 1.50
print("\n🔹 SISTEM 1: Domaći favoriti (1.20 - 1.50)")
ziceri = df[(df['1'] >= 1.20) & (df['1'] <= 1.50)]

if not ziceri.empty:
    # Sortiramo od najmanje kvote prema većoj
    print(ziceri[['Vrijeme', 'Domaćin', 'Gost', '1']].sort_values(by='1').to_string(index=False))
else:
    print("Nema utakmica za ovaj kriterij.")

# SISTEM 2: "Lov na X" (Neriješeno)
# Uvjet: Domaćin i Gost su podjednaki (kvote na 1 i 2 su iznad 2.40), a X je ispod 3.20
print("\n🔹 SISTEM 2: Potencijalni X (Izjednačene ekipe)")
iksevi = df[(df['1'] > 2.40) & (df['2'] > 2.40) & (df['X'] < 3.20) & (df['X'] > 1.0)]

if not iksevi.empty:
    print(iksevi[['Vrijeme', 'Domaćin', 'Gost', '1', 'X', '2']].to_string(index=False))
else:
    print("Nema utakmica za ovaj kriterij.")

# SISTEM 3: "Value Bet" (Dobra kvota na favorita)
# Uvjet: Kvota na pobjedu (bilo 1 ili 2) je između 1.70 i 2.10 (često se smatra 'isplativim' rizikom)
print("\n🔹 SISTEM 3: 'Value' zona (Kvota 1.70 - 2.10)")
value_bets = df[
    ((df['1'] >= 1.70) & (df['1'] <= 2.10)) | 
    ((df['2'] >= 1.70) & (df['2'] <= 2.10))
]

if not value_bets.empty:
    # Prikazujemo samo relevantne stupce
    print(value_bets[['Vrijeme', 'Domaćin', 'Gost', '1', '2']].to_string(index=False))
else:
    print("Nema utakmica za ovaj kriterij.")

print("\n" + "="*60)