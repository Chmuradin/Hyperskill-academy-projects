#!/usr/bin/env python

import argparse
import sys
import os

from databases import (MealsTable, MeasureTable,
                       IngredientTable, RecipeTable,
                       ServeTable, QuantityTable,
                       SearchMethods)

data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}


def cli_arguments():
    """ Handles command line arguments using argparse module. """
    parser = argparse.ArgumentParser(description='Accepts a single argument which is a database'
                                                 'name')
    parser.add_argument('db_name', type=str, help='Database name')
    parser.add_argument('--ingredients', type=str)
    parser.add_argument('--meals')
    return parser.parse_args()


db_name = cli_arguments().db_name
if db_name:
    pass
else:
    print('No database name was passed!')
    sys.exit()


class BlogBackend:
    """ The food blog backend that communicates with the
    3 database tables being used in this project. """

    @staticmethod
    def populate_recipe_table():
        recipe_class = RecipeTable(database_name=db_name)
        recipe_class.create_table()

        serve_class = ServeTable(database_name=db_name)
        serve_class.create_table()

        ingredient_class = IngredientTable(database_name=db_name)
        ingredient_class.table_creator()

        measure_class = MeasureTable(database_name=db_name)
        measure_class.table_creator()

        quantity_table_class = QuantityTable(database_name=db_name)
        quantity_table_class.create_table()
        print('Pass the empty recipe name to exit')
        while True:
            recipe_name = input('Recipe name: ')
            if not recipe_name:
                break
            else:
                recipe_description = input('Recipe description: ')
                meal_cls = MealsTable(database_name=db_name)
                recipe_id = recipe_class.populate_table(recipe_name=recipe_name,
                                                        recipe_description=recipe_description)
                print(meal_cls)
                dish_time = input('When the dish can be served: ').split(' ')
                serve_class.populate_table(meals=dish_time,
                                           recipe_id=recipe_id)
                while True:
                    ingredients_info = input('Input quantity of ingredient <press enter to stop>: ').split(' ')
                    if not ingredients_info[0]:
                        break
                    elif len(ingredients_info) == 2:
                        quantity, ingredient = ingredients_info[0], ingredients_info[1]
                        measure = ''
                    else:
                        quantity, measure, ingredient = ingredients_info[0], ingredients_info[1], ingredients_info[2]
                    check_measure = measure_class.get_measure_names(measure)
                    ingredient_check = ingredient_class.get_ingredients(ingredient)
                    if len(check_measure) == 0 or len(check_measure) > 1:
                        print(f'The measure value -- {measure} -- entered is invalid!')
                    elif len(ingredient_check) == 0 or len(ingredient_check) > 1:
                        print(f'The ingredient -- {ingredient} -- is invalid!')
                    else:
                        quantity_table_class.populate_table(ingredient_id=ingredient_check[0][1],
                                                            measure_id=check_measure[0][1],
                                                            quantity=int(quantity),
                                                            recipe_id=recipe_id)

        recipe_class.connection.close()
        serve_class.connection.close()
        quantity_table_class.connection.close()
        measure_class.connection.close()
        ingredient_class.connection.close()

    @staticmethod
    def populate_measures_table():
        measures = list(data.get("measures"))
        measure_class = MeasureTable(database_name=db_name)
        measure_class.table_creator()
        measure_class.populate_table(measure_names=measures)
        measure_class.connection.close()

    @staticmethod
    def populate_ingredient_table():
        ingredients = list(data.get("ingredients"))
        ingredients_class = IngredientTable(database_name=db_name)
        ingredients_class.table_creator()
        ingredients_class.populate_table(ingredients)
        ingredients_class.connection.close()

    @staticmethod
    def populate_meals_table():
        meal_data = list(data.get("meals"))
        meal_table_class = MealsTable(database_name=db_name)
        meal_table_class.table_creator()
        meal_table_class.populate_table(meal_names=meal_data)
        meal_table_class.connection.close()


def main():
    data_writer_cls = BlogBackend()
    if not os.access(db_name, os.F_OK):
        data_writer_cls.populate_meals_table()
        data_writer_cls.populate_ingredient_table()
        data_writer_cls.populate_measures_table()
        data_writer_cls.populate_recipe_table()
    search_tools = SearchMethods(db_name)
    if cli_arguments().ingredients is not None and cli_arguments().meals is not None:
        search_tools.search_recipes(cli_arguments().ingredients, cli_arguments().meals)


if __name__ == '__main__':
    main()
