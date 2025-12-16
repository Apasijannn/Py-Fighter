import pygame
import sys
import math

pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 200, 100)
DARK_BLUE = (20, 45, 90)
BLUE = (40, 70, 130)
ORANGE = (255, 150, 80)
CYAN = (100, 200, 255)

class ModeButton:
    """
    Button untuk memilih mode game.
    
    Args:
        x: Posisi x button
        y: Posisi y button
        width: Lebar button
        height: Tinggi button
        text: Text yang ditampilkan
        mode: Mode yang dipilih ('pvp' atau 'ai')
    """
    
    def __init__(self, x, y, width, height, text, mode):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.mode = mode
        self.is_hovered = False
        self.hover_alpha = 0
        self.scale = 1.0
    
    def update(self):
        """Update animasi hover button"""
        if self.is_hovered:
            self.hover_alpha = min(255, self.hover_alpha + 20)
            self.scale = min(1.05, self.scale + 0.01)
        else:
            self.hover_alpha = max(0, self.hover_alpha - 20)
            self.scale = max(1.0, self.scale - 0.01)
    
    def draw(self, surface):
        """
        Render button ke surface.
        
        Args:
            surface: Pygame surface untuk drawing
        """
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        button_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, (20, 40, 80, 200), button_surf.get_rect(), border_radius=15)
        surface.blit(button_surf, scaled_rect)
        
        if self.hover_alpha > 0:
            hover_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            pygame.draw.rect(hover_surf, (*ORANGE, self.hover_alpha // 3), hover_surf.get_rect(), border_radius=15)
            surface.blit(hover_surf, scaled_rect)
            pygame.draw.rect(surface, (*ORANGE, self.hover_alpha), scaled_rect, 3, border_radius=15)
        else:
            pygame.draw.rect(surface, (60, 100, 160), scaled_rect, 2, border_radius=15)
        
        font = pygame.font.Font(None, 48)
        text_color = ORANGE if self.is_hovered else WHITE
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, mouse_pos):
        """
        Check apakah mouse hover di button.
        
        Args:
            mouse_pos: Tuple (x, y) posisi mouse
        
        Returns:
            Boolean True jika hover
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, mouse_pos):
        """
        Check apakah button diklik.
        
        Args:
            mouse_pos: Tuple (x, y) posisi mouse
        
        Returns:
            Boolean True jika diklik
        """
        return self.rect.collidepoint(mouse_pos)


class ModeSelection:
    """
    Screen untuk memilih mode game: PvP atau vs AI.
    
    Returns dari run(): 'pvp', 'ai', atau None jika cancel
    """
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Select Game Mode")
        self.background = None
        self.load_background()
        self.time = 0
        
        button_width = 400
        button_height = 150
        spacing = 100
        total_height = button_height * 2 + spacing
        start_y = (SCREEN_HEIGHT - total_height) // 2 + 50
        center_x = SCREEN_WIDTH // 2
        
        self.buttons = [
            ModeButton(center_x - button_width // 2, start_y, button_width, button_height, "PLAYER VS PLAYER", "pvp"),
            ModeButton(center_x - button_width // 2, start_y + button_height + spacing, button_width, button_height, "PLAYER VS AI", "ai")
        ]
    
    def load_background(self):
        """Load background image atau fallback ke gradient"""
        try:
            self.background = pygame.image.load('background.png').convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
    
    def update(self):
        """Update semua animasi"""
        self.time += 1
        for button in self.buttons:
            button.update()
    
    def draw_background(self):
        """Render background dengan overlay"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
        else:
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                r = int(20 + ratio * 20)
                g = int(45 + ratio * 25)
                b = int(90 + ratio * 40)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_header(self):
        """Render header dengan title"""
        header_surf = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (10, 25, 50, 150), header_surf.get_rect())
        self.screen.blit(header_surf, (0, 0))
        
        title_font = pygame.font.Font(None, 90)
        title_text = "SELECT GAME MODE"
        
        for i in range(3):
            glow = title_font.render(title_text, True, (*CYAN, 60 - i*15))
            glow_rect = glow.get_rect(center=(SCREEN_WIDTH // 2 + i, 80 + i))
            self.screen.blit(glow, glow_rect)
        
        title = title_font.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        line_width = 600
        line_x = (SCREEN_WIDTH - line_width) // 2
        for i in range(3):
            offset = math.sin(self.time * 0.05 + i) * 2
            pygame.draw.line(self.screen, (*CYAN, 150 - i*40), 
                           (line_x, 130 + offset), (line_x + line_width, 130 + offset), 2 + i)
    
    def draw_footer(self):
        """Render footer dengan controls"""
        footer_surf = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        pygame.draw.rect(footer_surf, (10, 25, 50, 180), footer_surf.get_rect())
        self.screen.blit(footer_surf, (0, SCREEN_HEIGHT - 70))
        
        font = pygame.font.Font(None, 24)
        controls = [("MOUSE", "Select Mode"), ("ESC", "Exit to Menu")]
        
        total_width = 500
        start_x = (SCREEN_WIDTH - total_width) // 2
        spacing = total_width // len(controls)
        
        for i, (key, action) in enumerate(controls):
            x = start_x + i * spacing
            
            key_bg = pygame.Surface((90, 24), pygame.SRCALPHA)
            pygame.draw.rect(key_bg, (40, 70, 120, 200), key_bg.get_rect(), border_radius=4)
            self.screen.blit(key_bg, (x + 60, SCREEN_HEIGHT - 52))
            
            key_text = font.render(key, True, GOLD)
            key_rect = key_text.get_rect(center=(x + 105, SCREEN_HEIGHT - 40))
            
            action_text = font.render(action, True, WHITE)
            action_rect = action_text.get_rect(center=(x + 105, SCREEN_HEIGHT - 18))
            
            self.screen.blit(key_text, key_rect)
            self.screen.blit(action_text, action_rect)
    
    def draw(self):
        """Render semua elemen UI"""
        self.draw_background()
        self.draw_header()
        
        for button in self.buttons:
            button.draw(self.screen)
        
        self.draw_footer()
    
    def handle_hover(self, mouse_pos):
        """
        Handle mouse hover pada buttons.
        
        Args:
            mouse_pos: Tuple (x, y) posisi mouse
        """
        for button in self.buttons:
            button.check_hover(mouse_pos)
    
    def handle_click(self, mouse_pos):
        """
        Handle mouse click pada buttons.
        
        Args:
            mouse_pos: Tuple (x, y) posisi mouse
        
        Returns:
            String mode ('pvp' atau 'ai') jika button diklik, None jika tidak
        """
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                return button.mode
        return None
    
    def run(self):
        """
        Run mode selection screen.
        
        Returns:
            String 'pvp' untuk PvP mode, 'ai' untuk vs AI mode, atau None jika cancel
        """
        clock = pygame.time.Clock()
        running = True
        selected_mode = None
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        selected_mode = None
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mode = self.handle_click(mouse_pos)
                    if mode:
                        selected_mode = mode
                        running = False
                
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_hover(mouse_pos)
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        return selected_mode


if __name__ == "__main__":
    selection = ModeSelection()
    result = selection.run()
    if result:
        print(f"Selected mode: {result}")
    else:
        print("No mode selected")
