"""
FILE: mode_selection.py
DESKRIPSI: UI untuk memilih mode game (PvP atau vs AI)
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


# === KONSTANTA ===
SCREEN_W, SCREEN_H = 1400, 800
WHITE = (255, 255, 255)
CYAN = (100, 200, 255)
ORANGE = (255, 150, 80)


class ModeButton:
    """
    Class untuk tombol pilihan mode
    
    Attributes:
        rect: Area tombol (untuk collision detection)
        text: Teks yang ditampilkan
        mode: 'pvp' atau 'ai' (return value)
        hovered: True jika mouse di atas tombol
    """
    
    def __init__(self, x, y, w, h, text, mode):
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
    
    
    def draw(self, screen, font):
        """
        Gambar tombol ke layar
        
        Args:
            screen: Pygame surface
            font: Font untuk teks
        
        Visual:
            - Normal: border biru, teks putih
            - Hover: border orange, teks orange
        """
        # Warna berdasarkan hover state
        color = ORANGE if self.hovered else (60, 100, 160)
        text_color = ORANGE if self.hovered else WHITE
        
        # Gambar background
        pygame.draw.rect(screen, (20, 40, 80), self.rect, border_radius=15)
        # Gambar border
        pygame.draw.rect(screen, color, self.rect, 3, border_radius=15)
        
        # Gambar teks (centered)
        text_surf = font.render(self.text, True, text_color)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
    
    
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
                pygame.image.load('background.png').convert(), 
                (SCREEN_W, SCREEN_H)
            )
        except:
            self.bg = None
        
        # === BUAT BUTTONS ===
        cx, cy = SCREEN_W // 2, SCREEN_H // 2  # Center screen
        
        self.buttons = [
            ModeButton(cx - 200, cy - 100, 400, 80, "PLAYER VS PLAYER", "pvp"),
            ModeButton(cx - 200, cy + 50, 400, 80, "PLAYER VS AI", "ai")
        ]
        
        # === FONTS ===
        self.font = pygame.font.Font(None, 48)       # Untuk tombol
        self.title_font = pygame.font.Font(None, 80) # Untuk judul
    
    
    def run(self):
        """
        Main loop - Tampilkan UI dan handle input
        
        Returns:
            str: 'pvp' atau 'ai' jika user pilih
            None: jika user tekan ESC (cancel)
        
        Loop:
            1. Handle events (quit, ESC, click)
            2. Update hover state
            3. Draw background, title, buttons
            4. Return mode jika button diklik
        """
        clock = pygame.time.Clock()
        
        while True:
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
                    # Cek klik pada tombol
                    for btn in self.buttons:
                        if btn.check_click(mouse):
                            return btn.mode  # Return 'pvp' atau 'ai'
            
            # === UPDATE HOVER STATE ===
            for btn in self.buttons:
                btn.hovered = btn.rect.collidepoint(mouse)
            
            # === DRAW ===
            
            # Background
            if self.bg:
                self.screen.blit(self.bg, (0, 0))
                # Overlay gelap
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                self.screen.blit(overlay, (0, 0))
            else:
                self.screen.fill((20, 45, 90))
            
            # Title
            title = self.title_font.render("SELECT GAME MODE", True, WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, 150)))
            
            # Buttons
            for btn in self.buttons:
                btn.draw(self.screen, self.font)
            
            # Footer instruction
            small_font = pygame.font.Font(None, 24)
            self.screen.blit(
                small_font.render("Click to select | ESC to go back", True, (150, 150, 150)),
                (SCREEN_W//2 - 130, SCREEN_H - 40)
            )
            
            # === UPDATE DISPLAY ===
            pygame.display.flip()
            clock.tick(60)


# === ENTRY POINT (untuk testing langsung) ===
if __name__ == "__main__":
    result = ModeSelection().run()
    print(f"Selected mode: {result}")
