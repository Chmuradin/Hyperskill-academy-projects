import sqlite3 as sq


class DatabaseCon:
    """ Creates database connection. """

    def __init__(self, database_name: str = None):
        self.db = database_name
        self.cursor = None
        self.connection = None
        self.create_con()

    def create_con(self):
        """ Creates database connection. """
        self.connection = sq.connect(self.db)
        self.cursor = self.connection.cursor()

    def __str__(self):
        """ A string representation of this class """
        return f'A database named "{self.db}" has been created. '

    def __repr__(self):
        return f'Database [(name, {self.db}), (cursor, {self.cursor}), ' \
               f'(connection, {self.connection}]'


class MealsTable(DatabaseCon):
    table_name = 'meals'

    def __init__(self, database_name: str):
        super().__init__(database_name)

    def __str__(self):
        """ A string representation of this table which
        returns all meals available in the table"""
        query = f"SELECT meal_id, meal_name FROM meals"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        output = ''
        for meal in results:
            output += f'{meal[0]}) {meal[1]}  '
        return output

    def populate_table(self, meal_names: list) -> None:
        """ Populates meals table. """
        for meal in meal_names:
            if meal:
                query = f"INSERT INTO meals(meal_name) VALUES('{meal}')"
                self.cursor.execute(query)
        self.connection.commit()

    def table_creator(self):
        """ Creates meals table. """
        query = f'CREATE TABLE IF NOT EXISTS  {MealsTable.table_name} (' \
                f'meal_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                f'meal_name VARCHAR(20) NOT NULL UNIQUE )'
        self.cursor.execute(query)
        self.connection.commit()


class IngredientTable(DatabaseCon):
    table_name = 'ingredients'

    def __init__(self, database_name: str):
        super().__init__(database_name)

    def get_ingredients(self, ingredient: str):
        """ Gets a list of all ingredients that contains ingredient's
        string value in them. """
        query = f"SELECT ingredient_name, ingredient_id FROM ingredients WHERE ingredient_name " \
                f"GLOB '{ingredient}*' OR ingredient_name GLOB '*{ingredient}'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def populate_table(self, ingredients: list) -> None:
        for ingredient in ingredients:
            if ingredient:
                query = f"INSERT INTO ingredients(ingredient_name) VALUES('{ingredient}')"
                self.cursor.execute(query)
        self.connection.commit()

    def table_creator(self):
        """ Creates ingredients table """
        query = f'CREATE TABLE IF NOT EXISTS {IngredientTable.table_name} (' \
                f'ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT ,' \
                f'ingredient_name VARCHAR(20) NOT NULL UNIQUE )'
        self.cursor.execute(query)
        self.connection.commit()


class MeasureTable(DatabaseCon):
    table_name = 'measures'

    def __init__(self, database_name: str):
        super().__init__(database_name)

    def get_measure_names(self, letter: str):
        """ Gets all measure names starting with letter. """
        if letter == '':
            query = f"SELECT  measure_name, measure_id FROM measures WHERE measure_name == '{letter}'"
        else:
            query = f"SELECT  measure_name, measure_id FROM measures WHERE measure_name GLOB '{letter}*'"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results

    def populate_table(self, measure_names: list) -> None:
        for measure in measure_names:
            query = f"INSERT INTO measures(measure_name) VALUES ('{measure}')"
            self.cursor.execute(query)
        self.connection.commit()

    def table_creator(self):
        query = f'CREATE TABLE IF NOT EXISTS {MeasureTable.table_name} (' \
                f'measure_id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                f'measure_name VARCHAR(20) UNIQUE)'
        self.cursor.execute(query)
        self.connection.commit()


class RecipeTable(DatabaseCon):
    table_name = 'recipes'

    def __init__(self, database_name: str):
        super().__init__(database_name)

    def populate_table(self, recipe_name: str, recipe_description: str) -> int:
        query = f"INSERT INTO recipes(recipe_name, recipe_description) VALUES(" \
                f"'{recipe_name}', '{recipe_description}')"
        self.cursor.execute(query)
        self.connection.commit()
        # Am not closing connection because data are inserted into this table using
        # loop
        return self.cursor.lastrowid

    def create_table(self):
        query = f'CREATE TABLE IF NOT EXISTS {RecipeTable.table_name} (' \
                f'recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                f'recipe_name VARCHAR(40) NOT NULL,' \
                f'recipe_description VARCHAR(100))'
        self.cursor.execute(query)
        self.connection.commit()


class ServeTable(DatabaseCon):
    table_name = 'serve'

    def __init__(self, database_name: str):
        super(ServeTable, self).__init__(database_name)

    def populate_table(self, meals: list, recipe_id: int) -> None:
        for meal_id in meals:
            if meal_id:
                query = f"INSERT INTO serve(recipe_id, meal_id) VALUES ({recipe_id}, " \
                        f"{meal_id})"
                self.cursor.execute(query)
        self.connection.commit()
        # Am not closing connection because data are inserted into this table using
        # loop

    def create_table(self):
        query = f'CREATE TABLE IF NOT EXISTS {ServeTable.table_name} (' \
                f'serve_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                f'recipe_id INTEGER NOT NULL,' \
                f'meal_id INTEGER NOT NULL,' \
                f'FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),' \
                f'FOREIGN KEY(meal_id) REFERENCES meals(meal_id))'
        self.cursor.execute(query)
        self.connection.commit()


class QuantityTable(DatabaseCon):
    table_name = 'quantity'

    def __init__(self, database_name: str):
        super().__init__(database_name)

    def populate_table(self, measure_id: int, ingredient_id: int,
                       quantity: int, recipe_id: int):
        query = f"INSERT INTO quantity (measure_id, ingredient_id, quantity, recipe_id) VALUES (" \
                f"{measure_id}, {ingredient_id}, {quantity}, {recipe_id})"
        self.cursor.execute(query)
        self.connection.commit()
        # Am not closing connection because data are inserted into this table using
        # loop

    def create_table(self):
        query = f'CREATE TABLE IF NOT EXISTS {QuantityTable.table_name} (' \
                f'quantity_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                f'measure_id INTEGER NOT NULL,' \
                f'ingredient_id INTEGER NOT NULL,' \
                f'quantity INTEGER NOT NULL,' \
                f'recipe_id INTEGER NOT NULL,' \
                f'FOREIGN KEY(measure_id) REFERENCES measures(measure_id),' \
                f'FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),' \
                f'FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id))'
        self.cursor.execute(query)
        self.connection.commit()


class SearchMethods(DatabaseCon):

    def __init__(self, database_name: str):
        super().__init__(database_name)

    @staticmethod
    def find_recipes(results, ingredients, meals):
        recipes = []
        for row in results:  # find unique recipes
            if row[0] not in recipes:
                recipes.append(row[0])

        dishes = []
        for recipe in recipes:  # create a set for ingredients and meals
            meal = set()
            component = set()
            dish_name = ""
            for row in results:
                if recipe == row[0]:
                    dish_name = row[1]
                    meal.add(row[2])
                    component.add(row[3])
            dishes.append([dish_name, meal, component])

        answer = []
        for dish in dishes:  # evaluate rhe ingredients and meals
            if ingredients.issubset(dish[2]) and len(meals & dish[1]) > 0:
                answer.append(dish[0])

        if len(answer) > 0:
            print("Recipes selected for you:", ", ".join(answer))
        else:
            print("There are no such recipes in the database.")

    def search_recipes(self, ingredients, meals):
        results = self.cursor.execute("SELECT rec.recipe_id, recipe_name, meal_name, ingredient_name FROM serve ser "
                                      "INNER JOIN recipes rec ON rec.recipe_id = ser.recipe_id "
                                      "INNER JOIN meals mea ON mea.meal_id = ser.meal_id "
                                      "INNER JOIN quantity qua ON qua.recipe_id = rec.recipe_id "
                                      "INNER JOIN ingredients ing ON ing.ingredient_id = qua.ingredient_id ").fetchall()

        self.connection.commit()
        self.connection.close()

        self.find_recipes(results, set(ingredients.split(',')), set(meals.split(',')))
