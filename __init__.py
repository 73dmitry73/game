from .patrol_enemy import PatrolEnemy
from .charger_enemy import ChargerEnemy
from .patrol2_enemy import Patrol2Enemy  
from .boss_car import BossCar  # <-- ИЗМЕНЕНО: Теперь импортируем из локального файла boss_car

def create_enemy(enemy_type, x, y):
    enemy = None
    
    if enemy_type in ("Enemy", "Eneme", "PatrolEnemy"):
        enemy = PatrolEnemy(x, y)
    elif enemy_type == "ChargerEnemy":
        enemy = ChargerEnemy(x, y)
    elif enemy_type == "BossCar":  
        enemy = BossCar(x, y)
    elif enemy_type in ("patrol2enemy", "Patrol2Enemy"):  
        enemy = Patrol2Enemy(x, y)
        
    if enemy:
        enemy.enemy_type = enemy_type  
        return enemy

    print(f"[ПРЕДУПРЕЖДЕНИЕ] Неизвестный тип врага: {enemy_type}")
    return None
