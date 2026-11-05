import json
from pathlib import Path

import src.preprocessing.util as util


OCR_RESULTS_FOLDER = Path(__file__).parent.parent.resolve() / "ocr_results" / "mistral"


def create_markdown_from_ocr_result(ocr_result: dict) -> str:
    """Constrcut a full markdown using Mistral OCR result object"""
    try:
        pages = ocr_result['pages']
        assert len(pages) > 0
    except KeyError:
        raise ValueError("The provided OCR result does not contain the 'pages' key.")
    except AssertionError:
        raise ValueError("The 'pages' key in the OCR result is empty.")

    page_markdowns = []
    for page in pages:
        page_markdown = page.get('markdown', "")
        if page_markdown == "":
            continue
        hyperlinks = page.get("hyperlinks", [])
        markdown = util.remove_known_terms(page_markdown, hyperlinks)
        page_markdowns.append(markdown)
    full_markdown = "\n\n".join(page_markdowns)
    return full_markdown


def main():
    for file_ in OCR_RESULTS_FOLDER.iterdir():
        if file_.suffix.lower() != ".json":
            continue
        with open(file_, "r", encoding="utf-8") as f:
            result = json.load(f)
        full_markdown = create_markdown_from_ocr_result(result)
        with open(OCR_RESULTS_FOLDER / f"{file_.stem}.md", "w", encoding="utf-8") as f:
            f.write(full_markdown)

main()