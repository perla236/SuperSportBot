import pandas as pd
import os

# --- POSTAVKE SISTEMA ---
MIN_KVOTA = 1.10  
MAX_KVOTA = 1.45  
# ------------------------

# 1. UČITAVANJE ZADNJEG EXCELA
files = [f for f in os.listdir('.') if f.startswith('supersport_ponuda') and f.endswith('.xlsx')]
if not files:
    print("❌ Nema Excel datoteke s linkovima! Prvo pokreni scraper.")
    exit()

latest_file = max(files, key=os.path.getctime)
print(f"📂 Analiziram ponudu iz: {latest_file}")

df = pd.read_excel(latest_file)
df = df.drop_duplicates(subset=['Domaćin', 'Gost'])

# 2. PRETVARANJE TEKSTA U BROJEVE
cols = ['1', 'X', '2']
for col in cols:
    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(99.0)

print("\n" + "="*60)
print(f"🎯 GENERIRANJE LISTE ZA BOTA (Kvote {MIN_KVOTA} - {MAX_KVOTA})")
print("="*60)

# --- TRAŽENJE DOMAĆIH ZICERA ---
domaci = df[(df['1'] >= MIN_KVOTA) & (df['1'] <= MAX_KVOTA)].copy()
domaci['Tip_Za_Igru'] = '1'     # Samo za ispis
domaci['Tip_Index'] = 0         # 0 = Prvi gumb (Kec)

# --- TRAŽENJE GOSTUJUĆIH ZICERA ---
gosti = df[(df['2'] >= MIN_KVOTA) & (df['2'] <= MAX_KVOTA)].copy()
gosti['Tip_Za_Igru'] = '2'      # Samo za ispis
gosti['Tip_Index'] = 2          # 2 = Treći gumb (Dvojka)

# --- SPAJANJE U JEDNU TABLICU ---
# Spajamo ih, sortiramo po vremenu (ako postoji) ili po domaćinu
finalna_lista = pd.concat([domaci, gosti], ignore_index=True)

if not finalna_lista.empty:
    # Spremanje u novi Excel koji će Bot čitati
    output_file = "za_bot_igranje.xlsx"
    finalna_lista.to_excel(output_file, index=False)
    
    print(f"\n✅ USPIJEH! Pronađeno je {len(finalna_lista)} parova.")
    print(finalna_lista[['Domaćin', 'Gost', 'Tip_Za_Igru', '1', '2']].to_string(index=False))
    print(f"\n📄 Podaci spremljeni u: {output_file}")
    print("👉 Sada pokreni 'auto_listic.py'!")
else:
    print("❌ Nema parova koji zadovoljavaju kriterij.")

print("="*60)