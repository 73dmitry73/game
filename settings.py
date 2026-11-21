# settings.py
import pygame
import os

# РЕАЛЬНЫЕ ФИЗИЧЕСКИЕ РАЗМЕРЫ ОКНА (могут меняться в меню графики)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ВНУТРЕННЕЕ 8-БИТНОЕ РАЗРЕШЕНИЕ (игра рендерится сюда, пиксели будут крупными)
VIRTUAL_WIDTH = 400
VIRTUAL_HEIGHT = 300

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

spritesheet = None
spritesheet_2 = None
TILE_SIZE = 32

def init_spritesheet(folder="sprites", filename="sp1"):
    global spritesheet, spritesheet_2
    if not os.path.exists(folder):
        os.makedirs(folder)
    full_path = os.path.join(folder, filename)
    if not os.path.exists(full_path):
        full_path = os.path.join(folder, filename + ".png")

    if os.path.exists(full_path):
        try:
            spritesheet = pygame.image.load(full_path).convert_alpha()
            print(f"[УСПЕХ] Файл '{filename}' успешно найден и загружен!")
        except pygame.error as e:
            print(f"[ОШИБКА] Ошибка загрузки: {e}")
    else:
        # Заглушка срабатывает только если sp1 не найден
        spritesheet = pygame.Surface((128, 128), pygame.SRCALPHA)
        for i in range(3): pygame.draw.rect(spritesheet, (0, 0, 255 - i*40), (i*32, 96, 32, 32))
        pygame.draw.rect(spritesheet, (139, 69, 19), (96, 96, 32, 32))

    # Загружаем второй спрайт-лист (sp3.png)
    path_2 = os.path.join(folder, "sp3.png")
    if os.path.exists(path_2):
        try:
            spritesheet_2 = pygame.image.load(path_2).convert_alpha()
            print("[УСПЕХ] Второй спрайт-лист 'sp3.png' загружен!")
        except pygame.error as e:
            print(f"[ОШИБКА] Ошибка загрузки sp3: {e}")


def get_sprite_by_id(tile_id):
    # Выбираем лист: от 1025 и выше берется из sp3.png
    if tile_id >= 1025 and spritesheet_2 is not None:
        active_sheet = spritesheet_2
        idx = tile_id - 1025
    else:
        active_sheet = spritesheet
        idx = tile_id - 1

    if active_sheet is not None:
        try:
            tiles_per_row = active_sheet.get_width() // TILE_SIZE
            tile_x = (idx % tiles_per_row) * TILE_SIZE
            tile_y = (idx // tiles_per_row) * TILE_SIZE
            return active_sheet.subsurface((tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        except Exception:
            pass
    image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    return image


import json

def get_64x64_sprite(tl_id, tr_id, bl_id, br_id):
    """Склеивает 4 тайла 32x32 в один спрайт 64x64"""
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    surf.blit(get_sprite_by_id(tl_id), (0, 0))
    surf.blit(get_sprite_by_id(tr_id), (32, 0))
    surf.blit(get_sprite_by_id(bl_id), (0, 32))
    surf.blit(get_sprite_by_id(br_id), (32, 32))
    return surf
    
def get_96x64_sprite(tl, tm, tr, bl, bm, br):
    """Склеивает 6 тайлов 32x32 в один спрайт 96x64"""
    surf = pygame.Surface((96, 64), pygame.SRCALPHA)
    surf.blit(get_sprite_by_id(tl), (0, 0))
    surf.blit(get_sprite_by_id(tm), (32, 0))
    surf.blit(get_sprite_by_id(tr), (64, 0))
    surf.blit(get_sprite_by_id(bl), (0, 32))
    surf.blit(get_sprite_by_id(bm), (32, 32))
    surf.blit(get_sprite_by_id(br), (64, 32))
    return surf



# settings.py (замените функцию load_level)
def load_level(filename="level.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            tile_layers = []
            objects_list = []
            image_layers = []
            map_props = {}

            for p in data.get("properties", []):
                map_props[p["name"]] = p["value"]
            
            for layer in data["layers"]:
                # Пропускаем скрытые в Tiled слои
                if not layer.get("visible", True):
                    continue

                if layer["type"] == "tilelayer":
                    width = layer["width"]
                    height = layer["height"]
                    tile_ids = layer["data"]
                    layer_name = layer.get("name", "")
                    
                    current_layer_grid = []
                    for r in range(height):
                        current_layer_grid.append(tile_ids[r * width : (r + 1) * width])
                    
                    tile_layers.append((layer_name, current_layer_grid))
                
                # --- ОБРАБОТКА СЛОЯ ИЗОБРАЖЕНИЯ ---
                elif layer["type"] == "imagelayer":
                    image_layers.append({
                        "name": layer.get("name", ""),
                        "image": layer.get("image", ""),
                        "x": layer.get("x", 0) + layer.get("offsetx", 0),
                        "y": layer.get("y", 0) + layer.get("offsety", 0),
                        "parallax_x": layer.get("parallaxx", 1.0),
                        "parallax_y": layer.get("parallaxy", 1.0)
                    })

                
                elif layer["type"] == "objectgroup":
                    for obj in layer["objects"]:
                        properties = obj.get("properties", {})
                        props_dict = {}
                        if isinstance(properties, list):
                            for p in properties:
                                props_dict[p["name"]] = p["value"]
                        elif isinstance(properties, dict):
                            props_dict = properties

                        objects_list.append({
                            "name": obj.get("name", ""),
                            "x": obj["x"],
                            "y": obj["y"],
                            "width": obj.get("width", 32),
                            "height": obj.get("height", 32),
                            "target_level": props_dict.get("target_level", ""),
                        })

            return tile_layers, objects_list, image_layers, map_props
    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить уровень: {e}")
        return [], [], [], {}
