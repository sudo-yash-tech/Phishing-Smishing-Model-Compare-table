"""
generate_hinglish_dataset.py

Generates D4 (Hinglish dataset) by transliterating D3 (Hindi dataset)
from Devanagari script into Roman script. This is a SYNTHETIC/AUGMENTED
dataset, not organic Hinglish - documented clearly here and in the
dissertation because no public organic Hinglish phishing/spam corpus
exists (confirmed via literature search).

The raw transliteration library output uses academic ITRANS notation
(capital letters for long vowels, "|" for sentence punctuation) which
does not resemble how people actually type Hinglish casually. This
script includes a cleanup pass to make the output look like realistic
casual texting instead.

Run from your project root:
    python generate_hinglish_dataset.py
"""

import pandas as pd
from pathlib import Path
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

INPUT_PATH = Path("dataset/raw/d3_hindi.csv")
OUTPUT_PATH = Path("dataset/raw/d4_hinglish.csv")


def devanagari_to_roman(text: str) -> str:
    """
    Transliterate Devanagari script text into Roman script, then clean
    it up to look like CASUAL Hinglish texting rather than academic
    ITRANS notation.

    Raw ITRANS output uses conventions no real person types with, e.g.
    capital letters for long vowels/retroflex sounds ("KarIdArI") and
    "|" for sentence-ending punctuation. We lowercase everything and
    replace ITRANS-specific punctuation with normal punctuation, so the
    result resembles real informal Hinglish (e.g. "kharidari") instead.
    """
    try:
        raw = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    except Exception:
        return text  # fall back to original if transliteration fails on a given row

    cleaned = raw.lower()
    cleaned = cleaned.replace("|", ".")   # danda (sentence end) -> period
    cleaned = cleaned.replace("~", "")    # stray ITRANS diacritic marks
    cleaned = cleaned.replace(".n", "n")  # anusvara artifact cleanup (e.g. "jaaeM.N" -> "jaaen")

    import re
    cleaned = re.sub(r"[\u0900-\u097F]", "", cleaned)      # strip any leftover untransliterated Devanagari chars
    cleaned = re.sub(r"\.(?=[a-z])", "", cleaned)           # remove mid-word period artifacts (period followed directly by a letter, no space)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def main():
    df = pd.read_csv(INPUT_PATH)
    text_col = "message" if "message" in df.columns else df.columns[0]

    print(f"Transliterating {len(df)} Hindi rows into casual Roman-script Hinglish...")
    df["text"] = df[text_col].astype(str).apply(devanagari_to_roman)
    df["source"] = "transliterated_from_hindi_SYNTHETIC"

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows -> {OUTPUT_PATH}")
    print("\nSample transliteration:")
    for i in range(min(3, len(df))):
        print(f"  Original: {df[text_col].iloc[i]}")
        print(f"  Roman:    {df['text'].iloc[i]}\n")


if __name__ == "__main__":
    main()