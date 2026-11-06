import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_azure_ai.chat_models import AzureAIOpenAIApiChatModel

import constants as co
from prompts.extracting_agent_prompt import prompt

load_dotenv()

OCR_RESULTS_FOLDER = Path(__file__).parent.parent.resolve() / "ocr_results" / "mistral"
EXAMPLE_MD = OCR_RESULTS_FOLDER / "asda_groceries_00.md"
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
    Allowed units: millilitre, pint
    """
    if unit == "millilitre":
        return round(value / 1000, 2)
    elif unit == "pint":
        return round(value * 0.568261, 2)
    else:
        raise ValueError("Unsupported unit.")


def main():
    model = AzureAIOpenAIApiChatModel(
        endpoint=OPENAI_BASE_URL,
        credential=os.environ.get("AZURE_FOUNDRY_KEY"),
        model="gpt-5-nano"
    )
    agent = create_agent(
        model=model,
        # tools=[calculate_value_per_item, convert_to_kilograms, convert_to_litres],
        system_prompt="You are a helpful assistant who knows everything about dinosairs and directs every question towards dinosaurs.",
        # response_format=co.ExtractionResult
    )

    with open(EXAMPLE_MD, "r", encoding="utf-8") as f:
        example_markdown = f.read()
    
    # result = agent.invoke({
    #     "messages": [{
    #         "role": "user",
    #         "content": f"Extract from this receipts:\n\n{example_markdown}"
    #     }]
    # })

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "What is the capital of France?"
        }]
    })
    result

main()