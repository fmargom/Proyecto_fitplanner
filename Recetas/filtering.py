from loguru import logger


class Filtering:
    @staticmethod
    def filter_id_by_meal(data_in_json: dict) -> dict[str, list[int]]:
        weekly_meals_data = data_in_json.get("week", {})
        days_and_meals = {}
        for day, meals in weekly_meals_data.items():
            meals_id_list = [meal.get("id") for meal in meals.get("meals", [])]
            days_and_meals[day] = meals_id_list
        logger.debug(f"IDs filtrados: {days_and_meals}")
        return days_and_meals

    @staticmethod
    def filter_name_and_ingredients(recipe_details: dict) -> dict[str, str]:
        def filter_ingredients() -> str:
            extended_ingredients: list[dict[str, str]] = recipe_details.get(
                "extendedIngredients", []
            )
            ingredients_list = [
                ingredient.get("original", "") for ingredient in extended_ingredients
            ]
            return ", ".join(ingredients_list)

        name = recipe_details.get("title", "")
        ingredients = filter_ingredients()
        logger.debug(f"Nombre e ingredientes filtrados: {name} - {ingredients}")
        return {"Name": name, "Ingredients": ingredients}

    @staticmethod
    def filter_instructions(recipe_details: list) -> dict[str, str]:
        steps: list[dict[str, str]] = (
            recipe_details[0].get("steps", []) if recipe_details else []
        )
        instructions_list = [
            f"{i + 1}. {instruction.get('step', '')}"
            for i, instruction in enumerate(steps)
        ]
        instructions_str = " ".join(instructions_list)
        logger.debug(f"Instrucciones filtradas: {instructions_str}")
        return {"Instructions": instructions_str}

    @staticmethod
    def filter_nutrition_facts(nutrition_data: dict) -> dict[str, int]:
        filtered = {
            "Calories": nutrition_data.get("calories", 0),
            "Carbs": nutrition_data.get("carbs", 0),
            "Fat": nutrition_data.get("fat", 0),
            "Protein": nutrition_data.get("protein", 0),
        }
        logger.debug(f"Datos nutricionales filtrados: {filtered}")
        return filtered
