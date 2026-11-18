# sheet_config.py

# Списки ID для физических свойств тайлов
SOLID_TILES = {34}      # Твердые блоки
DEADLY_TILES = {}       # Смертельные блоки
PORTAL_TILES = {71}       # Оставляем пустым, так как порталы теперь обрабатываются как объекты Tiled

def get_properties(tile_id):
    """Автоматически возвращает свойства тайла по его порядковому номеру"""
    return {
        "is_solid": tile_id in SOLID_TILES,
        "is_deadly": tile_id in DEADLY_TILES,
        "is_portal": tile_id in PORTAL_TILES 
    }
