from datetime import timedelta
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def days_until_due(last_service, due_date):
    if last_service and due_date:
        today = timezone.now().date()  # Ensure `today` is a `date` object
        if isinstance(due_date, timezone.datetime):
            due_date = due_date.date()  # Convert `due_date` to a `date` if it's a `datetime`
        # Calculate the number of days until due_date
        days_remaining = (due_date - today).days
        return days_remaining
    return None

@register.filter
def anonymize_name(value, visible=3):
    """
    Anonymisiert jeden Teil des Namens, indem alle Buchstaben außer den ersten 
    und optional letzten Zeichen durch Punkte ersetzt werden.

    :param value: Der Name (String), der anonymisiert werden soll.
    :param visible: Anzahl der sichtbaren Buchstaben am Anfang (Standard: 1).
    :return: Der anonymisierte Name.
    """
    if not isinstance(value, str):
        return value  # Rückgabe des Originals, wenn keine Zeichenkette

    try:
        visible = int(visible)  # Sicherstellen, dass 'visible' eine Ganzzahl ist
    except ValueError:
        visible = 1  # Fallback auf Standardwert

    # Sicherstellen, dass 'visible' mindestens 1 ist
    if visible < 1:
        visible = 1

    # Verarbeitung: Jedes Wort anonymisieren
    anonymized_words = []
    for word in value.split():
        if len(word) <= visible:  # Wenn das Wort zu kurz ist, bleibt es bestehen
            anonymized_words.append(word)
        else:
            anonymized_words.append(f"{word[:visible]}{'*' * (len(word) - visible)}")

    return " ".join(anonymized_words)

@register.filter
def dict_item(dictionary, key):
    """ Custom template filter to safely access dictionary keys in Django templates. """
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}