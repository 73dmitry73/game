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
TILE_SIZE = 32

def init_spritesheet(folder="sprites", filename="sp1"):
    global spritesheet
    if not os.path.exists(folder):
        os.makedirs(folder)
    full_path = os.path.join(folder, filename)
    if not os.path.exists(full_path):
        full_path = os.path.join(folder, filename + ".png")

    if os.path.exists(full_path):
        try:
            spritesheet = pygame.image.load(full_path).convert_alpha()
            print(f"[УСПЕХ] Файл '{filename}' успешно найден и загружен!")
            return
        except pygame.error as e:
            print(f"[ОШИБКА] Ошибка загрузки: {e}")
            
    # Заглушка
    spritesheet = pygame.Surface((128, 128), pygame.SRCALPHA)
    for i in range(3): pygame.draw.rect(spritesheet, (0, 0, 255 - i*40), (i*32, 96, 32, 32))
    pygame.draw.rect(spritesheet, (139, 69, 19), (96, 96, 32, 32))

def get_sprite_by_id(tile_id):
    if spritesheet is not None:
        try:
            tiles_per_row = spritesheet.get_width() // TILE_SIZE
            idx = tile_id - 1
            tile_x = (idx % tiles_per_row) * TILE_SIZE
            tile_y = (idx // tiles_per_row) * TILE_SIZE
            return spritesheet.subsurface((tile_x, tile_y, TILE_SIZE, TILE_SIZE))
        except Exception:
            pass
    image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    return image

import json


def load_level(filename="level.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            tile_layers = []  # Список всех слоев тайлов
            objects_list = []
            
            for layer in data["layers"]:
                if layer["type"] == "tilelayer":
                    width = layer["width"]
                    height = layer["height"]
                    tile_ids = layer["data"]
                    
                    # Создаем чистую матрицу для конкретного слоя
                    current_layer_grid = []
                    for r in range(height):
                        current_layer_grid.append(tile_ids[r * width : (r + 1) * width])
                    
                    tile_layers.append(current_layer_grid)
                
                # settings.py (Внутри функции load_level)
                elif layer["type"] == "objectgroup":
                    for obj in layer["objects"]:
                        # Считываем кастомные свойства, если они есть
                        properties = obj.get("properties", {})
                        # Конвертируем список свойств Tiled в удобный словарь dict
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
                            "target_level": props_dict.get("target_level", ""), # Куда телепортировать
                        })

                        
            return tile_layers, objects_list
    except Exception as e:
        print(f"[ОШИБКА] Не удалось загрузить уровень: {e}")
        return [], []
