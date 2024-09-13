# app_name/templatetags/custom_filters.py

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
