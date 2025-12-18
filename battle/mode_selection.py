"""
FILE: mode_selection.py
DESKRIPSI: UI untuk memilih mode game (PvP atau vs AI) dengan efek visual lanjut
DIGUNAKAN OLEH: menu.py (sebelum character selection)
MENGGUNAKAN: pygame (untuk UI)

ALUR PROGRAM:
1. menu.py memanggil ModeSelection().run()
2. User melihat 2 tombol: "PLAYER VS PLAYER" dan "PLAYER VS AI"
3. User klik salah satu tombol
4. ModeSelection.run() return 'pvp' atau 'ai'
5. menu.py lanjut ke character selection dengan mode yang dipilih

OOP CONCEPTS:
- Encapsulation: UI logic dibungkus dalam class
- Composition: ModeSelection memiliki list ModeButton
- Single Responsibility: Setiap class punya 1 tugas
"""
import pygame
import sys
import random
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === KONSTANTA ===
SCREEN_W, SCREEN_H = 1400, 800
WHITE = (255, 255, 255)
CYAN = (100, 200, 255)
ORANGE = (255, 150, 80)
GOLD = (255, 200, 100)
FPS = 60

class ModeButton:
    """
    Class untuk tombol pilihan mode
    
    Attributes:
        rect: Area tombol (untuk collision detection)
        text: Teks yang ditampilkan
        mode: 'pvp' atau 'ai' (return value)
        hovered: True jika mouse di atas tombol
    """
    
    def __init__(self, x, y, w, h, text, mode, image_paths=None):
        """
        Constructor - Buat tombol
        
        Args:
            x, y: Posisi tombol
            w, h: Ukuran tombol
            text: Teks di tombol
            mode: Nilai yang di-return saat diklik
        
        Dipanggil dari: ModeSelection.__init__()
        """
        self.rect = pygame.Rect(x, y, w, h)     # Hitbox tombol
        self.text = text                         # Label tombol
        self.mode = mode                         # Return value
        self.hovered = False                     # Hover state
        
        # Penambahan atribut animasi dari kode baru
        self.hover_alpha = 0
        self.scale = 1.0
        self.images = []
        if image_paths:
            for path in image_paths:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (h - 40, h - 40))
                    self.images.append(img)
                except:
                    pass

    def update(self):
        if self.hovered:
            self.hover_alpha = min(255, self.hover_alpha + 20)
            self.scale = min(1.05, self.scale + 0.01)
        else:
            self.hover_alpha = max(0, self.hover_alpha - 20)
            self.scale = max(1.0, self.scale - 0.01)

    def draw_glitch(self, surface, img, pos):
        if self.hovered and self.mode == "ai":
            glitch_amount = 10
            off_x = random.randint(-glitch_amount, glitch_amount)
            off_y = random.randint(-glitch_amount, glitch_amount)
            
            temp_surf = img.copy()
            temp_surf.fill((0, 255, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp_surf, (pos[0] + off_x, pos[1] + off_y))
            surface.blit(img, (pos[0] - (off_x // 2), pos[1]))
            
            if random.random() > 0.6: 
                line_y = random.randint(pos[1], pos[1] + img.get_height())
                pygame.draw.line(surface, WHITE, (pos[0], line_y), (pos[0] + img.get_width(), line_y), 1)
        else:
            surface.blit(img, pos)

    def draw(self, screen, font):
        """
        Gambar tombol ke layar
        
        Args:
            screen: Pygame surface
            font: Font untuk teks
        
        Visual:
            - Normal: border biru, teks putih
            - Hover: border orange, teks orange, efek glow, scaling
        """
        # Kalkulasi scaling
        scaled_w = int(self.rect.width * self.scale)
        scaled_h = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_w // 2,
            self.rect.centery - scaled_h // 2,
            scaled_w,
            scaled_h
        )

        if self.hover_alpha > 0:
            for i in range(3):
                margin = 4 + (i * 4)
                glow_surf = pygame.Surface((scaled_w + margin*2, scaled_h + margin*2), pygame.SRCALPHA)
                glow_color = (*ORANGE, (self.hover_alpha // (i + 4)))
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=20 + margin)
                screen.blit(glow_surf, glow_surf.get_rect(center=scaled_rect.center))

        bg_alpha = 230 if self.hovered else 200
        button_surf = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
        pygame.draw.rect(button_surf, (20, 40, 80, bg_alpha), button_surf.get_rect(), border_radius=20)
        screen.blit(button_surf, scaled_rect)
        
        color = (*ORANGE, self.hover_alpha) if self.hovered else (60, 100, 160)
        thickness = 3 if self.hovered else 2
        pygame.draw.rect(screen, color, scaled_rect, thickness, border_radius=20)

        if self.images and len(self.images) >= 2:
            padding = 30
            vs_surf = font.render("vs", True, GOLD)
            img_w = self.images[0].get_width()
            
            total_w = (img_w * 2) + vs_surf.get_width() + (padding * 2)
            start_x = scaled_rect.centerx - total_w // 2
            
            # P1 Image
            screen.blit(self.images[0], (start_x, scaled_rect.centery - img_w // 2))
            # VS Text
            vs_x = start_x + img_w + padding
            screen.blit(vs_surf, (vs_x, scaled_rect.centery - vs_surf.get_height() // 2))
            # P2/AI Image
            p2_x = vs_x + vs_surf.get_width() + padding
            if self.mode == "ai":
                self.draw_glitch(screen, self.images[1], (p2_x, scaled_rect.centery - img_w // 2))
            else:
                screen.blit(self.images[1], (p2_x, scaled_rect.centery - img_w // 2))
        else:
            # Fallback ke teks jika gambar tidak ada
            text_color = ORANGE if self.hovered else WHITE
            text_surf = font.render(self.text, True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=scaled_rect.center))
    
    def check_click(self, pos):
        """
        Cek apakah posisi mouse di dalam tombol
        
        Args:
            pos: (x, y) posisi mouse
        
        Returns:
            bool: True jika mouse di dalam tombol
        """
        return self.rect.collidepoint(pos)


class ModeSelection:
    """
    Screen untuk memilih mode game
    
    Menampilkan 2 pilihan:
    - PLAYER VS PLAYER (mode='pvp')
    - PLAYER VS AI (mode='ai')
    
    Dipanggil dari: menu.py
    Returns: 'pvp', 'ai', atau None (jika cancel)
    """
    
    def __init__(self):
        """
        Constructor - Setup screen dan buttons
        
        Membuat 2 ModeButton di tengah layar
        """
        # === INIT PYGAME ===
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Select Game Mode")
        
        # === LOAD BACKGROUND ===
        try:
            self.bg = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, 'assets/menu/background.png')).convert(), 
                (SCREEN_W, SCREEN_H)
            )
        except:
            self.bg = None
        
        # === BUAT BUTTONS ===
        cx, cy = SCREEN_W // 2, SCREEN_H // 2  # Center screen
        self.time = 0 # Untuk animasi header
        
        self.buttons = [
            ModeButton(cx - 275, 250, 550, 150, "PLAYER VS PLAYER", "pvp", 
                       image_paths=[os.path.join(BASE_DIR, 'assets/select_char/p1.png'), os.path.join(BASE_DIR, 'assets/select_char/p2.png')]),
            ModeButton(cx - 275, 480, 550, 150, "PLAYER VS AI", "ai", 
                       image_paths=[os.path.join(BASE_DIR, 'assets/select_char/p1.png'), os.path.join(BASE_DIR, 'assets/select_char/ai.png')])
        ]
        
        # === FONTS ===
        self.font = pygame.font.Font(None, 48)       # Untuk tombol
        self.title_font = pygame.font.Font(None, 90) # Untuk judul
    
    def run(self):
        """
        Main loop - Tampilkan UI dan handle input
        
        Returns:
            str: 'pvp' atau 'ai' jika user pilih
            None: jika user tekan ESC (cancel)
        
        Loop:
            1. Handle events (quit, ESC, click)
            2. Update hover state & animations
            3. Draw background, title, buttons, footer
            4. Return mode jika button diklik
        """
        clock = pygame.time.Clock()
        
        while True:
            self.time += 1
            mouse = pygame.mouse.get_pos()
            
            # === HANDLE EVENTS ===
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None  # Cancel, kembali ke menu
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.buttons:
                        if btn.check_click(mouse):
                            return btn.mode 
            
            # === UPDATE STATE ===
            for btn in self.buttons:
                btn.hovered = btn.rect.collidepoint(mouse)
                btn.update()
            
            # === DRAW ===
            
            # 1. Background
            if self.bg:
                self.screen.blit(self.bg, (0, 0))
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                self.screen.blit(overlay, (0, 0))
            else:
                self.screen.fill((20, 45, 90))
            
            # 2. Header (Visual Baru)
            header_surf = pygame.Surface((SCREEN_W, 200), pygame.SRCALPHA)
            header_surf.fill((10, 25, 50, 150))
            self.screen.blit(header_surf, (0, 0))
            
            title_text = "SELECT GAME MODE"
            for i in range(3): # Title Glow
                glow = self.title_font.render(title_text, True, (*ORANGE, 60 - i*15))
                self.screen.blit(glow, glow.get_rect(center=(SCREEN_W//2 + i, 80 + i)))
            
            title = self.title_font.render(title_text, True, WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, 80)))

            # Animated Line under title
            line_w = 600
            lx = (SCREEN_W - line_w) // 2
            for i in range(3):
                offset = math.sin(self.time * 0.05 + i) * 2
                pygame.draw.line(self.screen, (*ORANGE, 150 - i*40), (lx, 130 + offset), (lx + line_w, 130 + offset), 2 + i)
            
            # 3. Buttons
            for btn in self.buttons:
                btn.draw(self.screen, self.font)
            
            # 4. Footer (Visual Baru)
            footer_surf = pygame.Surface((SCREEN_W, 70), pygame.SRCALPHA)
            footer_surf.fill((10, 25, 50, 180))
            self.screen.blit(footer_surf, (0, SCREEN_H - 70))
            
            # Footer Instruction
            small_font = pygame.font.Font(None, 24)
            instr = [("MOUSE", "Select Mode"), ("ESC", "Exit to Menu")]
            for i, (key, act) in enumerate(instr):
                x_pos = (SCREEN_W // 2 - 150) + (i * 200)
                # Key Box
                pygame.draw.rect(self.screen, (40, 70, 120, 200), (x_pos, SCREEN_H - 52, 90, 24), border_radius=4)
                # Key Text
                k_surf = small_font.render(key, True, GOLD)
                self.screen.blit(k_surf, k_surf.get_rect(center=(x_pos + 45, SCREEN_H - 40)))
                # Action Text
                a_surf = small_font.render(act, True, WHITE)
                self.screen.blit(a_surf, a_surf.get_rect(center=(x_pos + 45, SCREEN_H - 18)))
            
            # === UPDATE DISPLAY ===
            pygame.display.flip()
            clock.tick(FPS)

# === ENTRY POINT ===
if __name__ == "__main__":
    result = ModeSelection().run()
    if result:
        print(f"Selected mode: {result}")