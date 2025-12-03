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
P1_COLOR = CYAN
P2_COLOR = ORANGE

# Daftar karakter - gunakan forward slash
CHARACTERS = [
    {"name": "Samurai", "path": "character/assets/Samurai/Idle.png", "frames": 6},
    {"name": "Shinobi", "path": "character/assets/Shinobi/Idle.png", "frames": 6},
    {"name": "Fighter", "path": "character/assets/Fighter/Idle.png", "frames": 6},
    {"name": "Converted Vampire", "path": "character/assets/Vampire1/Idle.png", "frames": 5},
    {"name": "Countess Vampire", "path": "character/assets/Vampire2/Idle.png", "frames": 5},
    {"name": "Vampire Girl", "path": "character/assets/Vampire3/Idle.png", "frames": 5},
]

class CharacterSlot:
    def __init__(self, char_data, x, y, slot_width=180, slot_height=200):
        self.name = char_data["name"]
        self.num_frames = char_data["frames"]
        self.x = x
        self.y = y
        self.slot_width = slot_width
        self.slot_height = slot_height
        self.current_frame = 0
        self.frame_counter = 0
        self.is_hovered = False
        self.is_selected_p1 = False
        self.is_selected_p2 = False
        self.hover_alpha = 0
        self.select_alpha_p1 = 0
        self.select_alpha_p2 = 0
        
        try:
            spritesheet = pygame.image.load(char_data["path"]).convert_alpha()
            sprite_width = spritesheet.get_width() // self.num_frames
            sprite_height = spritesheet.get_height()
            
            # Calculate scale to fit in slot
            scale_x = (slot_width - 40) / sprite_width
            scale_y = (slot_height - 80) / sprite_height
            scale = min(scale_x, scale_y, 2.5)
            
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
        
        if self.is_selected_p1:
            self.select_alpha_p1 = min(255, self.select_alpha_p1 + 20)
        else:
            self.select_alpha_p1 = max(0, self.select_alpha_p1 - 20)
            
        if self.is_selected_p2:
            self.select_alpha_p2 = min(255, self.select_alpha_p2 + 20)
        else:
            self.select_alpha_p2 = max(0, self.select_alpha_p2 - 20)
    
    def draw(self, screen):
        # Draw card background with glass effect
        card_rect = pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
        
        # Base card - semi-transparent dark blue
        card_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (20, 40, 80, 180), card_surf.get_rect(), border_radius=12)
        screen.blit(card_surf, (self.x, self.y))
        
        # P1 Selection glow (left side)
        if self.select_alpha_p1 > 0:
            for i in range(3):
                glow_surf = pygame.Surface((self.slot_width + 8 + i*4, self.slot_height + 8 + i*4), pygame.SRCALPHA)
                glow_rect = glow_surf.get_rect(center=(self.x + self.slot_width//2, self.y + self.slot_height//2))
                pygame.draw.rect(glow_surf, (*P1_COLOR, self.select_alpha_p1 // (4 + i)), 
                               glow_surf.get_rect(), border_radius=12)
                screen.blit(glow_surf, glow_rect)
            
            pygame.draw.rect(screen, (*P1_COLOR, self.select_alpha_p1), card_rect, 3, border_radius=12)
        
        # P2 Selection glow (right side)
        if self.select_alpha_p2 > 0:
            for i in range(3):
                glow_surf = pygame.Surface((self.slot_width + 8 + i*4, self.slot_height + 8 + i*4), pygame.SRCALPHA)
                glow_rect = glow_surf.get_rect(center=(self.x + self.slot_width//2, self.y + self.slot_height//2))
                pygame.draw.rect(glow_surf, (*P2_COLOR, self.select_alpha_p2 // (4 + i)), 
                               glow_surf.get_rect(), border_radius=12)
                screen.blit(glow_surf, glow_rect)
            
            pygame.draw.rect(screen, (*P2_COLOR, self.select_alpha_p2), card_rect, 3, border_radius=12)
        
        # Hover effect
        if self.hover_alpha > 0:
            hover_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
            pygame.draw.rect(hover_surf, (*WHITE, self.hover_alpha // 6), 
                           hover_surf.get_rect(), border_radius=12)
            screen.blit(hover_surf, (self.x, self.y))
            
            pygame.draw.rect(screen, (*WHITE, self.hover_alpha), card_rect, 2, border_radius=12)
        
        # Normal border
        if not self.is_selected_p1 and not self.is_selected_p2 and not self.is_hovered:
            pygame.draw.rect(screen, (60, 100, 160, 200), card_rect, 2, border_radius=12)
        
        if not self.loaded:
            font = pygame.font.Font(None, 22)
            text = font.render("ERROR", True, (255, 100, 100))
            text_rect = text.get_rect(center=card_rect.center)
            screen.blit(text, text_rect)
            return
        
        # Character sprite area
        sprite_y_pos = self.y + 25
        
        # Character sprite
        frame_rect = self.frames[self.current_frame].get_rect(
            centerx=self.x + self.slot_width // 2,
            centery=sprite_y_pos + self.sprite_height // 2
        )
        screen.blit(self.frames[self.current_frame], frame_rect)
        
        # Name background
        name_bg_rect = pygame.Rect(self.x + 5, self.y + self.slot_height - 40, 
                                   self.slot_width - 10, 35)
        name_bg_surf = pygame.Surface((self.slot_width - 10, 35), pygame.SRCALPHA)
        pygame.draw.rect(name_bg_surf, (15, 30, 60, 220), name_bg_surf.get_rect(), border_radius=7)
        screen.blit(name_bg_surf, (self.x + 5, self.y + self.slot_height - 40))
        
        # Character name
        font = pygame.font.Font(None, 22)
        name_color = P1_COLOR if self.is_selected_p1 else (P2_COLOR if self.is_selected_p2 else WHITE)
        name_text = font.render(self.name, True, name_color)
        name_rect = name_text.get_rect(center=name_bg_rect.center)
        screen.blit(name_text, name_rect)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.get_rect().collidepoint(mouse_pos)
        return self.is_hovered

class CharacterSelection:
    def __init__(self):
        self.slots = []
        self.selected_index_p1 = None
        self.selected_index_p2 = None
        self.current_hover = None
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Character Selection - Player 1 & 2")
        self.background = None
        self.p1_badge = None
        self.p2_badge = None
        self.load_background()
        self.load_badges()
        self.load_characters()
        self.time = 0
        self.both_ready = False
    
    def load_badges(self):
        """Load P1 and P2 badge images"""
        try:
            self.p1_badge = pygame.image.load('p1.png').convert_alpha()
            # Scale badge to appropriate size
            badge_width = 50
            badge_height = int(self.p1_badge.get_height() * (badge_width / self.p1_badge.get_width()))
            self.p1_badge = pygame.transform.scale(self.p1_badge, (badge_width, badge_height))
            print("✓ P1 badge loaded successfully")
        except Exception as e:
            print(f"Error loading P1 badge: {e}")
            self.p1_badge = None
        
        try:
            self.p2_badge = pygame.image.load('p2.png').convert_alpha()
            # Scale badge to same size as P1
            badge_width = 50
            badge_height = int(self.p2_badge.get_height() * (badge_width / self.p2_badge.get_width()))
            self.p2_badge = pygame.transform.scale(self.p2_badge, (badge_width, badge_height))
            print("✓ P2 badge loaded successfully")
        except Exception as e:
            print(f"Error loading P2 badge: {e}")
            self.p2_badge = None
    
    def load_background(self):
        try:
            self.background = pygame.image.load('background.png').convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("Background image not found, using gradient")
            self.background = None
    
    def load_characters(self):
        # Grid layout - 3 kolom, 2 baris
        chars_per_row = 3
        slot_width = 180
        slot_height = 200
        spacing_x = 50
        spacing_y = 70
        
        total_width = (slot_width * chars_per_row) + (spacing_x * (chars_per_row - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 200
        
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
        
        # Check if both players ready
        self.both_ready = (self.selected_index_p1 is not None and 
                          self.selected_index_p2 is not None)
    
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
        header_surf = pygame.Surface((SCREEN_WIDTH, 180), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (10, 25, 50, 150), header_surf.get_rect())
        self.screen.blit(header_surf, (0, 0))
        
        # Center divider line
        # center_x = SCREEN_WIDTH // 2
        # pygame.draw.line(self.screen, (80, 120, 180, 200), (center_x, 0), (center_x, 180), 3)
        
        # Player 1 side (Left) - Badge + Text
        # if self.p1_badge:
        #     badge_scale = 1.2
        #     scaled_width = int(self.p1_badge.get_width() * badge_scale)
        #     scaled_height = int(self.p1_badge.get_height() * badge_scale)
        #     p1_badge_scaled = pygame.transform.scale(self.p1_badge, (scaled_width, scaled_height))
        #     badge_x = center_x // 2 - scaled_width // 2
        #     self.screen.blit(p1_badge_scaled, (badge_x, 35))
        # else:
        #     # Fallback text
        #     p1_font = pygame.font.Font(None, 60)
        #     p1_text = "PLAYER 1"
        #     for i in range(3):
        #         glow = p1_font.render(p1_text, True, (*P1_COLOR, 80 - i*20))
        #         glow_rect = glow.get_rect(center=(center_x // 2 + i, 50 + i))
        #         self.screen.blit(glow, glow_rect)
        #     p1_render = p1_font.render(p1_text, True, P1_COLOR)
        #     p1_rect = p1_render.get_rect(center=(center_x // 2, 50))
        #     self.screen.blit(p1_render, p1_rect)
        
        # # Player 2 side (Right) - Badge + Text
        # if self.p2_badge:
        #     badge_scale = 1.2
        #     scaled_width = int(self.p2_badge.get_width() * badge_scale)
        #     scaled_height = int(self.p2_badge.get_height() * badge_scale)
        #     p2_badge_scaled = pygame.transform.scale(self.p2_badge, (scaled_width, scaled_height))
        #     badge_x = center_x + center_x // 2 - scaled_width // 2
        #     self.screen.blit(p2_badge_scaled, (badge_x, 35))
        # else:
        #     # Fallback text
        #     p2_font = pygame.font.Font(None, 60)
        #     p2_text = "PLAYER 2"
        #     for i in range(3):
        #         glow = p2_font.render(p2_text, True, (*P2_COLOR, 80 - i*20))
        #         glow_rect = glow.get_rect(center=(center_x + center_x // 2 + i, 50 + i))
        #         self.screen.blit(glow, glow_rect)
        #     p2_render = p2_font.render(p2_text, True, P2_COLOR)
        #     p2_rect = p2_render.get_rect(center=(center_x + center_x // 2, 50))
        #     self.screen.blit(p2_render, p2_rect)
        
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
    
        # Status text
        # status_font = pygame.font.Font(None, 26)
        # p1_status = "✓ READY" if self.selected_index_p1 is not None else "Waiting..."
        # p2_status = "✓ READY" if self.selected_index_p2 is not None else "Waiting..."
        
        # p1_status_color = P1_COLOR if self.selected_index_p1 is not None else (100, 100, 100)
        # p2_status_color = P2_COLOR if self.selected_index_p2 is not None else (100, 100, 100)
        
        # p1_status_text = status_font.render(p1_status, True, p1_status_color)
        # p1_status_rect = p1_status_text.get_rect(center=(center_x // 2, 145))
        # self.screen.blit(p1_status_text, p1_status_rect)
        
        # p2_status_text = status_font.render(p2_status, True, p2_status_color)
        # p2_status_rect = p2_status_text.get_rect(center=(center_x + center_x // 2, 145))
        # self.screen.blit(p2_status_text, p2_status_rect)
        
        # Instruction when both ready
        if self.both_ready:
            inst_font = pygame.font.Font(None, 32)
            inst = inst_font.render("Press SPACE to continue", True, GOLD)
            center_x = SCREEN_WIDTH // 2
            inst_rect = inst.get_rect(center=(center_x, 165))
            
            # Pulsing effect
            pulse = abs(math.sin(self.time * 0.1))
            inst.set_alpha(int(200 + pulse * 55))
            self.screen.blit(inst, inst_rect)
    
    def draw_footer(self):
        # Semi-transparent footer background
        footer_surf = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        pygame.draw.rect(footer_surf, (10, 25, 50, 180), footer_surf.get_rect())
        self.screen.blit(footer_surf, (0, SCREEN_HEIGHT - 70))
        
        # Instructions
        font = pygame.font.Font(None, 24)
        
        controls = [
            ("CLICK", "Select Character"),
            ("SPACE", "Confirm" if self.both_ready else "Disabled"),
            ("ESC", "Back to Menu")
        ]
        
        total_width = 800
        start_x = (SCREEN_WIDTH - total_width) // 2
        spacing = total_width // len(controls)
        
        for i, (key, action) in enumerate(controls):
            x = start_x + i * spacing
            
            # Key background
            key_color = (40, 70, 120, 200) if not (key == "SPACE" and not self.both_ready) else (60, 60, 60, 150)
            key_bg = pygame.Surface((90, 24), pygame.SRCALPHA)
            pygame.draw.rect(key_bg, key_color, key_bg.get_rect(), border_radius=4)
            self.screen.blit(key_bg, (x + 40, SCREEN_HEIGHT - 52))
            
            key_text_color = GOLD if not (key == "SPACE" and not self.both_ready) else (120, 120, 120)
            key_text = font.render(key, True, key_text_color)
            key_rect = key_text.get_rect(center=(x + 85, SCREEN_HEIGHT - 40))
            
            action_text = font.render(action, True, WHITE if not (key == "SPACE" and not self.both_ready) else (120, 120, 120))
            action_rect = action_text.get_rect(center=(x + 85, SCREEN_HEIGHT - 18))
            
            self.screen.blit(key_text, key_rect)
            self.screen.blit(action_text, action_rect)
    
    def draw(self):
        self.draw_background()
        self.draw_header()
        
        # Draw character slots
        for slot in self.slots:
            slot.draw(self.screen)
        
        # Draw P1 and P2 badges on selected characters
        if self.selected_index_p1 is not None and self.p1_badge:
            slot = self.slots[self.selected_index_p1]
            badge_x = slot.x + 5
            badge_y = slot.y + 5
            self.screen.blit(self.p1_badge, (badge_x, badge_y))
        
        if self.selected_index_p2 is not None and self.p2_badge:
            slot = self.slots[self.selected_index_p2]
            badge_x = slot.x + slot.slot_width - self.p2_badge.get_width() - 5
            badge_y = slot.y + 5
            self.screen.blit(self.p2_badge, (badge_x, badge_y))
        
        self.draw_footer()
    
    def handle_click(self, mouse_pos):
        for i, slot in enumerate(self.slots):
            if slot.get_rect().collidepoint(mouse_pos):
                # Toggle selection untuk player yang click
                # Jika slot sudah dipilih salah satu player, biarkan player lain juga bisa pilih
                # User bisa click untuk toggle selection mereka sendiri
                
                # Check apakah ini selection pertama atau toggle
                if self.selected_index_p1 == i:
                    # P1 click character yang sama, deselect
                    self.slots[i].is_selected_p1 = False
                    self.selected_index_p1 = None
                elif self.selected_index_p2 == i:
                    # P2 click character yang sama, deselect
                    self.slots[i].is_selected_p2 = False
                    self.selected_index_p2 = None
                else:
                    # New selection - perlu determine P1 atau P2
                    # Jika P1 belum pilih, ini untuk P1
                    # Jika P1 sudah pilih tapi P2 belum, ini untuk P2
                    # Jika keduanya sudah pilih, abaikan (harus deselect dulu)
                    
                    if self.selected_index_p1 is None:
                        # P1 selection
                        self.selected_index_p1 = i
                        slot.is_selected_p1 = True
                    elif self.selected_index_p2 is None:
                        # P2 selection
                        self.selected_index_p2 = i
                        slot.is_selected_p2 = True
                    # Else: both already selected, need to deselect first
                
                break
    
    def handle_hover(self, mouse_pos):
        for slot in self.slots:
            slot.check_hover(mouse_pos)
    
    def confirm_selection(self):
        if self.both_ready:
            char_p1 = self.slots[self.selected_index_p1].name
            char_p2 = self.slots[self.selected_index_p2].name
            print(f"✓ Player 1 Character: {char_p1}")
            print(f"✓ Player 2 Character: {char_p2}")
            return (char_p1, char_p2)
        return None
    
    def run(self):
        """Run dual character selection and return (p1_char, p2_char) or None if cancelled"""
        clock = pygame.time.Clock()
        running = True
        result = None
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to menu without selection
                        running = False
                        result = None
                    elif event.key == pygame.K_SPACE:
                        if self.both_ready:
                            result = self.confirm_selection()
                            if result:
                                running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(mouse_pos)
                
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_hover(mouse_pos)
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        return result

if __name__ == "__main__":
    selection = DualCharacterSelection()
    result = selection.run()
    if result:
        p1_char, p2_char = result
        print(f"\n{'='*50}")
        print(f"✓ Player 1: {p1_char}")
        print(f"✓ Player 2: {p2_char}")
        print(f"{'='*50}")
    else:
        print("Selection cancelled")