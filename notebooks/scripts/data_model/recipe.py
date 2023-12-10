from typing import List
from data_model.ingredient import Ingredient

class Recipe:
    def __init__(self, name, ingredients, instruction):
        self.name = name
        self.ingredients = ingredients
        self.instruction = instruction
        