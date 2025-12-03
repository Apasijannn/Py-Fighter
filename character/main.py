import pygame
import sys
import math

# Inisialisasi Pygame
pygame.init()

# Konstanta
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
ANIMATION_SPEED = 8

# Warna disesuaikan dengan background cityscape
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 200, 100)
DARK_BLUE = (20, 45, 90)
BLUE = (40, 70, 130)
LIGHT_BLUE = (80, 120, 180)
ORANGE = (255, 150, 80)
CYAN = (100, 200, 255)
NIGHT_BLUE = (30, 60, 120)

# Daftar karakter
CHARACTERS = [
    {"name": "Samurai", "path": r"assets\Samurai\Idle.png", "frames": 6},
    {"name": "Shinobi", "path": r"assets\Shinobi\Idle.png", "frames": 6},
    {"name": "Fighter", "path": r"assets\Fighter\Idle.png", "frames": 6},
    {"name": "Converted Vampire", "path": r"assets\Vampire1\Idle.png", "frames": 5},
    {"name": "Countess Vampire", "path": r"assets\Vampire2\Idle.png", "frames": 5},
    {"name": "Vampire Girl", "path": r"assets\Vampire3\Idle.png", "frames": 5},
]

class CharacterSlot:
    def __init__(self, char_data, x, y, slot_width=200, slot_height=220):
        self.name = char_data["name"]
        self.num_frames = char_data["frames"]
        self.x = x
        self.y = y
        self.slot_width = slot_width
        self.slot_height = slot_height
        self.current_frame = 0
        self.frame_counter = 0
        self.is_hovered = False
        self.is_selected = False
        self.hover_alpha = 0
        self.select_alpha = 0
        
        try:
            spritesheet = pygame.image.load(char_data["path"]).convert_alpha()
            sprite_width = spritesheet.get_width() // self.num_frames
            sprite_height = spritesheet.get_height()
            
            # Calculate scale to fit in slot
            scale_x = (slot_width - 40) / sprite_width
            scale_y = (slot_height - 80) / sprite_height
            scale = min(scale_x, scale_y, 3.0)
            
            self.frames = []
            for i in range(self.num_frames):
                frame = spritesheet.subsurface(pygame.Rect(
                    i * sprite_width, 0, sprite_width, sprite_height
                ))
                frame = pygame.transform.scale(frame, 
                    (int(sprite_width * scale), int(sprite_height * scale)))
                self.frames.append(frame)
            
            self.sprite_width = int(sprite_width * scale)
            self.sprite_height = int(sprite_height * scale)
            self.loaded = True
            
        except Exception as e:
            print(f"Error loading {self.name}: {e}")
            self.loaded = False
    
    def update(self):
        if self.loaded:
            self.frame_counter += 1
            if self.frame_counter >= ANIMATION_SPEED:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % self.num_frames
        
        # Smooth transitions
        if self.is_hovered:
            self.hover_alpha = min(255, self.hover_alpha + 25)
        else:
            self.hover_alpha = max(0, self.hover_alpha - 25)
        
        if self.is_selected:
            self.select_alpha = min(255, self.select_alpha + 20)
        else:
            self.select_alpha = max(0, self.select_alpha - 20)
    
    def draw(self, screen):
        # Draw card background with glass effect
        card_rect = pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
        
        # Base card - semi-transparent dark blue
        card_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (20, 40, 80, 180), card_surf.get_rect(), border_radius=15)
        screen.blit(card_surf, (self.x, self.y))
        
        # Selection glow
        if self.select_alpha > 0:
            for i in range(3):
                glow_surf = pygame.Surface((self.slot_width + 8 + i*4, self.slot_height + 8 + i*4), pygame.SRCALPHA)
                glow_rect = glow_surf.get_rect(center=(self.x + self.slot_width//2, self.y + self.slot_height//2))
                pygame.draw.rect(glow_surf, (*ORANGE, self.select_alpha // (4 + i)), 
                               glow_surf.get_rect(), border_radius=15)
                screen.blit(glow_surf, glow_rect)
            
            pygame.draw.rect(screen, (*ORANGE, self.select_alpha), card_rect, 4, border_radius=15)
        
        # Hover effect
        if self.hover_alpha > 0:
            hover_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
            pygame.draw.rect(hover_surf, (*CYAN, self.hover_alpha // 5), 
                           hover_surf.get_rect(), border_radius=15)
            screen.blit(hover_surf, (self.x, self.y))
            
            pygame.draw.rect(screen, (*CYAN, self.hover_alpha), card_rect, 3, border_radius=15)
        
        # Normal border
        if not self.is_selected and not self.is_hovered:
            pygame.draw.rect(screen, (60, 100, 160, 200), card_rect, 2, border_radius=15)
        
        if not self.loaded:
            font = pygame.font.Font(None, 24)
            text = font.render("ERROR", True, (255, 100, 100))
            text_rect = text.get_rect(center=card_rect.center)
            screen.blit(text, text_rect)
            return
        
        # Character sprite area
        sprite_y_pos = self.y + 30
        
        # # Shadow
        # shadow_surf = pygame.Surface((self.sprite_width, 12), pygame.SRCALPHA)
        # pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120), shadow_surf.get_rect())
        # shadow_rect = shadow_surf.get_rect(
        #     centerx=self.x + self.slot_width // 2,
        #     centery=sprite_y_pos + self.sprite_height // 2 + 10
        # )
        # screen.blit(shadow_surf, shadow_rect)
        
        # Character sprite
        frame_rect = self.frames[self.current_frame].get_rect(
            centerx=self.x + self.slot_width // 2,
            centery=sprite_y_pos + self.sprite_height // 2
        )
        screen.blit(self.frames[self.current_frame], frame_rect)
        
        # Name background
        name_bg_rect = pygame.Rect(self.x + 5, self.y + self.slot_height - 45, 
                                   self.slot_width - 10, 40)
        name_bg_surf = pygame.Surface((self.slot_width - 10, 40), pygame.SRCALPHA)
        pygame.draw.rect(name_bg_surf, (15, 30, 60, 220), name_bg_surf.get_rect(), border_radius=8)
        screen.blit(name_bg_surf, (self.x + 5, self.y + self.slot_height - 45))
        
        # Character name
        font = pygame.font.Font(None, 26)
        name_color = ORANGE if self.is_selected else WHITE
        name_text = font.render(self.name, True, name_color)
        name_rect = name_text.get_rect(center=name_bg_rect.center)
        screen.blit(name_text, name_rect)
        
        # Selected indicator
        if self.is_selected:
            indicator_surf = pygame.Surface((self.slot_width - 10, 3), pygame.SRCALPHA)
            indicator_surf.fill(ORANGE)
            screen.blit(indicator_surf, (self.x + 5, self.y + 5))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.get_rect().collidepoint(mouse_pos)
        return self.is_hovered

class CharacterSelection:
    def __init__(self):
        self.slots = []
        self.selected_index = None
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Character Selection")
        self.background = None
        self.load_background()
        self.load_characters()
        self.time = 0
    
    def load_background(self):
        try:
            self.background = pygame.image.load('background2.png').convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("Background image not found, using gradient")
            self.background = None
    
    def load_characters(self):
        # Grid layout - 3 kolom, 2 baris
        chars_per_row = 3
        slot_width = 200
        slot_height = 220
        spacing_x = 60
        spacing_y = 80
        
        total_width = (slot_width * chars_per_row) + (spacing_x * (chars_per_row - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 180
        
        for i, char_data in enumerate(CHARACTERS):
            row = i // chars_per_row
            col = i % chars_per_row
            x = start_x + col * (slot_width + spacing_x)
            y = start_y + row * (slot_height + spacing_y)
            
            slot = CharacterSlot(char_data, x, y, slot_width, slot_height)
            self.slots.append(slot)
    
    def update(self):
        self.time += 1
        for slot in self.slots:
            slot.update()
    
    def draw_background(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
            # Add dark overlay for better contrast
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))
            self.screen.blit(overlay, (0, 0))
        else:
            # Fallback gradient
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                r = int(20 + ratio * 20)
                g = int(45 + ratio * 25)
                b = int(90 + ratio * 40)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_header(self):
        # Semi-transparent header background
        header_surf = pygame.Surface((SCREEN_WIDTH, 150), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (10, 25, 50, 150), header_surf.get_rect())
        self.screen.blit(header_surf, (0, 0))
        
        # Title with glow effect
        title_font = pygame.font.Font(None, 80)
        title_text = "SELECT YOUR CHARACTER"
        
        # Glow effect
        for i in range(3):
            glow = title_font.render(title_text, True, (*ORANGE, 60 - i*15))
            glow_rect = glow.get_rect(center=(SCREEN_WIDTH // 2 + i, 70 + i))
            self.screen.blit(glow, glow_rect)
        
        # Main title
        title = title_font.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(title, title_rect)
        
        # Animated decorative line under title
        line_width = 600
        line_x = (SCREEN_WIDTH - line_width) // 2
        
        # Glowing line effect
        for i in range(3):
            offset = math.sin(self.time * 0.05 + i) * 2
            pygame.draw.line(self.screen, (*ORANGE, 150 - i*40), 
                            (line_x, 110 + offset), (line_x + line_width, 110 + offset), 2 + i)
        
        # Instruction text
        if self.selected_index is not None:
            inst_font = pygame.font.Font(None, 28)
            inst = inst_font.render("Press SPACE to confirm selection", True, CYAN)
            inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, 135))
            
            # Pulsing effect
            pulse = abs(math.sin(self.time * 0.1))
            inst.set_alpha(int(200 + pulse * 55))
            self.screen.blit(inst, inst_rect)
    
    def draw_footer(self):
        # Semi-transparent footer background
        footer_surf = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        pygame.draw.rect(footer_surf, (10, 25, 50, 180), footer_surf.get_rect())
        self.screen.blit(footer_surf, (0, SCREEN_HEIGHT - 60))
        
        # Instructions
        font = pygame.font.Font(None, 24)
        
        controls = [
            ("MOUSE", "Select Character"),
            ("SPACE", "Confirm"),
            ("ESC", "Exit")
        ]
        
        total_width = 700
        start_x = (SCREEN_WIDTH - total_width) // 2
        spacing = total_width // len(controls)
        
        for i, (key, action) in enumerate(controls):
            x = start_x + i * spacing
            
            # Key background
            key_bg = pygame.Surface((80, 22), pygame.SRCALPHA)
            pygame.draw.rect(key_bg, (40, 70, 120, 200), key_bg.get_rect(), border_radius=4)
            self.screen.blit(key_bg, (x + 20, SCREEN_HEIGHT - 45))
            
            key_text = font.render(key, True, ORANGE)
            key_rect = key_text.get_rect(center=(x + 60, SCREEN_HEIGHT - 34))
            
            action_text = font.render(action, True, WHITE)
            action_rect = action_text.get_rect(center=(x + 60, SCREEN_HEIGHT - 12))
            
            self.screen.blit(key_text, key_rect)
            self.screen.blit(action_text, action_rect)
    
    def draw(self):
        self.draw_background()
        self.draw_header()
        
        # Draw character slots
        for slot in self.slots:
            slot.draw(self.screen)
        
        self.draw_footer()
    
    def handle_click(self, mouse_pos):
        for i, slot in enumerate(self.slots):
            if slot.get_rect().collidepoint(mouse_pos):
                if self.selected_index is not None:
                    self.slots[self.selected_index].is_selected = False
                
                self.selected_index = i
                slot.is_selected = True
                break
    
    def handle_hover(self, mouse_pos):
        for slot in self.slots:
            slot.check_hover(mouse_pos)
    
    def confirm_selection(self):
        if self.selected_index is not None:
            selected = self.slots[self.selected_index]
            print(f"✓ Character Confirmed: {selected.name}")
            return selected.name
        return None
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        char = self.confirm_selection()
                        if char:
                            print(f"Starting game with {char}!")
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(mouse_pos)
                
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_hover(mouse_pos)
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    selection = CharacterSelection()
    selection.run()