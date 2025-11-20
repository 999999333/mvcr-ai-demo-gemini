# MVCR AI Demo - Streamlit Chatbot

Chatbot aplikace využívající Gemini API s File Search funkcionalitou pro odpovídání na otázky založené na indexovaných dokumentech.

## Funkce

- 💬 Multi-turn konverzace (chatbot styl)
- 🔍 Odpovědi pouze na základě indexovaných dokumentů
- 🇨🇿 Odpovědi v češtině
- 📚 Zobrazení zdrojů pro každou odpověď
- 🗑️ Možnost vymazat historii chatu

## Instalace

1. Ujistěte se, že máte nainstalovaný Python 3.8 nebo novější

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

## Příprava dat

Před spuštěním aplikace je potřeba nahrát dokumenty do File Search Store:

```bash
python upload_file_search_store.py
```

Tento skript vytvoří soubor `file_search_store_name.txt`, který obsahuje název vašeho File Search Store.

## Spuštění aplikace

```bash
streamlit run streamlit_app.py
```

Aplikace se otevře ve vašem prohlížeči na adrese `http://localhost:8501`

## Použití

1. **Položte otázku:** Zadejte svou otázku do textového pole
2. **Získejte odpověď:** Asistent odpoví pouze na základě indexovaných dokumentů
3. **Zobrazte zdroje:** Klikněte na "📚 Zobrazit zdroje" pro zobrazení dokumentů použitých pro odpověď
4. **Pokračujte v konverzaci:** Můžete klást další otázky, kontext předchozích otázek je zachován
5. **Vymazat historii:** Použijte tlačítko "🗑️ Vymazat historii chatu" v postranním panelu

## Poznámky

- Aplikace odpovídá **POUZE** na základě indexovaných dokumentů
- Pokud informace nejsou v dokumentech, asistent to oznámí
- Všechny odpovědi jsou v českém jazyce
- API klíč je možné nastavit pomocí proměnné prostředí `GEMINI_API_KEY`

## Struktura projektu

```
.
├── streamlit_app.py              # Hlavní Streamlit aplikace
├── upload_file_search_store.py   # Skript pro nahrání dokumentů
├── llm.py                         # Příklad použití Gemini API
├── requirements.txt               # Python závislosti
├── file_search_store_name.txt    # Název File Search Store (generovaný)
├── files_metadata.csv             # Metadata dokumentů
└── source_files/                  # Složka s dokumenty k nahrání
```
