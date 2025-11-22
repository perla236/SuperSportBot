import sys
sys.stdout.reconfigure(encoding='utf-8')

def scrape_supersport_final():
    print(" čekam učitavanje tablice...")

import pandas as pd
import os

# --- POSTAVKE SISTEMA ---
MIN_KVOTA = 1.10  
MAX_KVOTA = 1.45  
# ------------------------

files = [f for f in os.listdir('.') if f.startswith('supersport_ponuda') and f.endswith('.xlsx')]
if not files:
    print("Nema Excel datoteke s linkovima! Prvo pokreni scraper.")
    exit()

latest_file = max(files, key=os.path.getctime)
print(f"Analiziram ponudu iz: {latest_file}")

df = pd.read_excel(latest_file)
df = df.drop_duplicates(subset=['Domaćin', 'Gost'])

cols = ['1', 'X', '2']
for col in cols:
    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(99.0)

print("\n" + "="*60)
print(f"GENERIRANJE LISTE ZA BOTA (Kvote {MIN_KVOTA} - {MAX_KVOTA})")
print("="*60)

domaci = df[(df['1'] >= MIN_KVOTA) & (df['1'] <= MAX_KVOTA)].copy()
domaci['Tip_Za_Igru'] = '1'     
domaci['Tip_Index'] = 0         


gosti = df[(df['2'] >= MIN_KVOTA) & (df['2'] <= MAX_KVOTA)].copy()
gosti['Tip_Za_Igru'] = '2'      
gosti['Tip_Index'] = 2          

finalna_lista = pd.concat([domaci, gosti], ignore_index=True)

if not finalna_lista.empty:
    output_file = "za_bot_igranje.xlsx"
    finalna_lista.to_excel(output_file, index=False)
    
    print(f"\nUSPIJEH! Pronađeno je {len(finalna_lista)} parova.")
    print(finalna_lista[['Domaćin', 'Gost', 'Tip_Za_Igru', '1', '2']].to_string(index=False))
    print(f"\nPodaci spremljeni u: {output_file}")
    print("Sada pokreni 'auto_listic.py'!")
else:
    print("Nema parova koji zadovoljavaju kriterij.")

print("="*60)