# enemies/charger_enemy.py
import pygame
import settings

class ChargerEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Спрайты анимации покоя (ID 5 и 37)
        self.idle_frames = [
            settings.get_sprite_by_id(5),
            settings.get_sprite_by_id(37)
        ]
        # Спрайты рывка
        self.charge_frames = [
            settings.get_sprite_by_id(5),
            settings.get_sprite_by_id(37)
        ]
        
        # Спрайты смерти (ID 9 и 41)
        self.death_frames = [
            settings.get_sprite_by_id(9),
            settings.get_sprite_by_id(41)
        ]
        
        self.current_frame = 0
        self.animation_speed = 0.15
        self.death_speed = 0.10     
        
        self.start_x = x
        self.start_y = y
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Состояния
        self.vel_x = 0
        self.vel_y = 0
        self.facing_right = True
        self.is_dead = False        
        self.has_triggered = False  # Сорвался ли в атаку
        
        # Дистанция агро по оси X
        self.trigger_distance = 120
        self.charge_speed = 5.0     
        
        self.visible = True
        self.flash_timer = 0

    def die(self):
        """Запускает процесс анимации смерти при ударе игрока"""
        if not self.is_dead:
            self.is_dead = True
            self.current_frame = 0  
            self.flash_timer = 0

    def update(self, platforms):
        import __main__
        player = getattr(__main__, 'player', None)

        # --- ЛОГИКА ДЛЯ МЕРТВОГО ВРАГА ---
        if self.is_dead:
            self.vel_x = 0
            self.flash_timer += 1
            if self.flash_timer >= 4:
                self.visible = not self.visible
                self.flash_timer = 0
            
            self.current_frame += self.death_speed
            if self.current_frame >= len(self.death_frames):
                self.kill()  
                return
                
            base_image = self.death_frames[int(self.current_frame)]
            self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
            return

        # --- ЛОГИКА ДЛЯ ЖИВОГО ВРАГА ---
                # --- ЛОГИКА ДЛЯ ЖИВОГО ВРАГА ---
        if not self.has_triggered and player:
            # Считаем расстояние по горизонтали X
            dx = player.rect.centerx - self.rect.centerx
            
            # Проверяем, находится ли центр игрока строго внутри высоты этого врага
            is_on_exact_line = self.rect.top <= player.rect.centery <= self.rect.bottom
            
            # Враг реагирует, только если игрок на одной линии по центру Y
            # и расстояние по горизонтали X укладывается в trigger_distance
            if is_on_exact_line and abs(dx) <= self.trigger_distance:
                self.has_triggered = True
                self.current_frame = 0  
                # Определяем направление рывка
                self.facing_right = dx > 0
                self.vel_x = self.charge_speed if self.facing_right else -self.charge_speed

        # Движение и прокрутка кадров
        if self.has_triggered:
            self.rect.x += self.vel_x
            
            # Анимация быстрого полета/рывка
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.charge_frames):
                self.current_frame = 0
            base_image = self.charge_frames[int(self.current_frame)]
            
            # Самоудаление, если улетел далеко за пределы экрана
            camera = getattr(__main__, 'camera', None)
            if camera:
                if self.rect.x < -camera.offset_x - 200 or self.rect.x > -camera.offset_x + settings.VIRTUAL_WIDTH + 200:
                    self.kill()
                    return
        else:
            # Стоит на месте, гравитация удерживает на платформе до рывка
            self.vel_y += 0.8
            if self.vel_y > 12: self.vel_y = 12
            self.rect.y += self.vel_y
            for platform in platforms:
                if pygame.sprite.collide_rect(self, platform):
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
            
            # --- АНИМАЦИЯ ПОКОЯ ---
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.idle_frames):
                self.current_frame = 0
            base_image = self.idle_frames[int(self.current_frame)]

        # Поворот спрайта
        self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
