import os
import pickle
import base64
import json
from urllib.request import Request, urlopen
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

import constants as co

load_dotenv()
FOUNDRY_KEY = os.environ.get("AZURE_FOUNDRY_KEY")
AZURE_DOC_INTEL_URL = co.AZURE_DOC_INTELLIGENCE_ENDPOINT
RECEIPTS_FOLDER = co.GOOGLE_DRIVE_PATH / "receipts"
SAVE_FOLDER = Path(__file__).parent / "ocr_results"
document_intelligence_client = DocumentIntelligenceClient(
    endpoint=AZURE_DOC_INTEL_URL, credential=AzureKeyCredential(FOUNDRY_KEY)
)


def _convert_with_mistral(pdf_file: Path) -> tuple:
    pdf_base64 = base64.b64encode(pdf_file.read_bytes()).decode("ascii")
    payload = {
            "model": "mistral-document-ai-2512",
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_base64}",
            },
            "include_image_base64": True,
        }
    request = Request(
        url="https://groceries-agent-foundry.services.ai.azure.com/providers/mistral/azure/ocr",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FOUNDRY_KEY}",
        },
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        result = json.load(response)
    pages = result.get("pages", [])
    markdowns = [p["markdown"] for p in pages]
    full_md = "\n\n <--page break--> \n\n".join(markdowns)
    return full_md, result


def _convert_with_azure(pdf_file: Path) -> tuple:
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=pdf_file.read_bytes())
    )
    result = poller.result()
    return result.content, result


def main():
    for pdf_file in RECEIPTS_FOLDER.iterdir(): 
        print(f"Processing {pdf_file}...")     
        md_mistral, result_mistral = _convert_with_mistral(pdf_file)
        md_azure, result_azure = _convert_with_azure(pdf_file)

        with open(SAVE_FOLDER / "mistral" / f"{pdf_file.stem}.md", "w", encoding="utf-8") as f:
            f.write(md_mistral)

        with open(SAVE_FOLDER / "mistral" / f"{pdf_file.stem}.json", "w", encoding="utf-8") as f:
            json.dump(result_mistral, f, indent=2)

        with open(SAVE_FOLDER / "azure" / f"{pdf_file.stem}.md", "w", encoding="utf-8") as f:
            f.write(md_azure)

        with open(SAVE_FOLDER / "azure" / f"{pdf_file.stem}.pkl", "wb") as pkl_file:
            pickle.dump(result_azure, pkl_file)

main()