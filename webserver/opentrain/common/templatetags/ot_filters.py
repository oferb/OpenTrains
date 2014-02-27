from django import template
from django.utils.translation import ugettext as _

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
    if d == 0: return _('Backward')
    if d == 1: return _('Forward')
    return '???'

@register.filter(name="shapes_to_points")
def shapes_to_points(shapes):
    return "[" + ",".join(["[%s,%s]" % (shape.shape_pt_lat,shape.shape_pt_lon) for shape in shapes]) + "]"
    
@register.filter(name="truefalse")
def truefalse(val):
    return _('true') if val else _('false')
        

from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

@stringfilter
def spacify(value, autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(esc(value).replace(' ','&nbsp;'))

spacify.needs_autoescape = True
register.filter(spacify)

