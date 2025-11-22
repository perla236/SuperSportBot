from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_supersport_final():
    matches_data = []

    with sync_playwright() as p:
        # Pokrećemo preglednik (headless=False da vidiš proces)
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        url = "https://www.supersport.hr/sport/nogomet"
        print(f"⚽ Otvaram {url}...")
        page.goto(url)

        # Čekamo da se učita barem jedan red s utakmicom
        try:
            print("⏳ Čekam učitavanje tablice...")
            page.wait_for_selector('tr[data-id="TableRow"]', timeout=15000)
        except:
            print("❌ Stranica se nije učitala ili su promijenili kod.")
            browser.close()
            return

        # Simuliramo skrolanje do dna kako bi se učitale SVE utakmice (tzv. lazy loading)
        # Ponavljamo 5 puta (po potrebi povećaj broj)
        for i in range(5):
            page.mouse.wheel(0, 2000)
            time.sleep(1)
        
        # Uzimamo kompletan HTML stranice
        html_content = page.content()
        browser.close()

        # --- OBRADA PODATAKA (BeautifulSoup) ---
        print("🔍 Obrađujem podatke...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Pronađi sve redove koji predstavljaju utakmice
        rows = soup.find_all('tr', {'data-id': 'TableRow'})

        for row in rows:
            try:
                # 1. DOHVATI TIMOVE
                # Tražimo span koji ima data-id="IconLineName"
                team_box = row.find('span', {'data-id': 'IconLineName'})
                if team_box:
                    match_title = team_box.get_text(strip=True)
                    # Razdvoji "Domacin - Gost"
                    if " - " in match_title:
                        domacin, gost = match_title.split(" - ", 1)
                    else:
                        domacin, gost = match_title, "N/A"
                else:
                    continue # Preskoči ako nema imena

                # 2. DOHVATI VRIJEME
                time_box = row.find('span', {'data-id': 'StartTime'})
                start_time = time_box.get_text(strip=True) if time_box else "N/A"

                # 3. DOHVATI KVOTE
                # Kvote su u <td> elementima koji u klasi imaju "outcome"
                # Obično idu redom: 1, X, 2, 1X, X2, 12...
                odds_cells = row.find_all('td', class_=lambda x: x and 'outcome' in x)
                
                # Ponekad nema svih kvota, pa stavljamo "-" ako fali
                k1 = odds_cells[0].get_text(strip=True) if len(odds_cells) > 0 else "-"
                kx = odds_cells[1].get_text(strip=True) if len(odds_cells) > 1 else "-"
                k2 = odds_cells[2].get_text(strip=True) if len(odds_cells) > 2 else "-"
                k1x = odds_cells[3].get_text(strip=True) if len(odds_cells) > 3 else "-"
                kx2 = odds_cells[4].get_text(strip=True) if len(odds_cells) > 4 else "-"

                # Dodaj u listu
                matches_data.append({
                    "Vrijeme": start_time,
                    "Domaćin": domacin,
                    "Gost": gost,
                    "1": k1,
                    "X": kx,
                    "2": k2,
                    "1X": k1x,
                    "X2": kx2
                })
                
            except Exception as e:
                print(f"Greška na jednom redu: {e}")
                continue

    return matches_data

if __name__ == "__main__":
    podaci = scrape_supersport_final()
    
    if podaci:
        # Spremanje u Excel pomoću Pandas-a
        df = pd.DataFrame(podaci)
        filename = "supersport_ponuda.xlsx"
        df.to_excel(filename, index=False)
        
        print("\n" + "="*50)
        print(f"✅ GOTOVO! Uspješno dohvaćeno {len(podaci)} utakmica.")
        print(f"📄 Podaci su spremljeni u datoteku: {filename}")
        print("="*50)
        
        # Ispis prvih 5 za provjeru
        print(df.head().to_string())
    else:
        print("Nema podataka za spremanje.")