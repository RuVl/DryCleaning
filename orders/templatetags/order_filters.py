from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
	"""Multiply the arg with the value"""
	try:
		return float(value) * float(arg)
	except (ValueError, TypeError):
		return value
