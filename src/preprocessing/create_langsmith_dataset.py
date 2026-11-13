from pathlib import Path
import json 

from langsmith import Client
from dotenv import load_dotenv

import constants as co

load_dotenv()

RESULTS_FOLDER = Path(__file__).parent.parent.resolve() / "result_files" / "mistral"
EXTRACTION_RESULTS_FOLDER = Path(__file__).parent.parent.resolve() / "result_files" / "extraction_results"


def create_examples() -> list[dict]:
    examples = []
    for file_ in RESULTS_FOLDER.iterdir():
        if file_.suffix != ".md":
            continue
        with open(file_, "r", encoding="utf-8") as f:
            markdown = f.read()

        with open(EXTRACTION_RESULTS_FOLDER / f"{file_.stem}_items.jsonl", "r", encoding="utf-8") as f:
            items = [json.loads(line) for line in f if line.strip()]
        with open(EXTRACTION_RESULTS_FOLDER / f"{file_.stem}_order.json", "r", encoding="utf-8") as f:
            order = json.load(f)
        # items = [co.ItemData.model_validate(item) for item in items]
        # order = co.OrderData.model_validate(order)
        example = {
            "inputs": {
                "markdown": markdown
            },
            "outputs": {
                "order": order,
                "items": items
            },
            "metadata": {
                "source_file": file_.name
            }
        }
        examples.append(example)
    return examples


def main():
    client = Client()
    # dataset = client.read_dataset(
    #     dataset_name="Receipts Extraction Results"
    # )
    # print("API endpoint:", client.api_url)
    # print("Dataset ID:", dataset.id)
    # print("Dataset URL:", dataset.url)

    
    examples = create_examples()
    dataset_name = "Receipts Extraction Results"
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Results of extration from grocery receipts"
    )
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )


if __name__ == "__main__":
    main()