# __init__.py
def classFactory(iface):
    from .relation_manager import RelationManager
    return RelationManager(iface)