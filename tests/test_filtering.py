from Recetas.filtering import Filtering

def test_filter_id_by_meal():
    # Datos de prueba
    data_in_json = {
        "week": {
            "Lunes": {"meals": [{"id": 1, "name": "Comida1"}, {"id": 2, "name": "Comida2"}]},
            "Martes": {"meals": [{"id": 3, "name": "Comida3"}]}
        }
    }
    expected = {"Lunes": [1, 2], "Martes": [3]}
    result = Filtering.filter_id_by_meal(data_in_json)
    assert result == expected

def test_filter_name_and_ingredients():
    # Datos de prueba
    recipe_details = {
        "title": "Ensalada",
        "extendedIngredients": [
            {"original": "Lechuga"},
            {"original": "Tomate"},
            {"original": "Aceite"}
        ]
    }
    expected = {"Name": "Ensalada", "Ingredients": "Lechuga, Tomate, Aceite"}
    result = Filtering.filter_name_and_ingredients(recipe_details)
    assert result == expected