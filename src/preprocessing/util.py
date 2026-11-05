import re
import os

from dotenv import load_dotenv

load_dotenv()


KNOWN_TERMS_TO_REMOVE = [
    "print order",
    "write a review",
]


def remove_known_terms(text: str, additional_remove_terms: list) -> str:
    """
    Remove known terms that don't add valuefrom the text, ignoring case.
    E.g. 
    """
    my_vars = [
        value
        for key, value in os.environ.items()
        if key.startswith("MY_")
    ]
    remove_terms = KNOWN_TERMS_TO_REMOVE + additional_remove_terms + my_vars
    for term in remove_terms:
        term_re = rf"[#*\s]*{term}\**"
        text = re.sub(term_re, "", text, flags=re.IGNORECASE)
    return text
