import os
import requests
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from Recetas.filtering import Filtering  # Importa la clase Filtering

load_dotenv()


class MealPlanner:
    URL_PLANNER = "https://api.spoonacular.com/mealplanner/generate"

    def __init__(self, api_key: str = None):
        self.api_key = api_key if api_key is not None else os.getenv("API_KEY6")
        self.daily_meals_plan = {
            "Meal": [],
            "Name": [],
            "Ingredients": [],
            "Instructions": [],
            "Calories": [],
            "Carbs": [],
            "Fat": [],
            "Protein": [],
        }
        logger.info(f"MealPlanner initialized with API_KEY: {self.api_key}")

    def _meal_planner(
        self, time_frame: str = "Week", target_calories: int = 2000
    ) -> dict[str, list[int]]:
        params = {
            "apiKey": self.api_key,
            "timeFrame": time_frame,
            "targetCalories": target_calories,
        }
        logger.info(f"Realizando petición a la API con parámetros: {params}")
        response = requests.get(self.URL_PLANNER, params=params)
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Respuesta recibida: {data}")
            return Filtering.filter_id_by_meal(data)
        else:
            logger.error(
                f"Error en la solicitud: {response.status_code} - {response.text}"
            )
            return {}

    def _insert_meal_plan_attributes(self, data_to_insert: dict[str, str]):
        """
        data_to_insert son los datos filtrados que se quieren añadir al plan de
        comidas diario.
        """
        for key, value in data_to_insert.items():
            self.daily_meals_plan[key].append(value)
            logger.debug(f"Asignando {key}: {value}")

    def format_meal_name(self, index: 1) -> str:
        if index == 1:
            return "breakfast"
        elif index == 2:
            return "lunch"
        elif index == 3:
            return "dinner"
    
    def _get_recipe_name_and_ingredients(self, days_and_ids: dict[str, list[int]]):
        for day, meal_ids_list in days_and_ids.items():
            for idx, meal_id in enumerate(meal_ids_list):
                url = f"https://api.spoonacular.com/recipes/{meal_id}/information"
                params = {"apiKey": self.api_key}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    filtered = Filtering.filter_name_and_ingredients(data)
                    self._insert_meal_plan_attributes(filtered)
                    meal_label = f"{day} {self.format_meal_name(idx + 1)}"
                    self.daily_meals_plan["Meal"].append(meal_label)
                    logger.info(
                        f"Datos de receta añadidos para {meal_label}: {filtered}"
                    )
                else:
                    logger.error(
                        f"Error en la solicitud: {response.status_code} - {response.text}"
                    )

    def _get_instructions(self, days_and_ids: dict[str, list[int]]):
        for day, meal_ids_list in days_and_ids.items():
            for meal_id in meal_ids_list:
                url = f"https://api.spoonacular.com/recipes/{meal_id}/analyzedInstructions"
                params = {"apiKey": self.api_key}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    filtered = Filtering.filter_instructions(data)
                    self._insert_meal_plan_attributes(filtered)
                    logger.info(f"Instrucciones añadidas para la receta {meal_id}")
                else:
                    logger.error(
                        f"Error en la solicitud: {response.status_code} - {response.text}"
                    )

    def _get_nutrition_facts(self, days_and_ids: dict[str, list[int]]):
        for day, meal_ids_list in days_and_ids.items():
            for meal_id in meal_ids_list:
                url = f"https://api.spoonacular.com/recipes/{meal_id}/nutritionWidget.json"
                params = {"apiKey": self.api_key}
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    filtered = Filtering.filter_nutrition_facts(data)
                    self._insert_meal_plan_attributes(filtered)
                    logger.info(
                        f"Datos nutricionales añadidos para la receta {meal_id}"
                    )
                else:
                    logger.error(
                        f"Error en la solicitud: {response.status_code} - {response.text}"
                    )

    def get_weekly_menu(self, target_calories: int) -> pd.DataFrame:
        days_and_ids = self._meal_planner(target_calories= target_calories)
        self._get_recipe_name_and_ingredients(days_and_ids)
        self._get_instructions(days_and_ids)
        self._get_nutrition_facts(days_and_ids)
        df = pd.DataFrame(self.daily_meals_plan)
        logger.info("Menú semanal generado")
        return df


if __name__ == "__main__":
    planner = MealPlanner()
    weekly_menu = planner.get_weekly_menu(2000)
    weekly_menu.to_csv("daily_meals_plan_example.csv", index=False)