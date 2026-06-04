# hw_08_streamlit — Weather Dashboard

Streamlit weather dashboard a 8. házihoz

## Funkciók

-  **Geocoding**: városnév → lat/lon (Open-Meteo Geocoding API)
-  **Aktuális adatok**: hőmérséklet, érzett hőmérséklet, páratartalom, szélsebesség
-  **7 napos előrejelzés**: hőmérséklet + páratartalom (dual-axis), szélsebesség, csapadékvalószínűség
-  **SQLite naplózás**: minden keresés mentve (városnév, temp, humidity, wind, datetime)
- **Hibakezelés**: warning üzenet, ha API hibát dob

## Futtatás lokálisan

```bash
pip install -r requirements.txt  
streamlit run weather_app.py
```

## Deployment

Az app a Streamlit Community Cloud-on fut:  

## Struktúra

```
hw_08_streamlit/
├── weather_app.py      # Fő alkalmazás
├── requirements.txt    # Függőségek
└── README.md
```

## API-k

- https://geocoding-api.open-meteo.com/v1/search
- https://api.open-meteo.com/v1/forecast
