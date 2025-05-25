class Item(dict):
    """Minimal stand-in for scrapy.Item"""
    pass

class Field:
    """Placeholder for scrapy.Field"""
    def __init__(self, *args, **kwargs):
        pass

from .exceptions import DropItem
