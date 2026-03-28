'''
For Carbon Emission balance
'''
import json
import os
import numpy as np
import math
import pandas as pd
from openai import OpenAI
SUPPLY_VALID_ENTITIES = [
    "Apples", "Bananas", "Barley", "Beef (beef herd)", "Beef (dairy herd)",
    "Beet Sugar", "Berries & Grapes", "Brassicas", "Cane Sugar", "Cassava",
    "Cheese", "Citrus Fruit", "Coffee", "Dark Chocolate", "Eggs",
    "Fish (farmed)", "Groundnuts", "Lamb & Mutton", "Maize", "Milk",
    "Nuts", "Oatmeal", "Olive Oil", "Onions & Leeks", "Other Fruit",
    "Other Pulses", "Other Vegetables", "Palm Oil", "Peas", "Pig Meat",
    "Potatoes", "Poultry Meat", "Rapeseed Oil", "Rice", "Root Vegetables",
    "Shrimps (farmed)", "Soy milk", "Soybean Oil", "Sunflower Oil", "Tofu",
    "Tomatoes", "Wheat & Rye", "Wine"
]

TOP_10_ENTITIES = [
    "Almonds, in shell",
    "Anise, badian, coriander, cumin, caraway, fennel and juniper berries, raw",
    "Apples",
    "Apricots",
    "Barley",
    "Beans, dry",
    "Beef and Buffalo Meat, primary",
    "Butter and Ghee",
    "Butter and ghee of sheep milk",
    "Butter of cow milk",
    "Buttermilk, dry",
    "Cantaloupes and other melons",
    "Cattle fat, unrendered",
    "Cereals, primary",
    "Cheese (All Kinds)",
    "Cheese from milk of goats, fresh or processed",
    "Cheese from milk of sheep, fresh or processed",
    "Citrus Fruit, Total",
    "Cotton lint, ginned",
    "Cotton seed",
    "Cottonseed oil",
    "Edible offal of cattle, fresh, chilled or frozen",
    "Edible offal of goat, fresh, chilled or frozen",
    "Edible offal of sheep, fresh, chilled or frozen",
    "Edible offals of camels and other camelids, fresh, chilled or frozen",
    "Eggs Primary",
    "Fat of camels",
    "Fibre Crops, Fibre Equivalent",
    "Figs",
    "Fruit Primary",
    "Game meat, fresh, chilled or frozen",
    "Goat fat, unrendered",
    "Grapes",
    "Hen eggs in shell, fresh",
    "Linseed",
    "Maize (corn)",
    "Meat of camels, fresh or chilled",
    "Meat of cattle with the bone, fresh or chilled",
    "Meat of chickens, fresh or chilled",
    "Meat of goat, fresh or chilled",
    "Meat of sheep, fresh or chilled",
    "Meat, Poultry",
    "Meat, Total",
    "Milk, Total",
    "Millet",
    "Molasses",
    "Mustard seed",
    "Natural honey",
    "Oil of linseed",
    "Oil of sesame seed",
    "Oilcrops, Cake Equivalent",
    "Oilcrops, Oil Equivalent",
    "Olive oil",
    "Olives",
    "Onions and shallots, dry (excluding dehydrated)",
    "Oranges",
    "Other berries and fruits of the genus vaccinium n.e.c.",
    "Other citrus fruit, n.e.c.",
    "Other fruits, n.e.c.",
    "Other nuts (excluding wild edible nuts and groundnuts), in shell, n.e.c.",
    "Other pulses n.e.c.",
    "Other stimulant, spice and aromatic crops, n.e.c.",
    "Other stone fruits",
    "Other vegetables, fresh n.e.c.",
    "Peaches and nectarines",
    "Pears",
    "Peas, dry",
    "Pistachios, in shell",
    "Plums and sloes",
    "Potatoes",
    "Pulses, Total",
    "Raw cane or beet sugar (centrifugal only)",
    "Raw hides and skins of cattle",
    "Raw hides and skins of goats or kids",
    "Raw hides and skins of sheep or lambs",
    "Raw milk of camel",
    "Raw milk of cattle",
    "Raw milk of goats",
    "Raw milk of sheep",
    "Raw silk (not thrown)",
    "Rice",
    "Roots and Tubers, Total",
    "Seed cotton, unginned",
    "Sesame seed",
    "Sheep and Goat Meat",
    "Sheep fat, unrendered",
    "Shorn wool, greasy, including fleece-washed shorn wool",
    "Silk-worm cocoons suitable for reeling",
    "Skim Milk & Buttermilk, Dry",
    "Skim milk of cows",
    "Soya beans",
    "Sugar Crops Primary",
    "Sugar beet",
    "Sugar cane",
    "Sunflower seed",
    "Sunflower-seed oil, crude",
    "Treenuts, Total",
    "Vegetables Primary",
    "Walnuts, in shell",
    "Watermelons",
    "Wheat",
    "Abaca, manila hemp, raw",
    "Areca nuts",
    "Artichokes",
    "Asparagus",
    "Avocados",
    "Bambara beans, dry",
    "Bananas",
    "Beer of barley, malted",
    "Beeswax",
    "Blueberries",
    "Brazil nuts, in shell",
    "Broad beans and horse beans, dry",
    "Broad beans and horse beans, green",
    "Buckwheat",
    "Buffalo fat, unrendered",
    "Butter of buffalo milk",
    "Cabbages",
    "Canary seed",
    "Carrots and turnips",
    "Cashew nuts, in shell",
    "Cashewapple",
    "Cassava leaves",
    "Cassava, fresh",
    "Castor oil seeds",
    "Cauliflowers and broccoli",
    "Cereals n.e.c.",
    "Cheese from milk of buffalo, fresh or processed",
    "Cheese from skimmed cow milk",
    "Cheese from whole cow milk",
    "Cherries",
    "Chestnuts, in shell",
    "Chick peas, dry",
    "Chicory roots",
    "Chillies and peppers, dry (Capsicum spp., Pimenta spp.), raw",
    "Chillies and peppers, green (Capsicum spp. and Pimenta spp.)",
    "Cinnamon and cinnamon-tree flowers, raw",
    "Cloves (whole stems), raw",
    "Cocoa beans",
    "Coconut oil",
    "Coconuts, in shell",
    "Coffee, green",
    "Coir, raw",
    "Cow peas, dry",
    "Cranberries",
    "Cream, fresh",
    "Cucumbers and gherkins",
    "Currants",
    "Dates",
    "Edible offal of buffalo, fresh, chilled or frozen",
    "Edible offal of pigs, fresh, chilled or frozen",
    "Edible offals of horses and other equines, fresh, chilled or frozen",
    "Edible roots and tubers with high starch or inulin content, n.e.c., fresh",
    "Eggplants (aubergines)",
    "Eggs from other birds in shell, fresh, n.e.c.",
    "Evaporated & Condensed Milk",
    "Fat of pigs",
    "Flax, raw or retted",
    "Fonio",
    "Ghee from cow milk",
    "Ginger, raw",
    "Green corn (maize)",
    "Green garlic",
    "Green tea (not fermented), black tea (fermented) and partly fermented tea, in immediate packings of a content not exceeding 3 kg",
    "Groundnut oil",
    "Groundnuts, excluding shelled",
    "Hazelnuts, in shell",
    "Hop cones",
    "Horse meat, fresh or chilled",
    "Jute, raw or retted",
    "Karite nuts (sheanuts)",
    "Kenaf, and other textile bast fibres, raw or retted",
    "Kiwi fruit",
    "Kola nuts",
    "Leeks and other alliaceous vegetables",
    "Lemons and limes",
    "Lentils, dry",
    "Lettuce and chicory",
    "Locust beans (carobs)",
    "Lupins",
    "Mangoes, guavas and mangosteens",
    "Margarine and shortening",
    "Meat of asses, fresh or chilled",
    "Meat of buffalo, fresh or chilled",
    "Meat of ducks, fresh or chilled",
    "Meat of geese, fresh or chilled",
    "Meat of pig with the bone, fresh or chilled",
    "Meat of pigeons and other birds n.e.c., fresh, chilled or frozen",
    "Meat of rabbits and hares, fresh or chilled",
    "Meat of turkeys, fresh or chilled",
    "Melonseed",
    "Mushrooms and truffles",
    "Natural rubber in primary forms",
    "Nutmeg, mace, cardamoms, raw",
    "Oats",
    "Oil of maize",
    "Oil of palm kernel",
    "Oil palm fruit",
    "Okra",
    "Onions and shallots, green",
    "Other beans, green",
    "Other fibre crops, raw, n.e.c.",
    "Other meat of mammals, fresh or chilled",
    "Other oil seeds, n.e.c.",
    "Other tropical fruits, n.e.c.",
    "Palm kernels",
    "Palm oil",
    "Papayas",
    "Peas, green",
    "Pepper (Piper spp.), raw",
    "Peppermint, spearmint",
    "Pig fat, rendered",
    "Pigeon peas, dry",
    "Pineapples",
    "Plantains and cooking bananas",
    "Pomelos and grapefruits",
    "Pumpkins, squash and gourds",
    "Pyrethrum, dried flowers",
    "Quinces",
    "Rape or colza seed",
    "Rapeseed or canola oil, crude",
    "Raspberries",
    "Raw hides and skins of buffaloes",
    "Raw milk of buffalo",
    "Rye",
    "Safflower seed",
    "Safflower-seed oil, crude",
    "Sisal, raw",
    "Skim milk and whey powder",
    "Skim milk, evaporated",
    "Snails, fresh, chilled, frozen, dried, salted or in brine, except sea snails",
    "Sorghum",
    "Soya bean oil",
    "Spinach",
    "Strawberries",
    "String beans",
    "Sweet potatoes",
    "Tallow",
    "Tangerines, mandarins, clementines",
    "Taro",
    "Tea leaves",
    "Tomatoes",
    "Triticale",
    "Tung nuts",
    "Unmanufactured tobacco",
    "Vanilla, raw",
    "Vetches",
    "Whey, dry",
    "Whole milk powder",
    "Whole milk, condensed",
    "Whole milk, evaporated",
    "Wine",
    "Yams",
    "Yoghurt",
    "Sour cherries",
    "Agave fibres, raw, n.e.c.",
    "Balata, gutta-percha, guayule, chicle and similar natural gums in primary forms or in plates, sheets or strip",
    "Hempseed",
    "Jojoba seeds",
    "Maté leaves",
    "Meat of mules, fresh or chilled",
    "Meat of other domestic camelids, fresh or chilled",
    "Meat of other domestic rodents, fresh or chilled",
    "Mixed grain",
    "Persimmons",
    "Quinoa",
    "Ramie, raw or retted",
    "Skim milk, condensed",
    "True hemp, raw or retted",
    "Whey, condensed",
    "Yautia",
    "Ghee from buffalo milk",
    "Gooseberries",
    "Kapok fibre, raw",
    "Kapok fruit",
    "Kapokseed in shell",
    "Other pome fruits",
    "Other sugar crops n.e.c.",
    "Poppy seed",
    "Tallowtree seeds"
]

API_KEY = 'sk-e43c0370c3f64cdb8d403520e01b09cb'
SUPPLY_SYSTEM_PROMPT = f"""
You are a professional food categorization assistant.
Your ONLY task is to categorize the input food name into the EXACT predefined category list below.
You MUST follow these rules STRICTLY:
1. Output ONLY the complete string of the matched category from the list, NO other content, NO explanation, NO punctuation, NO line breaks, NO quotes.
2. You can ONLY output a category that exists in the predefined list. Do NOT create, modify, or abbreviate any category.
3. Output ONLY ONE single category string, even if multiple categories are partially matched, choose the most suitable one.
4. If the input is not a food, still output the most relevant category from the list.

Predefined category list:
{SUPPLY_VALID_ENTITIES}
"""

TopTen_SYSTEM_PROMPT = f"""
You are a professional food categorization assistant.
Your ONLY task is to categorize the input food name into the EXACT predefined category list below.
You MUST follow these rules STRICTLY:
1. Output ONLY the complete string of the matched category from the list, NO other content, NO explanation, NO punctuation, NO line breaks, NO quotes.
2. You can ONLY output a category that exists in the predefined list. Do NOT create, modify, or abbreviate any category.
3. Output ONLY ONE single category string, even if multiple categories are partially matched, choose the most suitable one.
4. If the input is not a food, still output the most relevant category from the list.

Predefined category list:
{TOP_10_ENTITIES}
"""

def fuzz2top10(food_identity):
    client = OpenAI(
    api_key="sk-4d84e0b6f08749eaaaa1aaf21050df69",
    base_url="https://api.deepseek.com"
)
    response = client.chat.completions.create(
        model="deepseek-chat",  
        messages=[
            {"role": "system", "content": TopTen_SYSTEM_PROMPT},
            {"role": "user", "content": food_identity}
        ],
        temperature=0,  
        stream=False,  
        max_tokens=50   
    )
    result = response.choices[0].message.content.strip()
    return result
def fuzz2supply(food_identity):
    client = OpenAI(
    api_key="sk-4d84e0b6f08749eaaaa1aaf21050df69",
    base_url="https://api.deepseek.com"
)
    response = client.chat.completions.create(
        model="deepseek-chat",  
        messages=[
            {"role": "system", "content": SUPPLY_SYSTEM_PROMPT},
            {"role": "user", "content": food_identity}
        ],
        temperature=0,  
        stream=False,  
        max_tokens=50   
    )
    result = response.choices[0].message.content.strip()
    return result
def haversine(d,cur):
    current_lat = cur[0]
    current_long = cur[1]
    dest_lat = d['lat']
    dest_long = d['long']
    EARTH_RADIUS = 6371.0
    lat1 = math.radians(current_lat)
    lon1 = math.radians(current_long)
    lat2 = math.radians(dest_lat)
    lon2 = math.radians(dest_long)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    haversine_theta = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    central_angle = 2 * math.atan2(math.sqrt(haversine_theta), math.sqrt(1 - haversine_theta))
    distance = EARTH_RADIUS * central_angle
    return distance

def emissions(current_lat, current_long, food_identity, mass):
    total_emissions = 0
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_dir, "country_coordinates.json"), "r", encoding="utf-8") as json_file:
        countries = json.load(json_file)
    with open(os.path.join(_dir, "top_ten.json"), "r", encoding="utf-8") as json_file:
        top_ten = json.load(json_file)
    ten = top_ten[fuzz2top10(food_identity)]
    total = sum(ten.values())
    avg_transport = 0
    factor = (0.02+1+0.175+0.035)/4 # co2 / ton-km
    for k,v in ten.items():
        distance = haversine(countries[k],(current_lat,current_long))
        proportion = v / total
        avg_transport += distance * proportion * factor * mass / 1000
    df = pd.read_csv(os.path.join(_dir, 'food-emissions-supply-chain.csv'))
    target_cols = ['Land use change','Farm','Animal feed','Processing','Retail','Packaging','Losses']
    sums = df[target_cols].sum(axis=1)
    
    total_emissions += mass * sums[df['Entity'] == fuzz2supply(food_identity)].iloc[0]
    return total_emissions + avg_transport
    
print(emissions(22.5455,114.0683,'beef',3))
    

