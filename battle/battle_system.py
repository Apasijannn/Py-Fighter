"""
mengelola game loop dan fighters
DIGUNAKAN OLEH: menu.py (memanggil BattleSystem untuk mulai battle)

ALUR PROGRAM:
1. menu.py -> character selection -> arena selection -> BattleSystem()
2. BattleSystem.__init__() membuat 2 Fighter dan AIController (jika mode AI)
3. BattleSystem.run() menjalankan game loop:
   - Handle input (keyboard/quit)
   - Update fighters (move, attack, animasi)
   - Draw ke layar
4. Jika ada pemenang, tampilkan victory screen
5. ESC untuk kembali ke menu

- Composition: BattleSystem memiliki Fighter dan AIController
- Factory Pattern: create_fighter() membuat Fighter dengan config
- Encapsulation: Game loop tersembunyi dalam run()
"""
import pygame
import sys
import os
from battle.fighter_base import Fighter       # Class karakter
from battle.ai_controller import AIController # Class AI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCREEN_W, SCREEN_H = 1400, 800  # Ukuran layar
FPS = 60                         # Frame per second

# Warna (R, G, B)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (100, 200, 255)      # Warna P1
ORANGE = (255, 150, 80)     # Warna P2/AI


# === DATA KARAKTER ===
# Format: 'Nama': (folder, scale, [offset_x, offset_y], [files...], [frame_counts...])
# Files: Idle, Run, Jump, Attack1, Attack2, Attack3, Hurt, Dead
CHARACTERS = {
    'Samurai': (
        os.path.join(BASE_DIR, 'assets/character/Samurai'),     # Folder sprite
        2.5,                            # Scale sprite
        [40, 30],                       # Offset [x, y]
        ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 
         'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        [6, 8, 12, 6, 4, 3, 2, 3]       # Jumlah frame tiap animasi
    ),
    'Shinobi': (
        os.path.join(BASE_DIR, 'assets/character/Shinobi'), 2.5, [40, 30],
        ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 
         'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        [6, 8, 12, 5, 3, 4, 2, 4]
    ),
    'Fighter': (
        os.path.join(BASE_DIR, 'assets/character/Fighter'), 2.5, [40, 30],
        ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 
         'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        [6, 8, 10, 4, 3, 4, 3, 3]
    ),
    'Converted Vampire': (
        os.path.join(BASE_DIR, 'assets/character/Vampire1'), 2.0, [60, 50],
        ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 
         'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        [5, 8, 7, 5, 3, 4, 1, 8]
    ),
    'Countess Vampire': (
        os.path.join(BASE_DIR, 'assets/character/Vampire2'), 2.0, [60, 50],
        ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 
         'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        [5, 6, 6, 6, 3, 1, 2, 8]
    ),
    'Vampire Girl': (
        os.path.join(BASE_DIR, 'assets/character/Vampire3'), 2.0, [60, 50],
        ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 
         'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        [5, 6, 6, 5, 4, 2, 2, 10]
    ),
}


# === DATA ARENA ===
# Format: 'Nama Arena': 'path/to/background.png'
ARENAS = {
    'Keputih': os.path.join(BASE_DIR, 'assets/arena/Keputih.png'),
    'San Antonio': os.path.join(BASE_DIR, 'assets/arena/SanAntonio.png'),
    'Taman Apsari': os.path.join(BASE_DIR, 'assets/arena/TamanApsari.png'),
    'Tunjungan': os.path.join(BASE_DIR, 'assets/arena/Tunjungan.png')
}


class BattleSystem:
    """
    Class utama untuk mengelola pertarungan
    
    Attributes:
        screen: Pygame display surface
        p1, p2: Fighter objects
        ai: AIController (None jika PvP)
        mode: 'pvp' atau 'ai'
    
    Dipanggil dari: menu.py setelah character & arena selection
    """
    
    def __init__(self, char_p1, char_p2, arena, mode='pvp'):
        """
        Constructor - Setup battle
        
        Args:
            char_p1: Nama karakter P1 (dari character selection)
            char_p2: Nama karakter P2 (dari character selection)
            arena: Nama arena (dari arena selection)
            mode: 'pvp' (2 player) atau 'ai' (vs AI)
        
        Dipanggil dari: menu.py
        Membuat: Fighter P1, Fighter P2, AIController (jika mode AI)
        """
        # === INIT PYGAME ===
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Py-Fighter")
        self.clock = pygame.time.Clock()
        
        # === SIMPAN CONFIG ===
        self.mode = mode
        self.p1_name = char_p1
        self.p2_name = char_p2
        
        # === LOAD BACKGROUND ===
        # Menggunakan file dari assets/arena/
        try:
            bg_path = ARENAS.get(arena, os.path.join(BASE_DIR, 'assets/arena/Keputih.png'))
            self.bg = pygame.transform.scale(
                pygame.image.load(bg_path).convert(),
                (SCREEN_W, SCREEN_H)
            )
        except:
            self.bg = None  # Fallback: warna solid
        
        # === BUAT FIGHTERS ===
        # create_fighter() adalah Factory Method
        self.p1 = self.create_fighter(char_p1, 200, 450, False)   # P1 di kiri
        self.p2 = self.create_fighter(char_p2, 1000, 450, True)   # P2 di kanan
        
        # === SETUP AI (jika mode AI) ===
        if mode == 'ai':
            # AIController mengontrol P2, target adalah P1
            self.ai = AIController(self.p2, self.p1)
        else:
            self.ai = None
        
        # === GAME STATE ===
        self.round_over = False     # True jika ada pemenang
        self.winner = None          # 1 atau 2
        self.intro_count = 3        # Countdown sebelum mulai
        self.last_count = pygame.time.get_ticks()
    
    
    def create_fighter(self, name, x, y, flip):
        """
        Factory Method - Buat Fighter dengan konfigurasi dari CHARACTERS
        
        Args:
            name: Nama karakter (key di CHARACTERS dict)
            x, y: Posisi spawn
            flip: True jika menghadap kiri (P2)
        
        Returns:
            Fighter: Instance Fighter yang sudah dikonfigurasi
        
        Proses:
            1. Ambil data dari CHARACTERS dict
            2. Load semua sprite sheet dari folder
            3. Potong sprite sheet jadi frames
            4. Scale setiap frame
            5. Return Fighter dengan animations
        """
        # Ambil data karakter, default ke Samurai jika tidak ditemukan
        folder, scale, offset, files, frames = CHARACTERS.get(
            name, CHARACTERS['Samurai']
        )
        
        # === LOAD ANIMATIONS ===
        animations = []
        for file, num_frames in zip(files, frames):
            try:
                # Load sprite sheet
                sheet = pygame.image.load(f"{folder}/{file}").convert_alpha()
                w = sheet.get_width() // num_frames  # Lebar per frame
                h = sheet.get_height()
                
                # Potong menjadi frames individual
                anim = []
                for i in range(num_frames):
                    frame = sheet.subsurface(i * w, 0, w, h)
                    # Scale frame
                    scaled = pygame.transform.scale(
                        frame, 
                        (int(w * scale), int(h * scale))
                    )
                    anim.append(scaled)
                animations.append(anim)
                
            except Exception:
                # Fallback: dummy sprite pink
                dummy = pygame.Surface((100, 100), pygame.SRCALPHA)
                dummy.fill((255, 0, 255))
                animations.append([dummy] * num_frames)
        
        # === RETURN FIGHTER INSTANCE ===
        # Fighter class ada di fighter_base.py
        return Fighter(name, x, y, flip, 
                      {'scale': scale, 'offset': offset}, 
                      animations)
    
    
    def draw_health_bar(self, health, x, y, color):
        """
        Gambar health bar ke layar
        
        Args:
            health: HP saat ini (0-100)
            x, y: Posisi bar
            color: Warna bar HP
        """
        # Background (gelap)
        pygame.draw.rect(self.screen, (50, 50, 50), (x-2, y-2, 404, 34))
        # Base (abu-abu)
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, 400, 30))
        # HP bar (warna sesuai health)
        pygame.draw.rect(self.screen, color, (x, y, 400 * health / 100, 30))
        # Border
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 400, 30), 3)
    
    
    def draw_ui(self):
        """
        Gambar UI (health bars dan nama) ke layar
        
        Warna health bar berubah:
        - HP > 50: Cyan (P1) / Orange (P2)
        - HP 25-50: Kuning (warning)
        - HP < 25: Merah (critical)
        """
        # === TENTUKAN WARNA BERDASARKAN HP ===
        if self.p1.health > 50:
            c1 = CYAN
        elif self.p1.health > 25:
            c1 = YELLOW
        else:
            c1 = RED
        
        if self.p2.health > 50:
            c2 = ORANGE
        elif self.p2.health > 25:
            c2 = YELLOW
        else:
            c2 = RED
        
        # === GAMBAR HEALTH BARS ===
        self.draw_health_bar(self.p1.health, 50, 50, c1)
        self.draw_health_bar(self.p2.health, SCREEN_W - 450, 50, c2)
        
        # === GAMBAR NAMA ===
        font = pygame.font.Font(None, 32)
        self.screen.blit(
            font.render(f"P1: {self.p1_name}", True, CYAN), 
            (50, 20)
        )
        p2_label = "AI" if self.mode == 'ai' else "P2"
        self.screen.blit(
            font.render(f"{p2_label}: {self.p2_name}", True, ORANGE), 
            (SCREEN_W - 450, 20)
        )
    
    
    def run(self):
        """
        Main Game Loop - Inti dari game
        
        Loop:
            1. Handle events (quit, escape)
            2. Draw background
            3. Jika countdown: tampilkan angka
            4. Jika game aktif:
               - Update P1 (keyboard input)
               - Update P2 (keyboard/AI)
               - Cek pemenang
            5. Draw fighters dan UI
            6. Jika ada pemenang: tampilkan victory
        
        Returns:
            bool: True untuk kembali ke menu
        
        Dipanggil dari: menu.py setelah create BattleSystem
        """
        while True:
            self.clock.tick(FPS)  # Limit 60 FPS
            
            # === HANDLE EVENTS ===
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True  # Kembali ke menu
            
            # === DRAW BACKGROUND ===
            if self.bg:
                self.screen.blit(self.bg, (0, 0))
            else:
                self.screen.fill((50, 50, 50))
            
            # === INTRO COUNTDOWN ===
            if self.intro_count > 0:
                # Kurangi countdown setiap 1 detik
                if pygame.time.get_ticks() - self.last_count > 1000:
                    self.intro_count -= 1
                    self.last_count = pygame.time.get_ticks()
                
                # Tampilkan angka countdown
                font = pygame.font.Font(None, 200)
                txt = str(self.intro_count) if self.intro_count > 0 else "FIGHT!"
                color = YELLOW if self.intro_count > 0 else RED
                text = font.render(txt, True, color)
                self.screen.blit(text, text.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
            
            else:
                # === GAME LOGIC ===
                
                # P1 selalu pakai keyboard
                # move() ada di fighter_base.py
                self.p1.move(SCREEN_W, SCREEN_H, self.p2, self.round_over)
                
                # P2: AI atau keyboard
                if self.ai:
                    # AI update -> ai_move()
                    self.ai.update(SCREEN_W, SCREEN_H, self.round_over)
                else:
                    # Keyboard P2
                    self.p2.move(SCREEN_W, SCREEN_H, self.p1, self.round_over)
                
                # Update animasi
                self.p1.update()
                self.p2.update()
                
                # === CEK PEMENANG ===
                if not self.round_over:
                    if not self.p1.alive:
                        self.round_over = True
                        self.winner = 2
                    elif not self.p2.alive:
                        self.round_over = True
                        self.winner = 1
            
            # === DRAW FIGHTERS ===
            self.p1.draw(self.screen)
            self.p2.draw(self.screen)
            
            # === DRAW UI ===
            self.draw_ui()
            
            # === VICTORY SCREEN ===
            if self.round_over:
                # Overlay gelap
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                
                # Teks pemenang
                font = pygame.font.Font(None, 100)
                winner_name = self.p1_name if self.winner == 1 else self.p2_name
                color = CYAN if self.winner == 1 else ORANGE
                text = font.render(f"{winner_name} WINS!", True, color)
                self.screen.blit(text, text.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 50)))
                
                # Instruksi
                font2 = pygame.font.Font(None, 50)
                self.screen.blit(
                    font2.render("Press ESC to return", True, WHITE),
                    (SCREEN_W//2 - 150, SCREEN_H//2 + 50)
                )
            
            # === UPDATE DISPLAY ===
            pygame.display.update()
        
        return True


# === ENTRY POINT (untuk testing langsung) ===
if __name__ == "__main__":
    # Test langsung tanpa menu
    BattleSystem("Samurai", "Shinobi", "Keputih", "ai").run()
