from model.model import Plant


def build_prompt(plant: Plant, question: str) -> str:
    return (
        f"Информация о растении:\n"
        f"Название: {plant.name}\n"
        f"Описание: {plant.description}\n"
        f"Вероятность: {plant.probability}\n"
        f"Семейство: {plant.family}\n"
        f"Царство: {plant.kingdom}\n"
        f"Ранг: {plant.rank}\n\n"
        f"Ответь на вопрос о растении строго на основе приведённой информации. "
        f"Если вопрос не относится к растению — скажи 'Вопрос не относится к растению'.\n\n"
        f"Вопрос: {question}"
    )

