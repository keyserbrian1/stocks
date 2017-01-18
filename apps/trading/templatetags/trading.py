from django import template

register = template.Library()


from django.contrib.humanize.templatetags.humanize import intcomma

@register.filter
def currency(dollars):
    print dollars
    if dollars is None:
        return "None"
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
