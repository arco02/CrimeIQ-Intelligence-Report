import re


def clean_text(text: str) -> str:

    text = str(text)

    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text


def normalize_city(city: str) -> str:

    if not city:
        return "Unknown"

    city = clean_text(city)

    return city.title()


def normalize_state(state: str) -> str:

    if not state:
        return "Unknown"

    state = clean_text(state)

    return state.title()


def normalize_crime_type(crime_type: str) -> str:

    if not crime_type:
        return "Unknown"

    crime_type = clean_text(crime_type)

    return crime_type.title()