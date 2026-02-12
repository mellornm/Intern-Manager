def smart_title(text: str) -> str:
    acronyms = ["SUS", "DNA", "RNA"]
    exceptions = ["da", "de", "do", "das", "dos", "e", "em"]

    if not text:
        return ""

    words = text.split()

    final_text = []

    for i, word in enumerate(words):
        if i == 0:
            final_text.append(word.title())
        elif word.lower in exceptions:
            final_text.append(word.lower())
        elif word.upper in acronyms:
            final_text.append(word.upper())
        else:
            final_text.append(word)

    return " ".join(final_text)
