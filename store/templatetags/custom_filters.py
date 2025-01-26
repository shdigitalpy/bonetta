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
def truncate_each_word_with_ellipsis(value, length=5):
    """
    Truncate each word in the input string to the specified length and append ellipsis 
    if the word exceeds the given length.
    """
    if not isinstance(value, str):
        return value
    truncated_words = [
        word if len(word) <= int(length) else f"{word[:int(length)]}..."
        for word in value.split()
    ]
    return " ".join(truncated_words)