import re
import unicodedata


def smart_title(text: str) -> str:
    """
    Formata strings para Title Case inteligente.
    - Mantém minúsculas: de, da, do, dos, das, e, em...
    - Mantém maiúsculas (Siglas): SUS, UTI, TCC, RG...
    - Capitaliza o resto: João, Silva, Hospital...
    """
    if not text:
        return ""

    text = " ".join(text.split())

    # Lista de exceções que devem ficar minúsculas
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

    # Lista de siglas que devem ficar SEMPRE MAIÚSCULAS
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

        # Regra 1: A primeira palavra sempre recebe tratamento especial
        if i == 0:
            # Se for sigla mantém maiúsculo. Senão, capitaliza.
            if upper_word in acronyms:
                final_words.append(upper_word)
            else:
                final_words.append(word.capitalize())

        # Regra 2: Siglas conhecidas ficam em MAIÚSCULO
        elif upper_word in acronyms:
            final_words.append(upper_word)

        # Regra 3: Preposições ficam em minúsculo
        elif lower_word in exceptions:
            final_words.append(lower_word)

        # Regra 4: O resto vira "Nome Próprio"
        else:
            final_words.append(word.capitalize())

    return " ".join(final_words)


def sanitize_filename(text: str) -> str:
    # 1. Normaliza unicode (tira acentos)
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    # 2. Mantém apenas letras, números, hífens e underlines
    text = re.sub(r"[^\w\s-]", "", text)
    # 3. Troca espaços por underline
    text = re.sub(r"[-\s]+", "_", text).strip("-_")
    return text
