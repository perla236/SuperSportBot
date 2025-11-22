from playwright.sync_api import sync_playwright
import pandas as pd
import time

def napuni_listic_sistem():
    # 1. UČITAVANJE PRIPREMLJENIH ZICERA
    try:
        filename = "za_bot_igranje.xlsx"
        df = pd.read_excel(filename)
        
        if df.empty:
            print("❌ Tablica je prazna.")
            return
        
        # Uzmi prvih 15 parova
        parovi = df.head(15)
        
        print(f"🎯 Učitano {len(parovi)} parova za igranje.")
        print("-" * 40)

    except Exception as e:
        print(f"❌ Greška: Nema datoteke '{filename}'. Prvo pokreni 'ziceri.py'!")
        return

    with sync_playwright() as p:
        print("🚀 Pokrećem preglednik...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = context.new_page()

        print("⚽ Otvaram SuperSport...")
        page.goto("https://www.supersport.hr/sport/nogomet", timeout=90000)
        
        try:
            page.locator("button:has-text('Prihvati sve')").click(timeout=3000)
        except:
            pass

        time.sleep(2)

        # 2. PETLJA KROZ PAROVE
        for index, row in parovi.iterrows():
            domacin = str(row['Domaćin']).strip()
            tip_index = int(row['Tip_Index']) # 0 za Kec, 2 za Dvojku
            tip_naziv = "Domaćin" if tip_index == 0 else "Gost"
            
            print(f"\n🔍 Tražim: {domacin} (Igram: {tip_naziv})...")
            
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.2)
            
            pronaden = False
            
            # Skrolanje i traženje
            for scroll_attempt in range(20):
                try:
                    # Traži red s imenom domaćina
                    match_row = page.locator(f'tr[data-id="TableRow"]:has-text("{domacin}")').first
                    
                    if match_row.is_visible():
                        # Traži gumb na temelju indeksa!
                        # .nth(0) = 1, .nth(1) = X, .nth(2) = 2
                        kvota_btn = match_row.locator('td[class*="table-outcomes-module_outcome"]').nth(tip_index)
                        
                        # Provjeri je li već odabrano
                        if "selected" in kvota_btn.get_attribute("class"):
                            print(f"   -> Već je na listiću.")
                            pronaden = True
                            break

                        kvota_btn.scroll_into_view_if_needed()
                        kvota_btn.click(force=True)
                        
                        print(f"✅ KLIKNUTO: {domacin} -> Tip {tip_index + 1}") # +1 jer je index 0 ustvari tip 1
                        pronaden = True
                        time.sleep(0.3)
                        break 
                    
                    else:
                        page.mouse.wheel(0, 700)
                        time.sleep(0.2)

                except Exception:
                    page.mouse.wheel(0, 700)
                    time.sleep(0.2)

            if not pronaden:
                print(f"⚠️ Nisam našao: {domacin}")

        print("\n" + "="*50)
        print("🏁 GOTOVO! Provjeri listić.")
        print("="*50)
        
        time.sleep(600) 
        browser.close()

if __name__ == "__main__":
    napuni_listic_sistem()