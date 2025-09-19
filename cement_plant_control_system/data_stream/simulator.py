import random, time, json, datetime

def generate_plant_data():
    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "raw_mix_lime": round(random.uniform(62, 67), 2),
        "raw_mix_silica": round(random.uniform(20, 23), 2),
        "raw_mix_alumina": round(random.uniform(5, 7), 2),
        "raw_mix_iron": round(random.uniform(2.5, 3.5), 2),
        "kiln_temp": round(random.uniform(1400, 1500), 1),
        "kiln_speed": round(random.uniform(4, 5), 2),
        "grinding_power": round(random.uniform(25, 30), 2),
        "fuel_mix": {"coal": random.randint(60, 80), "AF": random.randint(20, 40)},
        "emissions": {"CO2": random.randint(800, 900), "NOx": random.randint(400, 500)}
    }

if __name__ == "__main__":
    while True:
        print(json.dumps(generate_plant_data()), flush=True)
        time.sleep(2)  # every 2 sec
