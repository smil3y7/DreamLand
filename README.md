# 🌙 DreamLand MVP

**DreamLand** je minimalno delujoča verzija aplikacije za beleženje sanj in vizualizacijo vašega "sveta sanj" kot interaktivne karte.

## ✨ Funkcionalnosti MVP

- 📝 **Vnos sanj** - Dodajanje novih sanj z datumom, ciklom in vsebino
- 🤖 **AI ekstrakcija** - Avtomatična ekstrakcija lokacij, entitet in tranzitov (OpenAI)
- 🗺️ **Interaktivna karta** - D3.js vizualizacija vašega sveta sanj
- 🔍 **Zoom & Pan** - Raziskovanje karte z zoomom in premikanjem
- 🎨 **Sloji** - Prikaz različnih slojev (primarni, zgornji, spodnji svet)
- 🌐 **Dvojezičnost** - Preklapljanje med angleščino in slovenščino
- 💾 **Export** - JSON export celotnega sveta
- ✏️ **Edit mode** - Ročno premikanje lokacij na karti

## 🚀 Hitra Namestitev

### Predpogoji

- Python 3.10+
- Node.js 18+
- (Opcijsko) OpenAI API ključ

### Backend Setup

```bash
# Pojdi v backend direktorij
cd backend

# Ustvari virtual environment
python -m venv venv

# Aktiviraj virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Namesti odvisnosti
pip install -r requirements.txt

# Kopiraj .env.example v .env
cp .env.example .env

# Uredi .env in dodaj svoj OpenAI API ključ (opcijsko)
# Če ne dodaš ključa, bo uporabljal stub funkcije za testiranje

# Inicializiraj bazo podatkov
python init_db.py

# Zaženi server
python main.py
```

Backend bo tekel na `http://localhost:8000`

### Frontend Setup

```bash
# Pojdi v frontend direktorij
cd frontend

# Namesti odvisnosti
npm install

# Zaženi development server
npm run dev
```

Frontend bo tekel na `http://localhost:5173`

## 📁 Struktura Projekta

```
dreamland/
├── backend/
│   ├── .env.example          # Primer konfiguracije
│   ├── requirements.txt      # Python odvisnosti
│   ├── database.py           # SQLAlchemy konfiguracija
│   ├── models.py             # Database modeli
│   ├── schemas.py            # Pydantic schemas
│   ├── crud.py               # CRUD operacije
│   ├── llm.py                # OpenAI integracija
│   ├── tasks.py              # Async background tasks
│   ├── main.py               # FastAPI aplikacija
│   └── init_db.py            # Database inicializacija
│
└── frontend/
    ├── package.json          # Node odvisnosti
    ├── vite.config.js        # Vite konfiguracija
    ├── tailwind.config.js    # Tailwind konfiguracija
    ├── index.html            # HTML entry point
    └── src/
        ├── main.jsx          # React entry point
        ├── App.jsx           # Glavna komponenta
        ├── lib/
        │   ├── api.js        # API client
        │   └── i18n.js       # Internacionalizacija
        └── components/
            ├── DreamInput.jsx      # Obrazec za vnos sanj
            ├── DreamList.jsx       # Seznam sanj
            ├── WorldMap.jsx        # Interaktivna karta
            ├── LocationPopup.jsx   # Popup z detajli lokacije
            └── LanguageToggle.jsx  # Preklopnik jezika
```

## 🎯 Uporaba

### 1. Dodajanje sanj

1. V levem panelu vnesi datum, cikel (če je več ciklov v eni noči) in vsebino sanj
2. Klikni "Save Dream"
3. Backend bo avtomatsko procesiral sanje in ekstrahiral lokacije, entitete in tranzite

### 2. Raziskovanje karte

- **Zoom**: Uporabi gumbe + / - ali scroll kolesce
- **Pan**: Klikni in povleci ozadje
- **Reset**: Klikni gumb za reset pogleda
- **Sloji**: Izberi primarni, zgornji ali spodnji svet
- **Klik na mehurček**: Odpre popup z detajli lokacije

### 3. Edit mode

1. Klikni gumb ✏️ za vklop edit mode
2. Povleci mehurčke na nove pozicije
3. Pozicije se avtomatsko shranjujejo

### 4. Preklop jezika

Klikni na gumb Globe v zgornjem desnem kotu za preklop med EN in SI.

## 🔧 API Endpoints

### Dreams

- `POST /api/dreams` - Ustvari novo sanje
- `GET /api/dreams` - Pridobi vse sanje
- `GET /api/dreams/{id}` - Pridobi specifične sanje

### Locations

- `GET /api/locations` - Pridobi vse lokacije
- `GET /api/locations?layer=PRIMARY` - Filtriraj po sloju
- `POST /api/locations` - Ustvari novo lokacijo
- `PATCH /api/locations/{id}` - Posodobi lokacijo
- `POST /api/locations/merge` - Združi več lokacij

### Entities

- `GET /api/entities` - Pridobi vse entitete
- `GET /api/entities?location_id=1` - Filtriraj po lokaciji
- `POST /api/entities` - Ustvari novo entiteto

### Stats & Export

- `GET /api/stats` - Pridobi statistiko
- `GET /api/export` - Exportaj celoten svet kot JSON

## 🤖 OpenAI Integracija

Če imaš OpenAI API ključ:

1. Uredi `.env` v backend direktoriju
2. Nastavi `OPENAI_API_KEY=sk-...`
3. (Opcijsko) Nastavi model: `OPENAI_MODEL=gpt-4-turbo-preview`

Če ključa nimaš, bo aplikacija delovala s stub funkcijami, ki vrnejo osnovne ekstrakcije na podlagi ključnih besed.

## 🌍 Sloji Sveta

- **PRIMARY (0)** - Običajen, "realen" svet v sanjah
- **UPPER (+1)** - Višje ravni, nebo, duhovne dimenzije
- **LOWER (-1)** - Podzemlje, vode, podzemna mesta

## 🎨 Barvni Sistemi

Lokacije imajo avtomatske barve glede na arhetipu:
- 🏠 Dom - Modra (#3b82f6)
- 🌲 Gozd - Zelena (#22c55e)
- 🏙️ Mesto - Indigo (#6366f1)
- 🌊 Voda - Cyan (#06b6d4)
- 🕳️ Jama - Siva (#78716c)

## 🔐 Varnost

MVP uporablja osnovno varnost:
- CORS zaščita
- `.env` za občutljive podatke
- SQLite za lokalno shranjevanje

Za produkcijo priporočamo:
- PostgreSQL namesto SQLite
- Pravilno autentikacijo
- HTTPS
- Rate limiting

## 📊 Testni Podatki

Pri inicializaciji lahko dodaš testne podatke za hitro testiranje funkcionalnosti.

```bash
python init_db.py
# Ko vpraša "Create sample data? (y/n):", vnesi 'y'
```

## 🐛 Troubleshooting

### Backend ne štarta

```bash
# Preveri če je virtual environment aktiviran
# Preveri če so vse odvisnosti nameščene
pip install -r requirements.txt
```

### Frontend ne štarta

```bash
# Preveri Node.js verzijo
node --version  # Mora biti 18+

# Izbriši node_modules in ponovno namesti
rm -rf node_modules
npm install
```

### OpenAI napake

- Preveri če je API ključ pravilen v `.env`
- Preveri kvote na OpenAI računu
- Aplikacija bo delovala tudi brez ključa (stub mode)

## 🚧 Napredne Funkcije (za prihodnost)

- [ ] Redis/RQ za produkcijo async tasks
- [ ] PostgreSQL za produkcijo
- [ ] User authentication
- [ ] Collaborative dreams
- [ ] AI predlogi za merge lokacij
- [ ] Advanced analytics
- [ ] Mobile app (PWA ready)
- [ ] Export to PDF/Image

## 📝 License

MIT License - uporabi prosto za osebne projekte!

## 🙏 Zahvale

Projekt uporablja:
- FastAPI - Backend framework
- React - Frontend framework
- D3.js - Vizualizacija
- OpenAI - AI ekstrakcija
- Tailwind CSS - Styling

---

**Ustvarjeno za DreamLand MVP projekt 🌙**