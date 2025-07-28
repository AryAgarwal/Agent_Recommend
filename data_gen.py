import json
import random

cuisines = ["Indian", "Chinese", "Italian", "Mexican", "Thai", "American", "Japanese", "French"]
locations = ["Koramangala", "Indiranagar", "MG Road", "Whitefield", "HSR Layout", "Jayanagar", "Marathahalli"]
tags_pool = ["romantic", "family-friendly", "live music", "rooftop", "buffet", "pet-friendly", "fine dining", "casual", "vegan options"]


restaurants = []
for i in range(50):
    restaurants.append({
        "id": i + 1,
        "name": f"Restaurant {i + 1}",
        "cuisine": random.choice(cuisines),
        "location": random.choice(locations),
        "capacity": random.randint(10, 100),
        "tags": random.sample(tags_pool, k=random.randint(1, 3)),
        "rating": round(random.uniform(3.0, 5.0), 1)
    })

with open("restaurants.json", "w") as f:
    json.dump(restaurants, f, indent=2)
