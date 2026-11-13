import os
from pathlib import Path
import json
from datetime import date

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from langchain.tools import tool
from langchain_azure_ai.chat_models import AzureAIOpenAIApiChatModel
import pandas as pd

import constants as co
from prompts.extracting_agent_prompt import prompt

load_dotenv()

RESULTS_FOLDER = Path(__file__).parent.parent.resolve() / "result_files" / "mistral"
EXTRACTION_RESULTS_FOLDER = Path(__file__).parent.parent.resolve() / "result_files" / "extraction_results"
EXAMPLE_MD = RESULTS_FOLDER / "asda_groceries_00.md"
OPENAI_BASE_URL = "https://groceries-agent-foundry.services.ai.azure.com/openai/v1"


@tool
def calculate_value_per_item(value: float, quantity: int) -> float:
    """
    Calculate the value per item based on the total value and quantity.
    E.g. If the total value is £7.60 for 2 items, the value per item is £3.80.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    return round(value / quantity, 2)


@tool 
def convert_to_kilograms(value: float, unit: str) -> float:
    """
    Convert a value to kilograms based on its unit.
    E.g. If the value is 7600 and the unit is 'grams', the converted value is 7.6.
    Allowed units: gram, ounce, pound
    """
    if unit == "gram":
        return round(value / 1000, 2)
    elif unit == "ounce":
        return round(value * 0.0283495, 2)
    elif unit == "pound":
        return round(value * 0.453592, 2)
    else:
        raise ValueError("Unsupported unit.")


@tool
def convert_to_litres(value: float, unit: str) -> float:
    """
    Convert a value to litres based on its unit.
    E.g. If the value is 7600 and the unit is 'millilitres', the converted value is 7.6.
    Allowed units: millilitre, pint, centilitre
    """
    if unit == "millilitre":
        return round(value / 1000, 2)
    elif unit == "pint":
        return round(value * 0.568261, 2)
    elif unit == "centilitre":
        return round(value / 100, 2)
    else:
        raise ValueError("Unsupported unit.")


def convert_items_list_to_pandas_df(items_list: list[co.ItemData]) -> pd.DataFrame:
    items_dict = {field: [getattr(item, field) for item in items_list] for field in co.ItemData.model_fields}
    df = pd.DataFrame(data=items_dict)
    return df

def main():
    model = AzureAIOpenAIApiChatModel(
        endpoint=OPENAI_BASE_URL,
        credential=os.environ.get("AZURE_FOUNDRY_KEY"),
        model="gpt-5-nano"
    )    

    agent = create_agent(
        model=model,
        tools=[convert_to_kilograms, convert_to_litres],
        system_prompt=prompt,
        response_format=ProviderStrategy(
            co.ExtractionResult
        )
    )

    for file_ in RESULTS_FOLDER.iterdir():
        if file_.suffix != ".md":
            continue

        with open(file_, "r", encoding="utf-8") as f:
            markdown = f.read()
    
        result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": f"Extract from this receipts:\n\n{markdown}"
            }]
        })

        structured_response = result["structured_response"]

        # items_df = convert_items_list_to_pandas_df(structured_response.items)

        items_dict = [item.__dict__ for item in structured_response.items]
        order_dict = structured_response.order.as_dict()
        
        with open(EXTRACTION_RESULTS_FOLDER / f"{file_.stem}_order.json", "w") as f:
            json.dump(order_dict, f, indent=4)
        with open(EXTRACTION_RESULTS_FOLDER / f"{file_.stem}_items.jsonl", "w") as f:
            for item in items_dict:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        # items_df.to_csv(EXTRACTION_RESULTS_FOLDER / f"{file_.stem}.csv")


if __name__ == "__main__":
    main()


#  TODO stop calculating value per unit, add total to item data and calculate after agent
# more robust rules for product names: no summarisation, should be a substring of original text
# implement ea logic
# add cl to volume rules
# stricter rules for num per pack
# add more examples with no num per pack, simpler cases (2 Cucumbers)