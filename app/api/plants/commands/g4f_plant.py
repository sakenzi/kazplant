import g4f
from fastapi import HTTPException
import logging
from typing import Dict, Optional
import ast
import traceback


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def process_plant_data_with_g4f(plant_name: str, probability: float) -> Dict[str, Optional[str]]:

    prompt = (
        f"Переведи название растения '{plant_name}' на русский язык. "
        f"Также предоставь краткое описание растения, его семейство (family) и царство (kingdom) на русском языке. "
        f"Формат ответа: {{'name': str, 'description': str, 'family': str, 'kingdom': str}}"
    )
    
    logger.info(f"Sending prompt to G4F for plant: {plant_name} with probability: {probability}")

    response = await g4f.ChatCompletion.create_async(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    logger.info("Received response from G4F")

    print("\n--- RAW RESPONSE FROM G4F ---")
    print(response)

    g4f_data = ast.literal_eval(response) if isinstance(response, str) else response

    logger.debug("Parsed G4F data successfully")

    print("\n--- PARSED G4F DATA ---")
    print(g4f_data)

    required_keys = {"name", "description", "family", "kingdom"}
    if not isinstance(g4f_data, dict) or not all(key in g4f_data for key in required_keys):
        logger.error("G4F response is missing required fields")
        raise HTTPException(status_code=500, detail="Incomplete G4F response")

    logger.info("Successfully processed G4F data")

    return {
        "name": g4f_data["name"],
        "description": g4f_data["description"],
        "family": g4f_data["family"],
        "kingdom": g4f_data["kingdom"]
    }

