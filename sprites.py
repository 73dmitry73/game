# sprites.py
import pygame
import settings
import sheet_config

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_id, pos_x, pos_y):
        super().__init__()
        self.image = settings.get_sprite_by_id(tile_id)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        
        properties = sheet_config.get_properties(tile_id)
        self.is_solid = properties["is_solid"]
        self.is_deadly = properties["is_deadly"]
        self.is_portal = properties.get("is_portal", False)

class PortalTrigger(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, target_level):
        super().__init__()
        
        # Загружаем спрайт двери/портала (ID 72 из вашей sp1)
        # Если размеры объекта в Tiled больше 32x32, pygame автоматически растянет текстуру
        base_image = settings.get_sprite_by_id(72) 
        self.image = pygame.transform.scale(base_image, (width, height))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Имя JSON-файла уровня для загрузки
        self.target_level = target_level
class ShopSign(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, tile_groups):
        """
        tile_groups: список списков из 4 ID тайлов для каждого кадра анимации.
        Пример: [[левый_верх, правый_верх, левый_ниж, правый_ниж], [кадр2...]]
        """
        super().__init__()
        self.frames = []
        
        # Склеиваем тайлы 32x32 в кадры 64x64
        for group in tile_groups:
            frame_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            # Вырезаем кусочки
            tl = settings.get_sprite_by_id(group[0]) # top-left
            tr = settings.get_sprite_by_id(group[1]) # top-right
            bl = settings.get_sprite_by_id(group[2]) # bottom-left
            br = settings.get_sprite_by_id(group[3]) # bottom-right
            
            # Собираем вместе
            frame_surf.blit(tl, (0, 0))
            frame_surf.blit(tr, (32, 0))
            frame_surf.blit(bl, (0, 32))
            frame_surf.blit(br, (32, 32))
            
            # Если в Tiled размеры объекта изменены, растягиваем кадр
            if width != 64 or height != 64:
                frame_surf = pygame.transform.scale(frame_surf, (width, height))
            self.frames.append(frame_surf)
            
        self.current_frame = 0
        self.animation_speed = 0.1  # Скорость анимации вывески
        self.image = self.frames[0]
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        # Прокрутка анимации по кругу
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]

import pygame
import settings
import math


