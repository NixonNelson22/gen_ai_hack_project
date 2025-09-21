import random, time, json, datetime

def generate_plant_data():
    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "TSR_Target_Percentage": round(random.uniform(25, 35), 2),
        "AF_Fuel_Flow_Setpoint": round(random.uniform(5, 10), 2),
        "Fossil_Fuel_Flow_SP": round(random.uniform(10, 15), 2),
        "Fuel_Calorific_Value": round(random.uniform(4000, 5000), 2),
        "Burning_Zone_Temp_SP": round(random.uniform(1350, 1550), 2),
        "Primary_Air_Flow_SP": round(random.uniform(10, 15), 2),
        "Secondary_Air_Flow_SP": round(random.uniform(20, 30), 2),
        "Tertiary_Air_Flow_SP": round(random.uniform(5, 10), 2),
        "Kiln_Speed_Setpoint": round(random.uniform(4, 5), 2),
        "Oxygen_Concentration_SP": round(random.uniform(1, 3), 2),
        "CO_Emission_Limit_SP": round(random.uniform(800, 900), 2),
        "NOx_Emission_Limit_SP": round(random.uniform(400, 500), 2),
        "Flame_Temperature_SP": round(random.uniform(1800, 2000), 2),
        "Waste_Gas_Temperature_SP": round(random.uniform(300, 400), 2),
        "kiln_temp": round(random.uniform(1400, 1500), 1),
        "kiln_speed": round(random.uniform(4, 5), 2),
        "emissions": {"CO2": random.randint(800, 900), "NOx": random.randint(400, 500)}
    }

if __name__ == "__main__":
    while True:
        print(json.dumps(generate_plant_data()), flush=True)
        time.sleep(2)  # every 2 sec
