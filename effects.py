# effects.py
import pygame

# Размеры кадра спецэффекта теперь 96x32
effects_spritesheet = None
EFFECT_WIDTH = 96
EFFECT_HEIGHT = 32

def init_effects_sheet(folder="sprites", filename="sp2"):
    """Загружает текстуру спецэффектов"""
    global effects_spritesheet
    import os
    full_path = os.path.join(folder, filename + ".png")
    if os.path.exists(full_path):
        try:
            effects_spritesheet = pygame.image.load(full_path).convert_alpha()
            print(f"[УСПЕХ] Спрайт-лист эффектов '{filename}' успешно загружен!")
            return
        except pygame.error as e:
            print(f"[ОШИБКА] Не удалось загрузить эффекты: {e}")
    
    # Заглушка, если файл отсутствует (белый прямоугольник)
    effects_spritesheet = pygame.Surface((EFFECT_WIDTH, EFFECT_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(effects_spritesheet, (255, 255, 255), (0, 0, EFFECT_WIDTH, EFFECT_HEIGHT), 2)

def get_effect_sprite(tile_id):
    """Вырезает кадр эффекта по его порядковому номеру (с 1) размером 96x32"""
    if effects_spritesheet is not None:
        try:
            # Считаем, сколько тайлов шириной 96 пикселей помещается в одной строке картинки
            tiles_per_row = effects_spritesheet.get_width() // EFFECT_WIDTH
            idx = tile_id - 1
            x = (idx % tiles_per_row) * EFFECT_WIDTH
            y = (idx // tiles_per_row) * EFFECT_HEIGHT
            return effects_spritesheet.subsurface((x, y, EFFECT_WIDTH, EFFECT_HEIGHT))
        except Exception:
            pass
    return pygame.Surface((EFFECT_WIDTH, EFFECT_HEIGHT), pygame.SRCALPHA)


class HitEffect(pygame.sprite.Sprite):
    def __init__(self, target, frame_ids, facing_right):
        """
        target: объект (игрок или моб), к которому привязан эффект
        frame_ids: список порядковых номеров кадров
        facing_right: направление взгляда цели (True/False) для разворота эффекта
        """
        super().__init__()
        self.target = target
        self.facing_right = facing_right
        
        # Нарезаем кадры анимации размером 96x32
        self.frames = [get_effect_sprite(fid) for fid in frame_ids]
        self.current_frame = 0
        self.animation_speed = 0.25 # Скорость анимации эффекта
        
        # Берем именно ПЕРВЫЙ кадр [0] из списка и отражаем его, если нужно
        base_image = self.frames[0]
        self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
        
        self.rect = self.image.get_rect()
        self.update_position()
        
        # === СПИСОК ВРАГОВ, КОТОРЫХ ЭТОТ УДАР УЖЕ ЗАДЕЛ ===
        self.hit_enemies = []

    def update_position(self):
        """Центрирует прямоугольный эффект 96x32 относительно центра цели"""
        if self.target:
            self.rect.center = self.target.rect.center

    def update(self):
        # Эффект следует за целью, если она сдвинулась
        self.update_position()
        
        # Прокрутка анимации
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.kill() # Самоудаление из всех групп при завершении анимации
        else:
            base_image = self.frames[int(self.current_frame)]
            # === ИСПРАВЛЕНО: Теперь каждый новый кадр анимации тоже корректно отражается по горизонтали ===
            self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
