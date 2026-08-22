import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.weather_service import fetch_live_weather_and_history
from backend.prediction_service import prediction_service

KARNATAKA_LOCATIONS = [
    # --- Mysuru & Old Mysore Region ---
    {"name": "Mysuru City", "district": "Mysuru", "type": "District HQ", "lat": 12.2958, "lon": 76.6394},
    {"name": "Nanjangud", "district": "Mysuru", "type": "Taluk", "lat": 12.1194, "lon": 76.6803},
    {"name": "Hunsur", "district": "Mysuru", "type": "Taluk", "lat": 12.3082, "lon": 76.2925},
    {"name": "T. Narasipura", "district": "Mysuru", "type": "Taluk", "lat": 12.2131, "lon": 76.9038},
    {"name": "Periyapatna", "district": "Mysuru", "type": "Taluk", "lat": 12.3389, "lon": 76.0967},
    {"name": "K.R. Nagar", "district": "Mysuru", "type": "Taluk", "lat": 12.4414, "lon": 76.3814},
    {"name": "H.D. Kote", "district": "Mysuru", "type": "Taluk", "lat": 12.0864, "lon": 76.3267},

    # --- Mandya District ---
    {"name": "Mandya City", "district": "Mandya", "type": "District HQ", "lat": 12.5218, "lon": 76.8951},
    {"name": "Srirangapatna", "district": "Mandya", "type": "Taluk", "lat": 12.4237, "lon": 76.6830},
    {"name": "Maddur", "district": "Mandya", "type": "Taluk", "lat": 12.5847, "lon": 77.0433},
    {"name": "Malavalli", "district": "Mandya", "type": "Taluk", "lat": 12.3861, "lon": 77.0544},
    {"name": "Pandavapura", "district": "Mandya", "type": "Taluk", "lat": 12.4947, "lon": 76.6711},
    {"name": "Nagamangala", "district": "Mandya", "type": "Taluk", "lat": 12.8189, "lon": 76.7583},

    # --- Hassan District ---
    {"name": "Hassan City", "district": "Hassan", "type": "District HQ", "lat": 13.0033, "lon": 76.1004},
    {"name": "Sakleshpur", "district": "Hassan", "type": "Taluk/Malnad", "lat": 12.9719, "lon": 75.7842},
    {"name": "Belur", "district": "Hassan", "type": "Taluk", "lat": 13.1611, "lon": 75.8647},
    {"name": "Channarayapatna", "district": "Hassan", "type": "Taluk", "lat": 12.9064, "lon": 76.3917},
    {"name": "Holenarasipura", "district": "Hassan", "type": "Taluk", "lat": 12.7881, "lon": 76.2411},

    # --- Chamarajanagar District ---
    {"name": "Chamarajanagar", "district": "Chamarajanagar", "type": "District HQ", "lat": 11.9261, "lon": 76.9437},
    {"name": "Gundlupet", "district": "Chamarajanagar", "type": "Taluk", "lat": 11.8089, "lon": 76.6897},
    {"name": "Kollegal", "district": "Chamarajanagar", "type": "Taluk", "lat": 12.1583, "lon": 77.1083},
    {"name": "Hanur", "district": "Chamarajanagar", "type": "Taluk", "lat": 12.0917, "lon": 77.3000},

    # --- Kodagu District ---
    {"name": "Madikeri", "district": "Kodagu", "type": "District HQ", "lat": 12.4244, "lon": 75.7382},
    {"name": "Virajpet", "district": "Kodagu", "type": "Taluk", "lat": 12.1972, "lon": 75.8089},
    {"name": "Somwarpet", "district": "Kodagu", "type": "Taluk", "lat": 12.5986, "lon": 75.8631},
    {"name": "Kushalnagar", "district": "Kodagu", "type": "Taluk", "lat": 12.4561, "lon": 75.9619},

    # --- Bengaluru & Surrounding Region ---
    {"name": "Bengaluru Urban", "district": "Bengaluru Urban", "type": "Capital City", "lat": 12.9716, "lon": 77.5946},
    {"name": "Yelahanka", "district": "Bengaluru Urban", "type": "Taluk", "lat": 13.1007, "lon": 77.5963},
    {"name": "Electronic City", "district": "Bengaluru Urban", "type": "Zone", "lat": 12.8399, "lon": 77.6770},
    {"name": "Doddaballapura", "district": "Bengaluru Rural", "type": "Taluk", "lat": 13.2974, "lon": 77.5393},
    {"name": "Devanahalli", "district": "Bengaluru Rural", "type": "Taluk", "lat": 13.2483, "lon": 77.7126},
    {"name": "Hoskote", "district": "Bengaluru Rural", "type": "Taluk", "lat": 13.0694, "lon": 77.7981},
    {"name": "Ramanagara", "district": "Ramanagara", "type": "District HQ", "lat": 12.7209, "lon": 77.2799},
    {"name": "Channapatna", "district": "Ramanagara", "type": "Taluk", "lat": 12.6517, "lon": 77.2089},
    {"name": "Kanakapura", "district": "Ramanagara", "type": "Taluk", "lat": 12.5447, "lon": 77.4194},

    # --- Coastal Karnataka (Karavali) ---
    {"name": "Mangaluru", "district": "Dakshina Kannada", "type": "District HQ", "lat": 12.9141, "lon": 74.8560},
    {"name": "Bantwal", "district": "Dakshina Kannada", "type": "Taluk", "lat": 12.8947, "lon": 75.0347},
    {"name": "Puttur", "district": "Dakshina Kannada", "type": "Taluk", "lat": 12.7661, "lon": 75.2047},
    {"name": "Belthangady", "district": "Dakshina Kannada", "type": "Taluk", "lat": 12.9931, "lon": 75.2975},
    {"name": "Sullia", "district": "Dakshina Kannada", "type": "Taluk", "lat": 12.5600, "lon": 75.3900},
    {"name": "Udupi City", "district": "Udupi", "type": "District HQ", "lat": 13.3409, "lon": 74.7421},
    {"name": "Kundapura", "district": "Udupi", "type": "Taluk", "lat": 13.6267, "lon": 74.6908},
    {"name": "Karkala", "district": "Udupi", "type": "Taluk", "lat": 13.2167, "lon": 74.9833},
    {"name": "Karwar", "district": "Uttara Kannada", "type": "District HQ", "lat": 14.8185, "lon": 74.1297},
    {"name": "Sirsi", "district": "Uttara Kannada", "type": "Taluk/Malnad", "lat": 14.6194, "lon": 74.8356},
    {"name": "Bhatkal", "district": "Uttara Kannada", "type": "Taluk", "lat": 13.9856, "lon": 74.5539},
    {"name": "Kumta", "district": "Uttara Kannada", "type": "Taluk", "lat": 14.4253, "lon": 74.4172},

    # --- Malnad & Central Karnataka ---
    {"name": "Shivamogga", "district": "Shivamogga", "type": "District HQ", "lat": 13.9299, "lon": 75.5681},
    {"name": "Sagar", "district": "Shivamogga", "type": "Taluk", "lat": 14.1667, "lon": 75.0333},
    {"name": "Thirthahalli", "district": "Shivamogga", "type": "Taluk", "lat": 13.6961, "lon": 75.2428},
    {"name": "Bhadravathi", "district": "Shivamogga", "type": "Taluk", "lat": 13.8436, "lon": 75.7033},
    {"name": "Chikkamagaluru", "district": "Chikkamagaluru", "type": "District HQ", "lat": 13.3161, "lon": 75.7720},
    {"name": "Tarikere", "district": "Chikkamagaluru", "type": "Taluk", "lat": 13.7083, "lon": 75.8139},
    {"name": "Kadur", "district": "Chikkamagaluru", "type": "Taluk", "lat": 13.5544, "lon": 76.0125},
    {"name": "Mudigere", "district": "Chikkamagaluru", "type": "Taluk", "lat": 13.1367, "lon": 75.6419},
    {"name": "Sringeri", "district": "Chikkamagaluru", "type": "Taluk", "lat": 13.4189, "lon": 75.2575},
    {"name": "Davanagere", "district": "Davanagere", "type": "District HQ", "lat": 14.4644, "lon": 75.9218},
    {"name": "Harihar", "district": "Davanagere", "type": "Taluk", "lat": 14.5161, "lon": 75.8028},
    {"name": "Chitradurga", "district": "Chitradurga", "type": "District HQ", "lat": 14.2254, "lon": 76.3980},
    {"name": "Hiriyur", "district": "Chitradurga", "type": "Taluk", "lat": 13.9472, "lon": 76.6214},

    # --- North-West Karnataka (Mumbai Karnataka) ---
    {"name": "Belagavi City", "district": "Belagavi", "type": "District HQ", "lat": 15.8497, "lon": 74.4977},
    {"name": "Chikkodi", "district": "Belagavi", "type": "Taluk", "lat": 16.4297, "lon": 74.5967},
    {"name": "Gokak", "district": "Belagavi", "type": "Taluk", "lat": 16.1683, "lon": 74.8272},
    {"name": "Athani", "district": "Belagavi", "type": "Taluk", "lat": 16.7314, "lon": 75.0600},
    {"name": "Bailhongal", "district": "Belagavi", "type": "Taluk", "lat": 15.8206, "lon": 74.8586},
    {"name": "Dharwad City", "district": "Dharwad", "type": "District HQ", "lat": 15.4589, "lon": 75.0078},
    {"name": "Hubballi", "district": "Dharwad", "type": "Major City", "lat": 15.3647, "lon": 75.1240},
    {"name": "Gadag City", "district": "Gadag", "type": "District HQ", "lat": 15.4319, "lon": 75.6319},
    {"name": "Ron", "district": "Gadag", "type": "Taluk", "lat": 15.6989, "lon": 75.7333},
    {"name": "Haveri City", "district": "Haveri", "type": "District HQ", "lat": 14.7958, "lon": 75.3986},
    {"name": "Ranebennur", "district": "Haveri", "type": "Taluk", "lat": 14.6225, "lon": 75.6264},
    {"name": "Vijayapura", "district": "Vijayapura", "type": "District HQ", "lat": 16.8302, "lon": 75.7100},
    {"name": "Indi", "district": "Vijayapura", "type": "Taluk", "lat": 17.1772, "lon": 75.9619},
    {"name": "Bagalkote", "district": "Bagalkote", "type": "District HQ", "lat": 16.1853, "lon": 75.6961},
    {"name": "Badami", "district": "Bagalkote", "type": "Taluk", "lat": 15.9189, "lon": 75.6797},
    {"name": "Jamkhandi", "district": "Bagalkote", "type": "Taluk", "lat": 16.5161, "lon": 75.2975},

    # --- Kalyana-Karnataka (Hyderabad Karnataka) ---
    {"name": "Kalaburagi", "district": "Kalaburagi", "type": "District HQ", "lat": 17.3297, "lon": 76.8343},
    {"name": "Aland", "district": "Kalaburagi", "type": "Taluk", "lat": 17.5647, "lon": 76.5683},
    {"name": "Ballari City", "district": "Ballari", "type": "District HQ", "lat": 15.1394, "lon": 76.9214},
    {"name": "Hosapete", "district": "Vijayanagara", "type": "District HQ", "lat": 15.2689, "lon": 76.3908},
    {"name": "Hampi", "district": "Vijayanagara", "type": "Heritage Zone", "lat": 15.3350, "lon": 76.4600},
    {"name": "Yadgir", "district": "Yadgir", "type": "District HQ", "lat": 16.7686, "lon": 77.1378},
    {"name": "Shahapur", "district": "Yadgir", "type": "Taluk", "lat": 16.6972, "lon": 76.8419},
    {"name": "Raichur City", "district": "Raichur", "type": "District HQ", "lat": 16.2076, "lon": 77.3463},
    {"name": "Sindhanur", "district": "Raichur", "type": "Taluk", "lat": 15.7761, "lon": 76.7583},
    {"name": "Bidar City", "district": "Bidar", "type": "District HQ", "lat": 17.9104, "lon": 77.5199},
    {"name": "Basavakalyan", "district": "Bidar", "type": "Taluk", "lat": 17.8731, "lon": 76.9478},
    {"name": "Koppal City", "district": "Koppal", "type": "District HQ", "lat": 15.3508, "lon": 76.1550},
    {"name": "Gangavathi", "district": "Koppal", "type": "Taluk", "lat": 15.4333, "lon": 76.5333},
]


def generate_karnataka_predictions() -> List[Dict[str, Any]]:
    """
    Computes real-time XGBoost ML rainfall & weather predictions across all 31 districts,
    taluks, and agricultural regions in Karnataka.
    """
    print("\n==================================================")
    print("GENERATING COMPLETE KARNATAKA ML WEATHER & RAINFALL PREDICTIONS")
    print(f"Total Locations Covered: {len(KARNATAKA_LOCATIONS)}")
    print("==================================================")

    results = []

    for loc in KARNATAKA_LOCATIONS:
        try:
            df, current_weather = fetch_live_weather_and_history(loc["lat"], loc["lon"])
            res = prediction_service.predict_current_and_hourly(df)
            pred = res["prediction"]

            loc_result = {
                "name": loc["name"],
                "district": loc["district"],
                "type": loc["type"],
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "temperature": round(current_weather["temperature"], 1),
                "humidity": round(current_weather["humidity"], 1),
                "pressure": round(current_weather["pressure"], 1),
                "wind_speed": round(current_weather["wind_speed"], 1),
                "cloud_cover": round(current_weather["cloud_cover"], 1),
                "rain_probability": pred["rain_probability"],
                "rain_prediction": pred["rain_prediction"],
                "expected_rainfall_mm": pred["expected_rainfall_mm"],
                "risk_level": pred["risk_level"],
                "open_meteo_probability": pred["open_meteo_probability"]
            }
            results.append(loc_result)
            print(f"  [OK] {loc['name']:<20} ({loc['district']:<18}): {pred['rain_probability']:>5.1f}% Rain Prob | {pred['expected_rainfall_mm']:>4.2f} mm | Risk: {pred['risk_level']}")
        except Exception as e:
            print(f"  [FAIL] Failed for {loc['name']}: {e}")

    # Save output to reports/karnataka_predictions.json
    output_path = "reports/karnataka_predictions.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print("\nSaved Karnataka results to:", output_path)
    print("==================================================\n")
    return results


if __name__ == "__main__":
    results = generate_karnataka_predictions()
    df_res = pd.DataFrame(results)
    df_res = df_res.sort_values(by="rain_probability", ascending=False)

    print("\nKARNATAKA DISTRICT & TALUK RAINFALL LEADERBOARD (SORTED BY RAIN PROBABILITY):")
    print(f"{'Location':<20} {'District':<18} {'Type':<14} {'Temp (°C)':<10} {'Humidity (%)':<14} {'Rain Prob (%)':<14} {'Expected mm':<12} {'Risk Level':<10}")
    print("-" * 112)
    for _, row in df_res.iterrows():
        print(f"{row['name']:<20} {row['district']:<18} {row['type']:<14} {row['temperature']:<10.1f} {row['humidity']:<14.1f} {row['rain_probability']:<14.1f} {row['expected_rainfall_mm']:<12.2f} {row['risk_level']:<10}")
