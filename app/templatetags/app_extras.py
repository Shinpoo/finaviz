from django import template

register = template.Library()
import humanize

def humanize_num(value):
    return humanize.intword(value)

def percent(value):
    if value is None:
        return "-"
    else:
        return round(value*100,2)

def capSize(value):
    if value is None:
        return "-"
    elif value >= 200*1e8:
        return "Mega Cap"
    elif value >= 10*1e8:
        return "Big Cap"
    elif value >= 2*1e8:
        return "Mid Cap"
    elif value >= 0.3*1e8:
        return "Small Cap"
    else:
        return "Micro Cap"


def volatility(value):
    if value is None:
        return "-"
    elif value >= 1.5:
        return "Very High"
    elif value >= 1.1:
        return "High"
    elif value >= 0.8:
        return "Average"
    elif value >= 0.5:
        return "Low"
    else:
        return "Very Low"


def payoutRatio(value):
    if value is None:
        return "-"
    elif value >= 1.2:
        return "Very High"
    elif value >= 0.75:
        return "High"
    elif value >= 0.6:
        return "Edging High"
    elif value >= 0.35:
        return "Low"
    else:
        return "Very Low"

register.filter("humanize_num", humanize_num)
register.filter("percent", percent)
register.filter("capSize", capSize)
register.filter("volatility", volatility)
register.filter("payoutRatio", payoutRatio)
