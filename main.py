# main.py
# main.py
import asyncio
import pygame
import sys
import audio  
import settings
import sheet_config
from sprites import Tile, PortalTrigger, ShopSign  # Добавлен ShopSign в импорт
from player import Player    
from ui import Button
from effects import init_effects_sheet, HitEffect
from enemies import create_enemy  

pygame.init()
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("8-Bit Ninja Platformer")
clock = pygame.time.Clock()

virtual_screen = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))

settings.init_spritesheet(folder="sprites", filename="sp1") 
init_effects_sheet(folder="sprites", filename="sp2")

game_state = "MAIN_MENU"
START_LEVEL = "level.json" 

# =========================================================================
# === НАСТРОЙКА АНИМАЦИИ ВЫВЕСКИ (МАТРИЦА НОМЕРОВ ТАЙЛОВ ИЗ TILED / SP1) ===
# Каждая строчка — это один кадр 64х64, собранный из четырех тайлов 32х32.
# Формат: [Вверх-Влево, Вверх-Вправо, Вниз-Влево, Вниз-Вправо]
# ЗАМЕНИТЕ ЭТИ ЧИСЛА НА РЕАЛЬНЫЕ НОМЕРА ВАШИХ ТАЙЛОВ:
SIGN_ANIMATION_DATA = [    # Кадр 1 вашей анимации вывески,     # Кадр 2 вашей анимации вывески
    [9, 10, 11, 12],
    [9, 10, 12, 12]    # Кадр 3 (если нужно, можно убрать или добавить еще)
]
# =========================================================================

class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0  
        self.width = width
        self.height = height

    def update(self, target, level_data_ref):
        self.offset_x = -(target.rect.centerx - int(settings.VIRTUAL_WIDTH / 2))
        if self.offset_x > 0: self.offset_x = 0
        max_offset_x = -(self.width - settings.VIRTUAL_WIDTH)
        if self.offset_x < max_offset_x: self.offset_x = max_offset_x

        level_height_pixels = len(level_data_ref) * 32 if level_data_ref else settings.VIRTUAL_HEIGHT
        if level_height_pixels <= settings.VIRTUAL_HEIGHT:
            self.offset_y = (settings.VIRTUAL_HEIGHT - level_height_pixels) // 2
        else:
            self.offset_y = -(target.rect.centery - int(settings.VIRTUAL_HEIGHT / 2))
            if self.offset_y > 0: self.offset_y = 0
            max_offset_y = -(level_height_pixels - settings.VIRTUAL_HEIGHT)
            if self.offset_y < max_offset_y: self.offset_y = max_offset_y


# --- ГЛОБАЛЬНЫЕ ГРУППЫ СПРАЙТОВ ---
all_sprites = pygame.sprite.Group()
foreground_sprites = pygame.sprite.Group() 
platforms = pygame.sprite.Group()
deadly_blocks = pygame.sprite.Group()
portals = pygame.sprite.Group()         
enemies_group = pygame.sprite.Group()  
effects_group = pygame.sprite.Group() 
signs_group = pygame.sprite.Group()  
bg_images = []   # Новая группа для вывесок магазинов
enemy_spawns = [] 
level_objects = []
level_data = []

def load_level_map(filename):
    global level_data, level_objects, enemy_spawns, bg_images
    
    print(f"[ИНФО] Загрузка уровня: {filename}")
    
    all_sprites.empty()
    foreground_sprites.empty()
    platforms.empty()
    deadly_blocks.empty()
    portals.empty()
    enemies_group.empty()
    effects_group.empty()
    signs_group.empty()
    enemy_spawns.clear()
    bg_images.clear()  # <-- Очищаем старые фоновые картинки при смене уровня
    
    tile_layers, level_objects, image_layers, map_props = settings.load_level(filename)
    if not tile_layers and not image_layers:
        print(f"[ОШИБКА] Не удалось загрузить карту: {filename}")
        return

    audio.play_level_music(map_props)


    # Загружаем картинки слоев изображений
        # Загружаем картинки слоев изображений
    for img_data in image_layers:
        img_path = img_data["image"]
        if img_path:
            try:
                loaded_img = pygame.image.load(img_path).convert_alpha()
                bg_images.append((
                    loaded_img, 
                    img_data["x"], 
                    img_data["y"], 
                    img_data.get("parallax_x", 0.3), 
                    img_data.get("parallax_y", 0.3)
                ))
            except Exception as e:
                print(f"[ОШИБКА] Не удалось загрузить фон '{img_path}': {e}")


    # Берем сетку первого слоя для расчета границ камеры (индекс [1] в кортеже)
    level_data = tile_layers[0][1] if tile_layers else []
    
    level_width_pixels = len(level_data[0]) * 32 if level_data else settings.VIRTUAL_WIDTH
    level_height_pixels = len(level_data) * 32 if level_data else settings.VIRTUAL_HEIGHT
    
    camera.width = level_width_pixels
    camera.height = level_height_pixels 

    player_spawn_x, player_spawn_y = 100, 100

    # 1. Расставляем объекты (остается без изменений)
    for obj in level_objects:
        if obj["name"] == "Player":
            player_spawn_x = int(obj["x"])
            player_spawn_y = int(obj["y"])
        elif obj["name"] == "Portal":
            portal = PortalTrigger(
                int(obj["x"]), int(obj["y"]), 
                int(obj["width"]), int(obj["height"]), 
                obj["target_level"]
            )
            portals.add(portal)
        elif obj["name"] == "ShopSign":
            sign = ShopSign(
                int(obj["x"]), int(obj["y"]), 
                int(obj["width"]), int(obj["height"]), 
                SIGN_ANIMATION_DATA
            )
            signs_group.add(sign)
        elif obj["name"] != "":  
            ex, ey = int(obj["x"]), int(obj["y"])
            enemy_spawns.append((ex, ey))
            enemy = create_enemy(obj["name"], ex, ey)
            if enemy: enemies_group.add(enemy)

    # 2. Строим тайлы слоев с учетом имени слоя
    for layer_name, layer_grid in tile_layers:
        for row_idx, row_list in enumerate(layer_grid):
            for col_idx, tile_id in enumerate(row_list):
                if tile_id == 0: continue
                
                x = col_idx * 32
                y = row_idx * 32
                tile = Tile(tile_id, x, y)
                
                # Если слой называется "верхний декор", кладем в группу переднего плана
                if layer_name == "верхний декор":
                    foreground_sprites.add(tile)
                else:
                    all_sprites.add(tile)
                
                if tile.is_solid:
                    platforms.add(tile)
                if tile.is_deadly:
                    deadly_blocks.add(tile)

    player.start_x = player_spawn_x
    player.start_y = player_spawn_y
    player.reset_position()


# --- Инициализация камеры и игрока ---
player = Player(100, 100)
camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)

# Загружаем стартовый уровень при первом запуске
load_level_map(START_LEVEL)

def start_game(): 
    global game_state
    game_state = "GAME"
    load_level_map(START_LEVEL)

def open_graphics_menu(): global game_state; game_state = "GRAPHICS_MENU"
def back_to_menu(): global game_state; game_state = "MAIN_MENU"
def change_res_800(): global screen; screen = pygame.display.set_mode((800, 600))
def change_res_1024(): global screen; screen = pygame.display.set_mode((1024, 768))

menu_buttons = [
    Button("Играть", 300, 200, 200, 50, start_game),
    Button("Графика", 300, 280, 200, 50, open_graphics_menu),
    Button("Выход", 300, 360, 200, 50, sys.exit)
]

graphics_buttons = [
    Button("800x600", 250, 200, 300, 50, change_res_800),
    Button("1024x768", 250, 280, 300, 50, change_res_1024),
    Button("Назад", 250, 380, 300, 50, back_to_menu)
]

async def main():
    global game_state, screen
    running = True
    while running:
        current_win_width = screen.get_width()
        current_win_height = screen.get_height()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "MAIN_MENU":
                for btn in menu_buttons:
                    btn.handle_event(event)
            elif game_state == "GRAPHICS_MENU":
                for btn in graphics_buttons:
                    btn.handle_event(event)
                
            elif game_state == "GAME":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        player.vel_x = -3
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        player.vel_x = 3
                    if event.key in (pygame.K_SPACE, pygame.K_w):
                        player.jump()
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MAIN_MENU" 
                    
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a) and player.vel_x < 0:
                        player.vel_x = 0
                    if event.key in (pygame.K_RIGHT, pygame.K_d) and player.vel_x > 0:
                        player.vel_x = 0

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not player.is_attacking:
                        player.attack()
                        fx = HitEffect(player, [1, 2, 3], player.facing_right)
                        effects_group.add(fx)

        virtual_screen.fill(settings.BLACK)
        screen.fill(settings.BLACK)

        if game_state == "MAIN_MENU":
            for btn in menu_buttons: 
                btn.rect.centerx = current_win_width // 2
                btn.draw(screen)
        elif game_state == "GRAPHICS_MENU":
            for btn in graphics_buttons: 
                btn.rect.centerx = current_win_width // 2
                btn.draw(screen)
        elif game_state == "GAME":
            screen_left = -camera.offset_x
            screen_right = screen_left + settings.VIRTUAL_WIDTH
            
            for spawn_x, spawn_y in enemy_spawns:
                if spawn_x < screen_left - 32 or spawn_x > screen_right + 32:
                    already_exists = False
                    current_enemy_type = "Enemy" 
                    
                    for enemy in enemies_group:
                        if enemy.start_x == spawn_x and enemy.start_y == spawn_y:
                            already_exists = True
                            break
                            
                    if not already_exists:
                        for obj in level_objects:
                            if int(obj["x"]) == spawn_x and int(obj["y"]) == spawn_y:
                                current_enemy_type = obj["name"]
                                break
                                
                        new_enemy = create_enemy(current_enemy_type, spawn_x, spawn_y)
                        if new_enemy:
                            enemies_group.add(new_enemy)

            player.update(platforms, deadly_blocks)
            effects_group.update() 
            enemies_group.update(platforms) 
            signs_group.update()
            
            hit_portals = pygame.sprite.spritecollide(player, portals, False)
            for p in hit_portals:
                if p.target_level:  
                    load_level_map(p.target_level)
                    break  

            for fx in effects_group:
                hit_enemies = pygame.sprite.spritecollide(fx, enemies_group, False)
                for enemy in hit_enemies:
                    if hasattr(fx, 'hit_enemies'):
                        if not enemy.is_dead and enemy not in fx.hit_enemies:  
                            if enemy.__class__.__name__ == "BossCar":
                                enemy.die(enemy_spawns)
                            else:
                                enemy.die()        
                            fx.hit_enemies.append(enemy)
                    else:
                        if not enemy.is_dead:
                            if enemy.__class__.__name__ == "BossCar":
                                enemy.die(enemy_spawns)
                            else:
                                enemy.die()

            for enemy in enemies_group:
                if not enemy.is_dead and pygame.sprite.collide_rect(player, enemy):
                    player.take_damage(enemy.rect.centerx)
            
            if pygame.sprite.spritecollideany(player, deadly_blocks):
                player.reset_position()
                effects_group.empty()
                
            camera.update(player, level_data)
            shake_x = 0
            shake_y = 0
            for enemy in enemies_group:
                if hasattr(enemy, 'state') and enemy.state == "crashed":
                    import random
                    shake_x = random.randint(-4, 4)
                    shake_y = random.randint(-4, 4)

            # --- ВСТАВИТЬ ЭТОТ БЛОК ОТРИСОВКИ ФОНА СЮДА ---
            for bg_img, bg_x, bg_y, px, py in bg_images:
                virtual_screen.blit(bg_img, (bg_x + camera.offset_x * 0.1 + shake_x, bg_y + camera.offset_y * 0.1 + shake_y))

            # ---------------------------------------------

            for sprite in all_sprites:
                virtual_screen.blit(sprite.image, (sprite.rect.x + camera.offset_x + shake_x, sprite.rect.y + camera.offset_y + shake_y))

                
            for p in portals:
                virtual_screen.blit(p.image, (p.rect.x + camera.offset_x + shake_x, p.rect.y + camera.offset_y + shake_y))

            for sign in signs_group:
                virtual_screen.blit(sign.image, (sign.rect.x + camera.offset_x + shake_x, sign.rect.y + camera.offset_y + shake_y))

            for enemy in enemies_group:
                if enemy.visible:  
                    virtual_screen.blit(enemy.image, (enemy.rect.x + camera.offset_x + shake_x, enemy.rect.y + camera.offset_y + shake_y))

            if player.visible:
                virtual_screen.blit(player.image, (player.rect.x + camera.offset_x + shake_x, player.rect.y + camera.offset_y + shake_y))
            
            for fx in effects_group:
                virtual_screen.blit(fx.image, (fx.rect.x + camera.offset_x + shake_x, fx.rect.y + camera.offset_y + shake_y))
          
            for sprite in foreground_sprites:
                virtual_screen.blit(sprite.image, (sprite.rect.x + camera.offset_x + shake_x, sprite.rect.y + camera.offset_y + shake_y))
                
            for enemy in enemies_group:
                if hasattr(enemy, 'hp') and not enemy.is_dead:
                    bar_width = 200
                    bar_height = 10
                    bar_x = (settings.VIRTUAL_WIDTH - bar_width) // 2
                    bar_y = 15
                    
                    pygame.draw.rect(virtual_screen, settings.BLACK, (bar_x, bar_y, bar_width, bar_height))
                    current_bar_width = int(bar_width * (enemy.hp / enemy.max_hp))
                    pygame.draw.rect(virtual_screen, (200, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                    pygame.draw.rect(virtual_screen, (50, 200, 50), (bar_x, bar_y, current_bar_width, bar_height))
                    pygame.draw.rect(virtual_screen, settings.WHITE, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), 1)

            scaled_surface = pygame.transform.scale(virtual_screen, (current_win_width, current_win_height))
            screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()
        clock.tick(settings.FPS)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
