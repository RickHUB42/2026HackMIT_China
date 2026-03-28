import pandas as pd
import requests
import string

def get_num(text):
    non_digits = ''.join([c for c in string.printable if not c.isdigit()])
    result = text.translate(str.maketrans('', '', non_digits))
    return result
class deepseek_assist_food():
    def __init__(self):
        self.API_KEY = "sk-e43c0370c3f64cdb8d403520e01b09cb"
        self.url = "https://api.deepseek.com/chat/completions"

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_KEY}"
        }
    def use_deepseek(self,prompt):
        data = {
            "model": "deepseek-reasoner",
            "messages": [
                {"role": "system", "content": "You are a professional assistant specializing in food science"},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            return (result['choices'][0]['message']['content'])
        else:
            return ("Request failed, error code:", response.status_code)

class deepseek_assist_ingredient():
    def __init__(self):
        self.API_KEY = "sk-e43c0370c3f64cdb8d403520e01b09cb"
        self.url = "https://api.deepseek.com/chat/completions"

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_KEY}"
        }

    def use_deepseek(self, prompt):
        data = {
            "model": "deepseek-reasoner",
            "messages": [
                {"role": "system", "content": "You are a professional assistant who specializes in food ingredients and is flexible"},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            return (result['choices'][0]['message']['content'])
        else:
            return ("Request failed, error code:", response.status_code)

class Food():
    def __init__(self, vitamin_a_content, vitamin_c_content, vitamin_e_content, vitamin_k_content, thiamin_content,
                 riboflavin_content, niacin_content, vitamin_b6_content, folate_content, vitamin_b12_content,
                 pantothenic_acid_content, biotin_content, choline_content, ca_content, cho_content, protein_content,
                 cu_content, i_content, fe_content, mg_content, mn_content, p_content, se_content, zn_content, fat_content):
        self.vitamin_a_content = vitamin_a_content
        self.vitamin_c_content = vitamin_c_content
        self.vitamin_e_content = vitamin_e_content
        self.vitamin_k_content = vitamin_k_content
        self.thiamin_content = thiamin_content
        self.riboflavin_content = riboflavin_content
        self.niacin_content = niacin_content
        self.vitamin_b6_content = vitamin_b6_content
        self.folate_content = folate_content
        self.vitamin_b12_content = vitamin_b12_content
        self.pantothenic_acid_content = pantothenic_acid_content
        self.biotin_content = biotin_content
        self.choline_content = choline_content
        self.ca_content = ca_content
        self.cho_content = cho_content
        self.protein_content = protein_content
        self.cu_content = cu_content
        self.i_content = i_content
        self.fe_content = fe_content
        self.mg_content = mg_content
        self.mn_content = mn_content
        self.p_content = p_content
        self.se_content = se_content
        self.zn_content = zn_content
        self.fat_content = fat_content

    def __add__(self, other):
        if not isinstance(other, Food):
            return NotImplemented
        return Food(
            vitamin_a_content=self.vitamin_a_content + other.vitamin_a_content,
            vitamin_c_content=self.vitamin_c_content + other.vitamin_c_content,
            vitamin_e_content=self.vitamin_e_content + other.vitamin_e_content,
            vitamin_k_content=self.vitamin_k_content + other.vitamin_k_content,
            thiamin_content=self.thiamin_content + other.thiamin_content,
            riboflavin_content=self.riboflavin_content + other.riboflavin_content,
            niacin_content=self.niacin_content + other.niacin_content,
            vitamin_b6_content=self.vitamin_b6_content + other.vitamin_b6_content,
            folate_content=self.folate_content + other.folate_content,
            vitamin_b12_content=self.vitamin_b12_content + other.vitamin_b12_content,
            pantothenic_acid_content=self.pantothenic_acid_content + other.pantothenic_acid_content,
            biotin_content=self.biotin_content + other.biotin_content,
            choline_content=self.choline_content + other.choline_content,
            ca_content=self.ca_content + other.ca_content,
            cho_content=self.cho_content + other.cho_content,
            protein_content=self.protein_content + other.protein_content,
            cu_content=self.cu_content + other.cu_content,
            i_content=self.i_content + other.i_content,
            fe_content=self.fe_content + other.fe_content,
            mg_content=self.mg_content + other.mg_content,
            mn_content=self.mn_content + other.mn_content,
            p_content=self.p_content + other.p_content,
            se_content=self.se_content + other.se_content,
            zn_content=self.zn_content + other.zn_content,
            fat_content=self.fat_content + other.fat_content
        )

emission_ingredients = pd.read_csv('/Users/andrew/Downloads/ghg-per-kg-poore.csv')
emission_ingredients['Entity'] = emission_ingredients['Entity'].str.lower()
ingredient_types = ('; ').join(emission_ingredients['Entity'].tolist())
foods_nutrient_content = {}
for ingredient in emission_ingredients['Entity']:
    foods_nutrient_content[ingredient] = Food(*([0]*25)) #placeholder, havent calculated nutrients yet
deepseek_assistant = deepseek_assist_food()
deepseek_ingredient_approximator = deepseek_assist_ingredient()
def get_most_similar_ingredient(raw_ingredient):
    ingredient = deepseek_assistant.use_deepseek(('Which ingredient of the following: '+ingredient_types+', is the ingredient '+raw_ingredient+' most similar to? Reply only the name of the similar ingredient, no punctuation or anything else, all lower case'))
    return ingredient
def food_emissions(food): #food is a dict
    tot_emissions = 0
    for ingredient,weight in food.items():
        ingredient = get_most_similar_ingredient(ingredient)
        tot_emissions += weight*emission_ingredients[ingredient.strip().lower()]
    return tot_emissions
class Food_Logger():
    def __init__(self):
        self.food_dic = Food(*([0]*25)) #the recipe stuff, with nutrients, etc.
        self.total_emissions = 0
        self.emissions_history = []
        self.food_history = []
    def log(self,food,food_name):
        self.food_history.append(food_name)
        food_added = food
        self.food_dic = self.food_dic + food_added
        self.total_emissions += food_emissions(food_added)
    def __get__(self,idx):
        return self.food_history[idx],self.food_dic[idx],self.emissions_history[idx]
    def __get__(self):
        return self.food_dic,self.total_emissions