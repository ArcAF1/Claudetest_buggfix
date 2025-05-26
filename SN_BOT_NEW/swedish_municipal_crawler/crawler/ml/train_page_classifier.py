from pathlib import Path

from .page_classifier import PageClassifier


def main() -> None:
    # Minimal example data; replace with real labeled pages for better accuracy
    texts = [
        "Timtaxa för livsmedelskontroll är 1400 kr per timme.",
        "Kommunfullmäktige beslutade om taxor för bygglov.",
        "Välkommen till vår kommunala hemsida utan relevanta avgifter.",
        "Detta är en kontaktsida för invånare.",
    ]
    labels = [1, 1, 0, 0]

    model = PageClassifier()
    model.train(texts, labels)
    print(f"Model trained and saved to {model.model_path}")


if __name__ == "__main__":
    main()
