from django import template

import common.ot_utils

register = template.Library()

@register.filter(name="weekday")
def week_day(dt):
    return common.ot_utils.get_weekdayname(dt)

@register.filter(name="nicedate")
def nice_date(dt):
    return common.ot_utils.format_date(dt)

@register.filter(name="denorm_time")
def denorm_time(t):
    return common.ot_utils.denormalize_time_to_string(t)

@register.filter(name="direction_to_string")
def direction_to_string(d):
    if d == 0: return 'Backward'
    if d == 1: return 'Forward'
    return '???'

 