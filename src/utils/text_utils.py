import re
import unicodedata


def smart_title(text: str) -> str:
    """Converts a string to a title case while preserving certain exceptions and acronyms.

    Args:
        text (str): The string to be converted.

    Returns:
        str: The converted string in title case.
    """
    if not text:
        return ""

    text = " ".join(text.split())

    exceptions = {
        "de",
        "da",
        "do",
        "das",
        "dos",
        "e",
        "em",
        "na",
        "no",
        "nas",
        "nos",
        "por",
        "com",
    }

    acronyms = {
        "SUS",
        "UTI",
        "TCC",
        "UBS",
        "SAMU",
        "PS",
        "UPA",
        "RG",
        "CPF",
        "CNPJ",
        "RA",
        "DNA",
        "RNA",
        "HIV",
    }

    words = text.split()
    final_words = []

    for i, word in enumerate(words):
        lower_word = word.lower()
        upper_word = word.upper()

        if i == 0:
            if upper_word in acronyms:
                final_words.append(upper_word)
            else:
                final_words.append(word.capitalize())

        elif upper_word in acronyms:
            final_words.append(upper_word)

        elif lower_word in exceptions:
            final_words.append(lower_word)

        else:
            final_words.append(word.capitalize())

    return " ".join(final_words)


def sanitize_filename(text: str) -> str:
    """Sanitizes a filename by removing non-alphanumeric characters and replacing
    whitespace with underscores.

    Args:
        text (str): The filename to be sanitized.

    Returns:
        str: The sanitized filename.
    """
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text).strip("-_")
    return text
