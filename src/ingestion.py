import os
import pandas as pd
from typing import Tuple
from src.data_generator import generate_synthetic_commodity_data

def parse_agmarknet(filepath: str) -> pd.DataFrame:
    rows = []
    current_market = "Unknown"
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('Arrival Date'):
            start_idx = i + 1
            break
            
    for line in lines[start_idx:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('Market Name :'):
            current_market = line.split(':')[1].strip()
            continue
            
        parts = line.split(',')
        if len(parts) >= 6:
            date_str = parts[0].strip()
            arrival = parts[1].strip()
            modal_price = parts[5].strip()
            
            if not date_str and rows:
                date_str = rows[-1]['date']
                
            try:
                arrival_qty = float(arrival) if arrival else 0.0
                price = float(modal_price) if modal_price else 0.0
                rows.append({
                    'date': date_str,
                    'market': current_market,
                    'modal_price': price,
                    'arrival_qty': arrival_qty
                })
            except ValueError:
                pass
                
    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
    return df.dropna(subset=['date'])

def extract_district(market_name: str, commodity: str) -> str:
    market_name = market_name.lower()
    if commodity == "Onion":
        if any(x in market_name for x in ["nashik", "lasalgaon", "pimpalgaon", "chandwad", "sinner", "yeola", "niphad"]):
            return "Nashik"
        elif any(x in market_name for x in ["pune", "junnar", "manchar", "khed", "baramati"]):
            return "Pune"
        elif any(x in market_name for x in ["solapur", "akluj", "mangwedha", "kurdwadi"]):
            return "Solapur"
        else:
            return "Nashik"
    elif commodity == "Tur":
        if any(x in market_name for x in ["latur", "ausa", "nilanga", "chakur"]):
            return "Latur"
        else:
            return "Latur"
    return "Unknown"

def load_data(commodity: str = "Onion", raw_data_dir: str = "data/raw", force_demo: bool = False) -> Tuple[pd.DataFrame, bool]:
    if force_demo:
        demo_df = generate_synthetic_commodity_data(commodity=commodity)
        return demo_df, True

    file_path = os.path.join(raw_data_dir, f"{commodity.lower()}_mandi_data.csv")
    weather_path = os.path.join(raw_data_dir, "nasa_weather_2026.csv")
    production_path = os.path.join(raw_data_dir, "crop_production_data.csv")
    
    if os.path.exists(file_path):
        try:
            df = parse_agmarknet(file_path)
            df['commodity'] = commodity
            df['state'] = 'Maharashtra'
            df['district'] = df['market'].apply(lambda m: extract_district(m, commodity))
            
            if os.path.exists(weather_path):
                w_df = pd.read_csv(weather_path)
                w_df['Price Date'] = pd.to_datetime(w_df['Price Date'])
                w_df = w_df.rename(columns={
                    'District Name': 'district',
                    'Price Date': 'date'
                })
                # Drop daily_rainfall_mm etc, keep only what we need to avoid clutter
                cols_to_keep = ['district', 'date', 'rainfall_7d_mm', 'temp_max_7d_avg', 'humidity_7d_avg']
                w_df = w_df[[c for c in cols_to_keep if c in w_df.columns]]
                df = pd.merge(df, w_df, on=['district', 'date'], how='left')
            else:
                df['rainfall_7d_mm'] = 0.0
                df['temp_max_7d_avg'] = 30.0
                df['humidity_7d_avg'] = 50.0
                
            if os.path.exists(production_path):
                p_df = pd.read_csv(production_path)
                p_df = p_df[p_df['Crop'] == commodity]
                p_df = p_df.rename(columns={'District': 'district', 'Production (Tonnes)': 'production_tonnes'})
                df = pd.merge(df, p_df[['district', 'production_tonnes']], on='district', how='left')
            else:
                df['production_tonnes'] = 0.0

            df['rainfall_7d_mm'] = df['rainfall_7d_mm'].fillna(0.0)
            df['temp_max_7d_avg'] = df['temp_max_7d_avg'].fillna(30.0)
            df['humidity_7d_avg'] = df['humidity_7d_avg'].fillna(50.0)
            df['production_tonnes'] = df['production_tonnes'].fillna(0.0)

            return df.sort_values('date').reset_index(drop=True), False
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[INGESTION WARNING] Failed to read {file_path}: {e}. Falling back to demo data.")
            
    demo_df = generate_synthetic_commodity_data(commodity=commodity)
    return demo_df, True
