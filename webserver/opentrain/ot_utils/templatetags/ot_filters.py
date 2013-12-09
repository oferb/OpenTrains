from django import template

import ot_utils.ot_utils

register = template.Library()

@register.filter(name="weekday")
def week_day(dt):
    return ot_utils.ot_utils.get_weekdayname(dt)

@register.filter(name="nicedate")
def nice_date(dt):
    return ot_utils.ot_utils.format_date(dt)

