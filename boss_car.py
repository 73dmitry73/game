import pygame
import settings

class BossCar(pygame.sprite.Sprite):
    def __init__(self, x, y, width=96, height=64):
        super().__init__()
        
        # === ТОЧНЫЕ ID ТАЙЛОВ ДЛЯ БОССА ===
        BOSS_FRAMES = [
            [73, 74, 75, 105, 106, 107]
        ]
        
        self.frames = []
        for group in BOSS_FRAMES:
            frame_surf = pygame.Surface((96, 64), pygame.SRCALPHA)
            tl = settings.get_sprite_by_id(group[0])
            tc = settings.get_sprite_by_id(group[1])
            tr = settings.get_sprite_by_id(group[2])
            bl = settings.get_sprite_by_id(group[3])
            bc = settings.get_sprite_by_id(group[4])
            br = settings.get_sprite_by_id(group[5])
            
            frame_surf.blit(tl, (0, 0))
            frame_surf.blit(tc, (32, 0))
            frame_surf.blit(tr, (64, 0))
            frame_surf.blit(bl, (0, 32))
            frame_surf.blit(bc, (32, 32))
            frame_surf.blit(br, (64, 32))
            
            if width != 96 or height != 64:
                frame_surf = pygame.transform.scale(frame_surf, (width, height))
            self.frames.append(frame_surf)

        self.current_frame = 0
        self.animation_speed = 0.1  
        self.image = self.frames[0]
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # === ФИКСАЦИЯ КРАЙНИХ ТОЧЕК МАРШРУТА ===
        self.start_x = x                 
        self.right_border = x            
        self.move_range = 416            
        self.left_border = x - self.move_range 
        
        self.start_y = y
        self.is_dead = False
        self.visible = True
        
        # === НАСТРОЙКИ ЗДОРОВЬЯ (HP) ===
        self.max_hp = 15                 # Увеличили здоровье босса до 15 ед.
        self.hp = self.max_hp
        self.hit_flash_timer = 0         # Таймер мигания при получении урона
        
        # Настройки физики скоростей
        self.max_speed = 8.0             
        self.current_speed = 0.0         
        
        # Направление движения (Изначально едет влево)
        self.facing_right = False         
        
        # Стейт-машина состояний
        self.STATE_MOVE = "move"
        self.STATE_CRASHED = "crashed"   # Состояние удара (экран трясется 2 секунды)
        self.STATE_WAIT = "wait"         # Состояние покоя после разворота (ждет 3 секунды)
        self.state = self.STATE_WAIT     
        
        # Длительность фаз таймера в кадрах (при 60 FPS)
        self.crash_duration = 120        # 2 секунды в стене при ударе
        self.wait_duration = 180         # 3 секунды ожидания перед стартом
        self.timer = self.wait_duration 

    def die(self, enemy_spawns=None):
        """Вызывается при атаке игрока по боссу"""
        if self.is_dead:
            return
            
        self.hp -= 1
        self.hit_flash_timer = 15        # Эффект мигания на 15 кадров (~0.25 сек)
        
        if self.hp <= 0:
            self.is_dead = True
            
            # Если передан список спавнов, навсегда удаляем точку возрождения босса
            if enemy_spawns is not None and (self.start_x, self.start_y) in enemy_spawns:
                enemy_spawns.remove((self.start_x, self.start_y))
                
            self.kill()


    def update(self, platforms):
        if self.is_dead:
            return

        self.rect.y = self.start_y

        # Обработка таймера мигания от получения повреждений
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            self.visible = (self.hit_flash_timer % 4 < 2)
        else:
            self.visible = True

        # === ЛОГИКА СОСТОЯНИЙ ===
        if self.state == self.STATE_CRASHED:
            self.current_speed = 0.0
            self.timer -= 1
            if self.timer <= 0:
                # 2 секунды тряски прошли -> разворачиваемся на месте и переходим к ожиданию
                self.facing_right = not self.facing_right
                self.state = self.STATE_WAIT
                self.timer = self.wait_duration
                
        elif self.state == self.STATE_WAIT:
            self.current_speed = 0.0
            self.timer -= 1
            if self.timer <= 0:
                # 3 секунды ожидания прошли -> начинаем плавно ехать вперед
                self.state = self.STATE_MOVE
                
        elif self.state == self.STATE_MOVE:
            # Вычисляем прогресс пути (от 0.0 до 1.0)
            distance_traveled = abs(self.rect.x - (self.right_border if not self.facing_right else self.left_border))
            progress = distance_traveled / self.move_range
            
            # Двухфазное динамическое ускорение
            if progress < 0.5:
                accel_rate = 0.02  # Медленный разгон в первой половине пути
            else:
                accel_rate = 0.55  # Резкое и агрессивное ускорение на финише

            if self.current_speed < self.max_speed:
                self.current_speed += accel_rate
            else:
                self.current_speed = self.max_speed

            # Логика перемещения и регистрации столкновения со стеной
            if not self.facing_right:
                # Движение ВЛЕВО
                self.rect.x -= self.current_speed
                if self.rect.x <= self.left_border:
                    self.rect.x = self.left_border
                    # Врезался: активируем фазу аварии и тряски экрана
                    self.state = self.STATE_CRASHED
                    self.timer = self.crash_duration
            else:
                # Движение ВПРАВО
                self.rect.x += self.current_speed
                if self.rect.x >= self.right_border:
                    self.rect.x = self.right_border
                    # Врезался: активируем фазу аварии и тряски экрана
                    self.state = self.STATE_CRASHED
                    self.timer = self.crash_duration

        # === АНИМАЦИЯ ===
        if self.state == self.STATE_MOVE:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
                
        base_image = self.frames[int(self.current_frame)]
        self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
