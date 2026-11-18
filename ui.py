import pygame
import settings

class Button:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        # Подсветка кнопки при наведении мыши
        color = settings.LIGHT_GRAY if self.rect.collidepoint(mouse_pos) else settings.WHITE
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, settings.BLACK, self.rect, 2)
        
        text_surf = self.font.render(self.text, True, settings.BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()
