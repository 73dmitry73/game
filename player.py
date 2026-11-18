import pygame
import settings

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.start_x = x
        self.start_y = y
        
        # 9-й спрайт — одиночный кадр покоя (idle)
        self.idle_image = settings.get_sprite_by_id(6)
        
        # Анимация бега: 14, 13, 14, 16
        self.run_frames = [
            settings.get_sprite_by_id(38),
            settings.get_sprite_by_id(39),
            settings.get_sprite_by_id(40),
            settings.get_sprite_by_id(39)
        ]
        
        # Анимация удара: 10, 11
        self.attack_frames = [
            settings.get_sprite_by_id(7),
            settings.get_sprite_by_id(8)
        ]
        
        self.current_frame = 0
        self.animation_speed = 0.15 
        self.attack_speed = 0.20     
        
        # Состояния персонажа
        self.is_attacking = False
        
        # --- СОСТОЯНИЯ УРОНА И МИГАНИЯ ---
        self.is_hurt = False          # Находится ли в процессе отбрасывания
        self.hurt_timer = 0           # Таймер неуязвимости (в кадрах)
        self.flash_timer = 0          # Таймер для переключения видимости при мигании
        self.visible = True           # Рисовать ли спрайт в текущем кадре
        
        # --- СИСТЕМА ДВОЙНОГО ПРЫЖКА ---
        self.max_jumps = 2            # Всего прыжков доступно (1 обычный + 1 двойной)
        self.jumps_left = self.max_jumps
        
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        """Возвращает игрока на начальную точку"""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.is_attacking = False
        self.is_hurt = False
        self.hurt_timer = 0
        self.visible = True
        self.jumps_left = self.max_jumps

    def attack(self):
        """Запускает анимацию атаки, если персонаж управлем"""
        if not self.is_attacking and not self.is_hurt:
            self.is_attacking = True
            self.current_frame = 0

    def take_damage(self, source_x):
        """Вызывается при получении урона от источника с координатами source_x"""
        if self.hurt_timer > 0: 
            return # Если уже неуязвим — игнорируем урон
            
        self.is_hurt = True
        self.is_attacking = False # Прерываем атаку при получении урона
        self.hurt_timer = 60       # 1 секунда неуязвимости (при 60 FPS)
        
        # Отбрасывание: определяем, с какой стороны враг
        if self.rect.centerx < source_x:
            self.vel_x = -4 # Враг справа -> летим влево
            self.facing_right = True
        else:
            self.vel_x = 4  # Враг слева -> летим вправо
            self.facing_right = False
            
        self.vel_y = -6     # Немного подбрасываем вверх

    def jump(self):
        """Логика совершения прыжка (включая двойной)"""
        if self.is_hurt:
            return
            
        if self.jumps_left > 0:
            self.vel_y = -11
            self.jumps_left -= 1
            self.on_ground = False

    def update(self, platforms, deadly_blocks):
        # Если упали в бездну
        if self.rect.y > settings.VIRTUAL_HEIGHT + 100:
            self.reset_position()
            return

        # Восстановление прыжков, если стоим на земле
        if self.on_ground:
            self.jumps_left = self.max_jumps

        # --- ОБРАБОТКА ТАЙМЕРОВ УРОНА ---
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            
            # Логика мигания: каждые 5 кадров инвертируем видимость
            self.flash_timer += 1
            if self.flash_timer >= 5:
                self.visible = not self.visible
                self.flash_timer = 0
                
            # Через 15 кадров (~0.25 сек) возвращаем игроку управление по оси X
            if self.is_hurt and self.hurt_timer < 45:
                self.is_hurt = False
                self.vel_x = 0
        else:
            self.visible = True # Гарантируем видимость, когда неуязвимость спала

        # --- ЛОГИКА АНИМАЦИИ ---
        if self.is_attacking:
            self.current_frame += self.attack_speed
            if self.current_frame >= len(self.attack_frames):
                self.is_attacking = False  
                self.current_frame = 0
                base_image = self.idle_image
            else:
                base_image = self.attack_frames[int(self.current_frame)]
        else:
            if self.vel_x == 0:
                base_image = self.idle_image
            else:
                self.current_frame += self.animation_speed
                if self.current_frame >= len(self.run_frames):
                    self.current_frame = 0
                base_image = self.run_frames[int(self.current_frame)]

        # --- ПОВОРОТ СПРАЙТА ---
        if not self.is_attacking and not self.is_hurt: 
            if self.vel_x > 0: self.facing_right = True
            elif self.vel_x < 0: self.facing_right = False

        if not self.facing_right:
            self.image = pygame.transform.flip(base_image, True, False)
        else:
            self.image = base_image

        # --- ФИЗИКА ---
        self.vel_y += 0.8
        if self.vel_y > 12: self.vel_y = 12

        current_vel_x = self.vel_x

        self.rect.x += current_vel_x
        self.collide(current_vel_x, 0, platforms)

        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide(0, self.vel_y, platforms)

    def collide(self, vel_x, vel_y, platforms):
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                if vel_x > 0: self.rect.right = platform.rect.left
                if vel_x < 0: self.rect.left = platform.rect.right
                if vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
