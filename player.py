import pygame
import settings

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.start_x = x
        self.start_y = y
        
        # ЗАМЕНИТЕ НОМЕРА НА ВАШИ 4 ТАЙЛА ДЛЯ КАЖДОГО КАДРА (Верх-Лев, Верх-Прав, Низ-Лев, Низ-Прав)
                # 8 кадров анимации покоя (idle) размером 64x64
        self.idle_frames = [
            settings.get_64x64_sprite(163, 164, 195, 196), # Кадр 1
            settings.get_64x64_sprite(165, 166, 197, 198), # Кадр 2
            settings.get_64x64_sprite(167, 168, 199, 200), # Кадр 3
            settings.get_64x64_sprite(227, 228, 259, 260), # Кадр 4
            settings.get_64x64_sprite(229, 230, 261, 262), # Кадр 5
            settings.get_64x64_sprite(231, 232, 263, 264), # Кадр 6
            settings.get_64x64_sprite(291, 292, 323, 324), # Кадр 7
            settings.get_64x64_sprite(293, 294, 325, 326), # Кадр 8
        ]

        
        self.run_frames = [
            settings.get_96x64_sprite(353, 354, 355, 385, 386, 387), # Кадр 1
            settings.get_96x64_sprite(356, 357, 358, 388, 389, 390), # Кадр 2
            settings.get_96x64_sprite(359, 360, 361, 391, 392, 393), # Кадр 3
            settings.get_96x64_sprite(362, 363, 364, 394, 395, 396), # Кадр 4
            settings.get_96x64_sprite(365, 366, 367, 397, 398, 399), # Кадр 5
            settings.get_96x64_sprite(368, 369, 370, 400, 401, 402), # Кадр 6
            settings.get_96x64_sprite(371, 372, 373, 403, 404, 405), # Кадр 7
            settings.get_96x64_sprite(374, 375, 376, 406, 407, 408), # Кадр 8
        ]


        
        # Анимация удара
        self.attack_frames = [
            settings.get_64x64_sprite(9, 10, 41, 42),
            settings.get_64x64_sprite(11, 12, 43, 44)
        ]
        
        # ... остальной код __init__ без изменений ...

        
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
        
        self.image = self.idle_frames[0]

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        """Возвращает игрока на начальную точку"""
        self.rect.x = self.start_x
        self.rect.y = self.start_y - 32
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
                base_image = self.idle_frames[0]
            else:
                base_image = self.attack_frames[int(self.current_frame)]

        else:
            if self.vel_x == 0:
                self.current_frame += self.animation_speed
                if self.current_frame >= len(self.idle_frames):
                    self.current_frame = 0
                base_image = self.idle_frames[int(self.current_frame)]
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
