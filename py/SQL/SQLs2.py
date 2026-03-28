import sqlite3
class SQLs:
    def __init__(self,name='database.db'):
        self.db = name
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()
    def initialize_db(self):
        self.cursor.execute('''CREATE Table IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            Health_Points INTEGER NOT NULL,
                            Carbon_Points INTEGER NOT NULL,
                            vitamin_a_mcg_d REAL,
                            vitamin_c_mg_d REAL,
                            vitamin_d_mcg_d REAL,
                            vitamin_e_mg_d REAL,
                            vitamin_k_mcg_d REAL,
                            thiamin_mg_d REAL,
                            riboflavin_mg_d REAL,
                            niacin_mg_d REAL,
                            vitamin_b6_mg_d REAL,
                            folate_mcg_d REAL,
                            vitamin_b12_mcg_d REAL,
                            pantothenic_acid_mg_d REAL,
                            biotin_mcg_d REAL,
                            choline_mg_d REAL,
                            total_water_l_d REAL,
                            carbohydrate_g_d REAL,
                            total_fiber_g_d REAL,
                            fat_g_d REAL,
                            linoleic_acid_g_d REAL,
                            alpha_linolenic_acid_g_d REAL,
                            protein_g_d REAL,
                            calcium_mg_d REAL,
                            chromium_mcg_d REAL,
                            copper_mcg_d REAL,
                            fluoride_mg_d REAL,
                            iodine_mcg_d REAL,
                            iron_mg_d REAL,
                            magnesium_mg_d REAL,
                            manganese_mg_d REAL,
                            molybdenum_mcg_d REAL,
                            phosphorus_mg_d REAL,
                            selenium_mcg_d REAL,
                            zinc_mg_d REAL,
                            potassium_mg_d REAL,
                            sodium_mg_d REAL,
                            chloride_g_d REAL,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL,
                            email TEXT NOT NULL,
                            profile_picture TEXT NOT NULL)''')
        self.conn.commit()
        self.cursor.execute('''CREATE Table IF NOT EXISTS meals
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserId INTEGER NOT NULL,
                            Meal_Name TEXT NOT NULL,
                            grams REAL NOT NULL,
                            Calories INTEGER NOT NULL,
                            Carbon_Footprint REAL NOT NULL,
                            vitamin_a_mcg_d REAL,
                            vitamin_c_mg_d REAL,
                            vitamin_d_mcg_d REAL,
                            vitamin_e_mg_d REAL,
                            vitamin_k_mcg_d REAL,
                            thiamin_mg_d REAL,
                            riboflavin_mg_d REAL,
                            niacin_mg_d REAL,
                            vitamin_b6_mg_d REAL,
                            folate_mcg_d REAL,
                            vitamin_b12_mcg_d REAL,
                            pantothenic_acid_mg_d REAL,
                            biotin_mcg_d REAL,
                            choline_mg_d REAL,
                            total_water_l_d REAL,
                            carbohydrate_g_d REAL,
                            total_fiber_g_d REAL,
                            fat_g_d REAL,
                            linoleic_acid_g_d REAL,
                            alpha_linolenic_acid_g_d REAL,
                            protein_g_d REAL,
                            calcium_mg_d REAL,
                            chromium_mcg_d REAL,
                            copper_mcg_d REAL,
                            fluoride_mg_d REAL,
                            iodine_mcg_d REAL,
                            iron_mg_d REAL,
                            magnesium_mg_d REAL,
                            manganese_mg_d REAL,
                            molybdenum_mcg_d REAL,
                            phosphorus_mg_d REAL,
                            selenium_mcg_d REAL,
                            zinc_mg_d REAL,
                            potassium_mg_d REAL,
                            sodium_mg_d REAL,
                            chloride_g_d REAL,
                            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(UserId) REFERENCES users(id))''')
        self.conn.commit()
        self.cursor.execute('''CREATE Table IF NOT EXISTS Inventory
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            UserId INTEGER NOT NULL,
                            Food_Name TEXT NOT NULL,
                            grams REAL NOT NULL,
                            Calories INTEGER NOT NULL,
                            Carbon_Footprint REAL NOT NULL,
                            Time_entered DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(UserId) REFERENCES users(id))''')
        self.conn.commit()
    def add_user(self, username, password, email, profile_picture, 
             health_points=0, carbon_points=0,
             vitamin_a_mcg_d=0.0, vitamin_c_mg_d=0.0, vitamin_d_mcg_d=0.0,
             vitamin_e_mg_d=0.0, vitamin_k_mcg_d=0.0, thiamin_mg_d=0.0,
             riboflavin_mg_d=0.0, niacin_mg_d=0.0, vitamin_b6_mg_d=0.0,
             folate_mcg_d=0.0, vitamin_b12_mcg_d=0.0, pantothenic_acid_mg_d=0.0,
             biotin_mcg_d=0.0, choline_mg_d=0.0, total_water_l_d=0.0,
             carbohydrate_g_d=0.0, total_fiber_g_d=0.0, fat_g_d=0.0,
             linoleic_acid_g_d=0.0, alpha_linolenic_acid_g_d=0.0, protein_g_d=0.0,
             calcium_mg_d=0.0, chromium_mcg_d=0.0, copper_mcg_d=0.0,
             fluoride_mg_d=0.0, iodine_mcg_d=0.0, iron_mg_d=0.0,
             magnesium_mg_d=0.0, manganese_mg_d=0.0, molybdenum_mcg_d=0.0,
             phosphorus_mg_d=0.0, selenium_mcg_d=0.0, zinc_mg_d=0.0,
             potassium_mg_d=0.0, sodium_mg_d=0.0, chloride_g_d=0.0):
    
        try:
            self.cursor.execute('''
                INSERT INTO users (
                username, password, email, profile_picture,
                Health_Points, Carbon_Points,
                vitamin_a_mcg_d, vitamin_c_mg_d, vitamin_d_mcg_d,
                vitamin_e_mg_d, vitamin_k_mcg_d, thiamin_mg_d,
                riboflavin_mg_d, niacin_mg_d, vitamin_b6_mg_d,
                folate_mcg_d, vitamin_b12_mcg_d, pantothenic_acid_mg_d,
                biotin_mcg_d, choline_mg_d, total_water_l_d,
                carbohydrate_g_d, total_fiber_g_d, fat_g_d,
                linoleic_acid_g_d, alpha_linolenic_acid_g_d, protein_g_d,
                calcium_mg_d, chromium_mcg_d, copper_mcg_d,
                fluoride_mg_d, iodine_mcg_d, iron_mg_d,
                magnesium_mg_d, manganese_mg_d, molybdenum_mcg_d,
                phosphorus_mg_d, selenium_mcg_d, zinc_mg_d,
                potassium_mg_d, sodium_mg_d, chloride_g_d
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, email, profile_picture, health_points, carbon_points,
              vitamin_a_mcg_d, vitamin_c_mg_d, vitamin_d_mcg_d,
              vitamin_e_mg_d, vitamin_k_mcg_d, thiamin_mg_d,
              riboflavin_mg_d, niacin_mg_d, vitamin_b6_mg_d,
              folate_mcg_d, vitamin_b12_mcg_d, pantothenic_acid_mg_d,
              biotin_mcg_d, choline_mg_d, total_water_l_d,
              carbohydrate_g_d, total_fiber_g_d, fat_g_d,
              linoleic_acid_g_d, alpha_linolenic_acid_g_d, protein_g_d,
              calcium_mg_d, chromium_mcg_d, copper_mcg_d,
              fluoride_mg_d, iodine_mcg_d, iron_mg_d,
              magnesium_mg_d, manganese_mg_d, molybdenum_mcg_d,
              phosphorus_mg_d, selenium_mcg_d, zinc_mg_d,
              potassium_mg_d, sodium_mg_d, chloride_g_d))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to add user: {str(e)}")
    
    def add_carbon_points(self,user_id,points):
        self.cursor.execute('''UPDATE users SET Carbon_Points = Carbon_Points + ? WHERE id = ?''', (points, user_id))
        self.conn.commit()
    def add_health_points(self,user_id,points):
        self.cursor.execute('''UPDATE users SET Health_Points = Health_Points + ? WHERE id = ?''', (points, user_id))
        self.conn.commit()
    def set_health_points(self,user_id,points):
        self.cursor.execute('''UPDATE users SET Health_Points = ? WHERE id = ?''', (points, user_id))
        self.conn.commit()
    def set_carbon_points(self,user_id,points):
        self.cursor.execute('''UPDATE users SET Carbon_Points = ? WHERE id = ?''', (points, user_id))
        self.conn.commit()
    def get_user(self,userid):
        self.cursor.execute('''SELECT * FROM users WHERE id = ?''', (userid,))
        return self.cursor.fetchone()
    def add_meal(self,user_id,meal_name,grams,calories,carbon_footprint):
        self.cursor.execute('''INSERT INTO meals (UserId, Meal_Name, grams, Calories, Carbon_Footprint) 
                            VALUES (?, ?, ?, ?, ?)''', (user_id, meal_name, grams, calories, carbon_footprint))
        self.conn.commit()
    
    def get_meals(self,user_id):
        self.cursor.execute('''SELECT * FROM meals WHERE UserId = ?''', (user_id,))
        return self.cursor.fetchall()
    def get_inventory(self,user_id):
        self.cursor.execute('''SELECT * FROM Inventory WHERE UserId = ?''', (user_id,))
        return self.cursor.fetchall()
    def get_email(self, user_id):
        self.cursor.execute('''SELECT email FROM users WHERE id = ?''', (user_id,))  # Add comma!
        return self.cursor.fetchone()
    def set_email(self,user_id,email):
        self.cursor.execute('''UPDATE users SET email = ? WHERE id = ?''', (email, user_id))
        self.conn.commit()
    def set_profile_picture(self,user_id,profile):
        self.cursor.execute('''UPDATE users SET profile_picture = ? WHERE id = ?''', (profile, user_id))
        self.conn.commit()
    def set_user_nutrition(self, user_id, vitamin_a_mcg_d,
                  vitamin_c_mg_d,
                  vitamin_d_mcg_d,
                  vitamin_e_mg_d,
                  vitamin_k_mcg_d,
                  thiamin_mg_d,
                  riboflavin_mg_d,
                  niacin_mg_d,
                  vitamin_b6_mg_d,
                  folate_mcg_d,
                  vitamin_b12_mcg_d,
                  pantothenic_acid_mg_d,
                  biotin_mcg_d,
                  choline_mg_d,
                  total_water_l_d,
                  carbohydrate_g_d,
                  total_fiber_g_d,
                  fat_g_d,
                  linoleic_acid_g_d,
                  alpha_linolenic_acid_g_d,
                  protein_g_d,
                  calcium_mg_d,
                  chromium_mcg_d,
                  copper_mcg_d,
                  fluoride_mg_d,
                  iodine_mcg_d,
                  iron_mg_d,
                  magnesium_mg_d,
                  manganese_mg_d,
                  molybdenum_mcg_d,
                  phosphorus_mg_d,
                  selenium_mcg_d,
                  zinc_mg_d,
                  potassium_mg_d,
                  sodium_mg_d,
                  chloride_g_d):
        self.cursor.execute('''UPDATE users 
                        SET vitamin_a_mcg_d = ?,
                            vitamin_c_mg_d = ?,
                            vitamin_d_mcg_d = ?,
                            vitamin_e_mg_d = ?,
                            vitamin_k_mcg_d = ?,
                            thiamin_mg_d = ?,
                            riboflavin_mg_d = ?,
                            niacin_mg_d = ?,
                            vitamin_b6_mg_d = ?,
                            folate_mcg_d = ?,
                            vitamin_b12_mcg_d = ?,
                            pantothenic_acid_mg_d = ?,
                            biotin_mcg_d = ?,
                            choline_mg_d = ?,
                            total_water_l_d = ?,
                            carbohydrate_g_d = ?,
                            total_fiber_g_d = ?,
                            fat_g_d = ?,
                            linoleic_acid_g_d = ?,
                            alpha_linolenic_acid_g_d = ?,
                            protein_g_d = ?,
                            calcium_mg_d = ?,
                            chromium_mcg_d = ?,
                            copper_mcg_d = ?,
                            fluoride_mg_d = ?,
                            iodine_mcg_d = ?,
                            iron_mg_d = ?,
                            magnesium_mg_d = ?,
                            manganese_mg_d = ?,
                            molybdenum_mcg_d = ?,
                            phosphorus_mg_d = ?,
                            selenium_mcg_d = ?,
                            zinc_mg_d = ?,
                            potassium_mg_d = ?,
                            sodium_mg_d = ?,
                            chloride_g_d = ?
                        WHERE id = ?''', 
                        (vitamin_a_mcg_d, vitamin_c_mg_d, vitamin_d_mcg_d, vitamin_e_mg_d, vitamin_k_mcg_d,
                         thiamin_mg_d, riboflavin_mg_d, niacin_mg_d, vitamin_b6_mg_d, folate_mcg_d,
                         vitamin_b12_mcg_d, pantothenic_acid_mg_d, biotin_mcg_d, choline_mg_d, total_water_l_d,
                         carbohydrate_g_d, total_fiber_g_d, fat_g_d, linoleic_acid_g_d, alpha_linolenic_acid_g_d,
                         protein_g_d, calcium_mg_d, chromium_mcg_d, copper_mcg_d, fluoride_mg_d, iodine_mcg_d,
                         iron_mg_d, magnesium_mg_d, manganese_mg_d, molybdenum_mcg_d, phosphorus_mg_d, selenium_mcg_d,
                         zinc_mg_d, potassium_mg_d, sodium_mg_d, chloride_g_d, user_id))  # user_id last!
        self.conn.commit()
    def set_meal_nutrition(self, meal_id, vitamin_a_mcg_d,
                        vitamin_c_mg_d,
                        vitamin_d_mcg_d,
                        vitamin_e_mg_d,
                        vitamin_k_mcg_d,
                        thiamin_mg_d,
                        riboflavin_mg_d,
                        niacin_mg_d,
                        vitamin_b6_mg_d,
                        folate_mcg_d,
                        vitamin_b12_mcg_d,
                        pantothenic_acid_mg_d,
                        biotin_mcg_d,
                        choline_mg_d,
                        total_water_l_d,
                        carbohydrate_g_d,
                        total_fiber_g_d,
                        fat_g_d,
                        linoleic_acid_g_d,
                        alpha_linolenic_acid_g_d,
                        protein_g_d,
                        calcium_mg_d,
                        chromium_mcg_d,
                        copper_mcg_d,
                        fluoride_mg_d,
                        iodine_mcg_d,
                        iron_mg_d,
                        magnesium_mg_d,
                        manganese_mg_d,
                        molybdenum_mcg_d,
                        phosphorus_mg_d,
                        selenium_mcg_d,
                        zinc_mg_d,
                        potassium_mg_d,
                        sodium_mg_d,
                        chloride_g_d):
            # Update all nutrition columns for the specified meal entry
        self.cursor.execute('''UPDATE meals 
                        SET vitamin_a_mcg_d = ?,
                            vitamin_c_mg_d = ?,
                            vitamin_d_mcg_d = ?,
                            vitamin_e_mg_d = ?,
                            vitamin_k_mcg_d = ?,
                            thiamin_mg_d = ?,
                            riboflavin_mg_d = ?,
                            niacin_mg_d = ?,
                            vitamin_b6_mg_d = ?,
                            folate_mcg_d = ?,
                            vitamin_b12_mcg_d = ?,
                            pantothenic_acid_mg_d = ?,
                            biotin_mcg_d = ?,
                            choline_mg_d = ?,
                            total_water_l_d = ?,
                            carbohydrate_g_d = ?,
                            total_fiber_g_d = ?,
                            fat_g_d = ?,
                            linoleic_acid_g_d = ?,
                            alpha_linolenic_acid_g_d = ?,
                            protein_g_d = ?,
                            calcium_mg_d = ?,
                            chromium_mcg_d = ?,
                            copper_mcg_d = ?,
                            fluoride_mg_d = ?,
                            iodine_mcg_d = ?,
                            iron_mg_d = ?,
                            magnesium_mg_d = ?,
                            manganese_mg_d = ?,
                            molybdenum_mcg_d = ?,
                            phosphorus_mg_d = ?,
                            selenium_mcg_d = ?,
                            zinc_mg_d = ?,
                            potassium_mg_d = ?,
                            sodium_mg_d = ?,
                            chloride_g_d = ?
                        WHERE id = ?''', 
                        (vitamin_a_mcg_d, vitamin_c_mg_d, vitamin_d_mcg_d, vitamin_e_mg_d, vitamin_k_mcg_d,
                         thiamin_mg_d, riboflavin_mg_d, niacin_mg_d, vitamin_b6_mg_d, folate_mcg_d,
                         vitamin_b12_mcg_d, pantothenic_acid_mg_d, biotin_mcg_d, choline_mg_d, total_water_l_d,
                         carbohydrate_g_d, total_fiber_g_d, fat_g_d, linoleic_acid_g_d, alpha_linolenic_acid_g_d,
                         protein_g_d, calcium_mg_d, chromium_mcg_d, copper_mcg_d, fluoride_mg_d, iodine_mcg_d,
                         iron_mg_d, magnesium_mg_d, manganese_mg_d, molybdenum_mcg_d, phosphorus_mg_d, selenium_mcg_d,
                         zinc_mg_d, potassium_mg_d, sodium_mg_d, chloride_g_d, meal_id))  # meal_id last!
        self.conn.commit()
    def add_meal(self, user_id, meal_name, grams, calories, carbon_footprint,
             vitamin_a_mcg_d=0.0, vitamin_c_mg_d=0.0, vitamin_d_mcg_d=0.0,
             vitamin_e_mg_d=0.0, vitamin_k_mcg_d=0.0, thiamin_mg_d=0.0,
             riboflavin_mg_d=0.0, niacin_mg_d=0.0, vitamin_b6_mg_d=0.0,
             folate_mcg_d=0.0, vitamin_b12_mcg_d=0.0, pantothenic_acid_mg_d=0.0,
             biotin_mcg_d=0.0, choline_mg_d=0.0, total_water_l_d=0.0,
             carbohydrate_g_d=0.0, total_fiber_g_d=0.0, fat_g_d=0.0,
             linoleic_acid_g_d=0.0, alpha_linolenic_acid_g_d=0.0, protein_g_d=0.0,
             calcium_mg_d=0.0, chromium_mcg_d=0.0, copper_mcg_d=0.0,
             fluoride_mg_d=0.0, iodine_mcg_d=0.0, iron_mg_d=0.0,
             magnesium_mg_d=0.0, manganese_mg_d=0.0, molybdenum_mcg_d=0.0,
             phosphorus_mg_d=0.0, selenium_mcg_d=0.0, zinc_mg_d=0.0,
             potassium_mg_d=0.0, sodium_mg_d=0.0, chloride_g_d=0.0):
        """
        Add a meal with complete nutritional data.
        Returns the ID of the newly created meal entry.
        """
        try:
            self.cursor.execute('''
                INSERT INTO meals (
                    UserId, Meal_Name, grams, Calories, Carbon_Footprint,
                    vitamin_a_mcg_d, vitamin_c_mg_d, vitamin_d_mcg_d,
                    vitamin_e_mg_d, vitamin_k_mcg_d, thiamin_mg_d,
                    riboflavin_mg_d, niacin_mg_d, vitamin_b6_mg_d,
                    folate_mcg_d, vitamin_b12_mcg_d, pantothenic_acid_mg_d,
                    biotin_mcg_d, choline_mg_d, total_water_l_d,
                    carbohydrate_g_d, total_fiber_g_d, fat_g_d,
                    linoleic_acid_g_d, alpha_linolenic_acid_g_d, protein_g_d,
                    calcium_mg_d, chromium_mcg_d, copper_mcg_d,
                    fluoride_mg_d, iodine_mcg_d, iron_mg_d,
                    magnesium_mg_d, manganese_mg_d, molybdenum_mcg_d,
                    phosphorus_mg_d, selenium_mcg_d, zinc_mg_d,
                    potassium_mg_d, sodium_mg_d, chloride_g_d
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, meal_name, grams, calories, carbon_footprint,
                vitamin_a_mcg_d, vitamin_c_mg_d, vitamin_d_mcg_d,
                vitamin_e_mg_d, vitamin_k_mcg_d, thiamin_mg_d,
                riboflavin_mg_d, niacin_mg_d, vitamin_b6_mg_d,
                folate_mcg_d, vitamin_b12_mcg_d, pantothenic_acid_mg_d,
                biotin_mcg_d, choline_mg_d, total_water_l_d,
                carbohydrate_g_d, total_fiber_g_d, fat_g_d,
                linoleic_acid_g_d, alpha_linolenic_acid_g_d, protein_g_d,
                calcium_mg_d, chromium_mcg_d, copper_mcg_d,
                fluoride_mg_d, iodine_mcg_d, iron_mg_d,
                magnesium_mg_d, manganese_mg_d, molybdenum_mcg_d,
                phosphorus_mg_d, selenium_mcg_d, zinc_mg_d,
                potassium_mg_d, sodium_mg_d, chloride_g_d))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Failed to add meal: {str(e)}")

    def add_inventory(self,user_id,food_name,grams,calories,carbon_footprint):
        self.cursor.execute('''INSERT INTO Inventory (UserId, Food_Name, grams, Calories, Carbon_Footprint) 
                            VALUES (?, ?, ?, ?, ?)''', (user_id, food_name, grams, calories, carbon_footprint))
        self.conn.commit()
manager = SQLs()
manager.initialize_db()
manager.add_user('me','1111','111@shsid.org','me.png')
manager.add_inventory(0,'me',100,100,100)
manager.add_meal(0,'mw',100,100,100)
