# audio.py
import pygame
import os

pygame.mixer.init()

# Отдельные каналы для 2-го и 3-го треков
second_track_channel = pygame.mixer.Channel(0)
third_track_channel = pygame.mixer.Channel(1)

def play_level_music(map_props):
    """Запускает до трех треков уровня одновременно с разной громкостью"""
    pygame.mixer.music.stop()
    second_track_channel.stop()
    third_track_channel.stop()

    # --- ТРЕК 1 (основная музыка) ---
    music1 = map_props.get("music", "")
    vol1 = float(map_props.get("music_vol", 0.5))

    if music1 and os.path.exists(music1):
        try:
            pygame.mixer.music.load(music1)
            pygame.mixer.music.set_volume(vol1)
            pygame.mixer.music.play(-1)
            print(f"[МУЗЫКА 1] Играет: {music1} (громкость: {vol1})")
        except Exception as e:
            print(f"[ОШИБКА] Трек 1 '{music1}': {e}")
    elif music1:
        print(f"[ОШИБКА] Файл не найден: {music1}")

    # --- ТРЕК 2 (например, дождь) ---
    music2 = map_props.get("music2", "")
    vol2 = float(map_props.get("music2_vol", 0.6))

    if music2 and os.path.exists(music2):
        try:
            snd2 = pygame.mixer.Sound(music2)
            snd2.set_volume(vol2)
            second_track_channel.play(snd2, loops=-1)
            print(f"[МУЗЫКА 2] Играет: {music2} (громкость: {vol2})")
        except Exception as e:
            print(f"[ОШИБКА] Трек 2 '{music2}': {e}")
    elif music2:
        print(f"[ОШИБКА] Файл не найден: {music2}")

    # --- ТРЕК 3 (например, ветер или гром) ---
    music3 = map_props.get("music3", "")
    vol3 = float(map_props.get("music3_vol", 0.1))

    if music3 and os.path.exists(music3):
        try:
            snd3 = pygame.mixer.Sound(music3)
            snd3.set_volume(vol3)
            third_track_channel.play(snd3, loops=-1)
            print(f"[МУЗЫКА 3] Играет: {music3} (громкость: {vol3})")
        except Exception as e:
            print(f"[ОШИБКА] Трек 3 '{music3}': {e}")
    elif music3:
        print(f"[ОШИБКА] Файл не найден: {music3}")
