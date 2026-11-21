import pygame
import settings

class Patrol2Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.walk_frames = [
            settings.get_sprite_by_id(10),
            settings.get_sprite_by_id(42),
            settings.get_sprite_by_id(10),
            settings.get_sprite_by_id(42)
        ]
        
        self.death_frames = [
            settings.get_sprite_by_id(9),
            settings.get_sprite_by_id(41)
        ]
        
        self.current_frame = 0
        self.animation_speed = 0.1
        self.death_speed = 0.10     
        self.start_x = x
        self.start_y = y
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.pos_x = float(x)
        self.vel_x = 0.6
        self.vel_y = 0
        self.facing_right = True
        self.is_dead = False        
        
        self.visible = True
        self.flash_timer = 0

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.current_frame = 0  
            self.flash_timer = 0

    def update(self, platforms, player=None, camera=None):
        self.vel_y += 0.8
        if self.vel_y > 12: self.vel_y = 12
        
        self.rect.y += self.vel_y
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0

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

        self.pos_x += self.vel_x
        self.rect.x = round(self.pos_x)
        
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.pos_x = float(self.rect.x)
                    self.vel_x = -self.vel_x
                    self.facing_right = False
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.pos_x = float(self.rect.x)
                    self.vel_x = -self.vel_x
                    self.facing_right = True

        sensor_dist = 10 if self.facing_right else -10
        test_rect = pygame.Rect(self.rect.centerx + sensor_dist, self.rect.bottom + 1, 2, 2)
        
        on_edge = True
        for platform in platforms:
            if platform.rect.colliderect(test_rect):
                on_edge = False 
                break
                
        if on_edge:
            self.vel_x = -self.vel_x
            self.facing_right = not self.facing_right

        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.walk_frames):
            self.current_frame = 0
        base_image = self.walk_frames[int(self.current_frame)]
        self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)

        return

        # --- ЛОГИКА ДЛЯ ЖИВОГО ВРАГА ---
        self.rect.x += self.vel_x
        
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.vel_x = -self.vel_x
                    self.facing_right = False
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.vel_x = -self.vel_x
                    self.facing_right = True

        # Проверка края платформы
        sensor_dist = 10 if self.facing_right else -10
        test_rect = pygame.Rect(self.rect.centerx + sensor_dist, self.rect.bottom + 1, 2, 2)
        
        on_edge = True
        for platform in platforms:
            if platform.rect.colliderect(test_rect):
                on_edge = False 
                break
                
        if on_edge:
            self.vel_x = -self.vel_x
            self.facing_right = not self.facing_right

        # Анимация ходьбы
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.walk_frames):
            self.current_frame = 0
        base_image = self.walk_frames[int(self.current_frame)]
        self.image = base_image if self.facing_right else pygame.transform.flip(base_image, True, False)
