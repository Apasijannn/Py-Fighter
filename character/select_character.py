"""
FILE: character_selection.py
DESKRIPSI: UI untuk memilih karakter pemain (P1 dan P2/AI)
DIGUNAKAN OLEH: menu.py
MENGGUNAKAN: pygame (untuk UI), random (untuk pemilihan AI)

ALUR PROGRAM:
1. CharacterSelection(game_mode).run() dipanggil dengan mode 'pvp' atau 'ai'.
2. User memilih karakter dengan klik pada slot yang tersedia.
3. Jika mode 'ai', sistem otomatis memilihkan karakter lawan secara acak.
4. Jika mode 'pvp', Player 2 memilih setelah Player 1 selesai.
5. Menekan SPACE setelah kedua pemain siap akan mengembalikan nama karakter yang dipilih.

OOP CONCEPTS:
- Encapsulation: Logika animasi dan status setiap karakter dibungkus dalam CharacterSlot.
- Composition: CharacterSelection mengelola sekumpulan objek CharacterSlot.
"""

import pygame
import sys
import math
import random

# === KONSTANTA ===
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
ANIMATION_SPEED = 8

# === WARNA ===
WHITE = (255, 255, 255)
GOLD = (255, 200, 100)
ORANGE = (255, 150, 80)
CYAN = (100, 200, 255)
P1_COLOR = CYAN
P2_COLOR = ORANGE

# === DATA KARAKTER ===
CHARACTERS = [
    {"name": "Samurai", "path": "assets/character/Samurai/Idle.png", "frames": 6},
    {"name": "Shinobi", "path": "assets/character/Shinobi/Idle.png", "frames": 6},
    {"name": "Fighter", "path": "assets/character/Fighter/Idle.png", "frames": 6},
    {"name": "Converted Vampire", "path": "assets/character/Vampire1/Idle.png", "frames": 5},
    {"name": "Countess Vampire", "path": "assets/character/Vampire2/Idle.png", "frames": 5},
    {"name": "Vampire Girl", "path": "assets/character/Vampire3/Idle.png", "frames": 5},
]

class CharacterSlot:
    """
    Class untuk merepresentasikan kartu pilihan karakter dalam grid.
    
    Attributes:
        name: Nama karakter.
        num_frames: Jumlah frame animasi dalam spritesheet.
        frames: List berisi Surface pygame untuk setiap frame animasi.
        is_hovered: Status apakah mouse sedang berada di atas slot.
        is_selected_p1/p2: Status apakah karakter ini dipilih oleh P1 atau P2.
    """
    
    def __init__(self, char_data, x, y, slot_width=180, slot_height=200):
        """
        Constructor - Setup data slot karakter dan memproses spritesheet.
        
        Args:
            char_data: Dictionary berisi info karakter (nama, path, frames).
            x, y: Posisi koordinat slot di layar.
            slot_width, slot_height: Dimensi kartu slot.
        """
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
            
            scale_x = (slot_width - 40) / sprite_width
            scale_y = (slot_height - 80) / sprite_height
            scale = min(scale_x, scale_y, 2.5)
            
            self.frames = []
            for i in range(self.num_frames):
                frame = spritesheet.subsurface(pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height))
                frame = pygame.transform.scale(frame, (int(sprite_width * scale), int(sprite_height * scale)))
                self.frames.append(frame)
            
            self.sprite_width = int(sprite_width * scale)
            self.sprite_height = int(sprite_height * scale)
            self.loaded = True
        except:
            self.loaded = False
    
    def update(self):
        """Update frame animasi karakter dan transparansi efek visual."""
        if self.loaded:
            self.frame_counter += 1
            if self.frame_counter >= ANIMATION_SPEED:
                self.frame_counter = 0
                self.current_frame = (self.current_frame + 1) % self.num_frames
        
        self.hover_alpha = min(255, self.hover_alpha + 25) if self.is_hovered else max(0, self.hover_alpha - 25)
        self.select_alpha_p1 = min(255, self.select_alpha_p1 + 20) if self.is_selected_p1 else max(0, self.select_alpha_p1 - 20)
        self.select_alpha_p2 = min(255, self.select_alpha_p2 + 20) if self.is_selected_p2 else max(0, self.select_alpha_p2 - 20)

    def draw(self, screen):
        """
        Render slot karakter, animasi idle, dan efek glow pemilihan.
        
        Args:
            screen: Surface utama tempat merender.
        """
        card_rect = pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
        
        # 1. Background Dasar
        card_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (20, 40, 80, 180), card_surf.get_rect(), border_radius=15)
        screen.blit(card_surf, (self.x, self.y))

        # 2. Render Glow Selection P1 & P2
        for p_color, alpha in [(P1_COLOR, self.select_alpha_p1), (P2_COLOR, self.select_alpha_p2)]:
            if alpha > 0:
                for i in range(3):
                    glow_surf = pygame.Surface((self.slot_width + 8 + i*4, self.slot_height + 8 + i*4), pygame.SRCALPHA)
                    glow_rect = glow_surf.get_rect(center=(self.x + self.slot_width//2, self.y + self.slot_height//2))
                    pygame.draw.rect(glow_surf, (*p_color, alpha // (4 + i)), glow_surf.get_rect(), border_radius=15)
                    screen.blit(glow_surf, glow_rect)
                pygame.draw.rect(screen, (*p_color, alpha), card_rect, 4, border_radius=15)

        # 3. Gambar Karakter & Label Nama
        if self.loaded:
            frame_rect = self.frames[self.current_frame].get_rect(centerx=self.x + self.slot_width // 2, centery=self.y + 85)
            screen.blit(self.frames[self.current_frame], frame_rect)
            
            name_font = pygame.font.Font(None, 22)
            name_color = P1_COLOR if self.is_selected_p1 else (P2_COLOR if self.is_selected_p2 else WHITE)
            name_text = name_font.render(self.name, True, name_color)
            screen.blit(name_text, name_text.get_rect(center=(self.x + self.slot_width//2, self.y + self.slot_height - 25)))
            
    def get_rect(self):
        """Returns: Objek Rect dari slot untuk deteksi klik."""
        return pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)

class CharacterSelection:
    """
    Kelas utama pengelola layar pemilihan karakter.
    
    Menangani alur pemilihan berdasarkan mode (PvP atau AI) dan aset UI pendukung.
    """
    
    def __init__(self, game_mode='ai'): 
        """
        Constructor - Inisialisasi screen, badges, dan memuat grid karakter.
        
        Args:
            game_mode: String 'pvp' atau 'ai'.
        """
        self.game_mode = game_mode
        self.slots = []
        self.selected_index_p1 = None
        self.selected_index_p2 = None
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.time = 0
        self.both_ready = False
        
        self.load_background()
        self.load_badges()
        self.load_characters()
    
    def load_badges(self):
        """Memuat ikon badge (P1, P2, AI) yang akan diletakkan di atas slot terpilih."""
        try:
            self.p1_badge = pygame.transform.scale(pygame.image.load('assets/select_char/p1.png').convert_alpha(), (50, 50))
        except: self.p1_badge = None
        
        badge_p2_path = 'assets/select_char/ai.png' if self.game_mode == 'ai' else 'assets/select_char/p2.png'
        try:
            self.p2_badge = pygame.transform.scale(pygame.image.load(badge_p2_path).convert_alpha(), (50, 50))
        except: self.p2_badge = None

    def load_background(self):
        """Memuat gambar background menu."""
        try:
            self.background = pygame.transform.scale(pygame.image.load('assets/menu/background.png').convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        except: self.background = None

    def load_characters(self):
        """Mengatur posisi grid untuk setiap CharacterSlot di layar."""
        start_x, start_y = (SCREEN_WIDTH - 640) // 2, 220
        for i, char_data in enumerate(CHARACTERS):
            x = start_x + (i % 3) * 230
            y = start_y + (i // 3) * 270
            self.slots.append(CharacterSlot(char_data, x, y))

    def update(self):
        """Update status seluruh elemen dan cek kesiapan kedua pemain."""
        self.time += 1
        for slot in self.slots: slot.update()
        self.both_ready = self.selected_index_p1 is not None and self.selected_index_p2 is not None

    def draw_header(self):
        """Render header teks, efek glow judul, dan instruksi giliran pemain."""
        header_surf = pygame.Surface((SCREEN_WIDTH, 180), pygame.SRCALPHA)
        header_surf.fill((10, 25, 50, 150))
        self.screen.blit(header_surf, (0, 0))
        
        title_font = pygame.font.Font(None, 80)
        title_text = "SELECT YOUR CHARACTER"
        for i in range(3):
            glow = title_font.render(title_text, True, (*ORANGE, 60 - i*15))
            self.screen.blit(glow, glow.get_rect(center=(SCREEN_WIDTH // 2 + i, 70 + i)))
        self.screen.blit(title_font.render(title_text, True, WHITE), title_font.render(title_text, True, WHITE).get_rect(center=(SCREEN_WIDTH // 2, 70)))
        
        # Animated Decorative Line
        line_w = 600
        lx = (SCREEN_WIDTH - line_w) // 2
        for i in range(3):
            off = math.sin(self.time * 0.05 + i) * 2
            pygame.draw.line(self.screen, (*ORANGE, 150 - i*40), (lx, 110 + off), (lx + line_w, 110 + off), 2 + i)
        
        # Turn Instructions
        if not self.both_ready:
            turn_font = pygame.font.Font(None, 35)
            t_text, t_color = ("", WHITE)
            if self.selected_index_p1 is None:
                t_text, t_color = "PLAYER 1: CHOOSE YOUR HERO", P1_COLOR
            elif self.game_mode == 'pvp' and self.selected_index_p2 is None:
                t_text, t_color = "PLAYER 2: YOUR TURN", P2_COLOR
            
            if t_text:
                alpha = int(155 + abs(math.sin(self.time * 0.1)) * 100)
                s = turn_font.render(t_text, True, t_color)
                s.set_alpha(alpha)
                self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        else:
            inst = pygame.font.Font(None, 35).render("PRESS SPACE TO START FIGHT!", True, GOLD)
            inst.set_alpha(int(155 + abs(math.sin(self.time * 0.1)) * 100))
            self.screen.blit(inst, inst.get_rect(center=(SCREEN_WIDTH // 2, 140)))
            
    def draw_footer(self):
        """Render panel instruksi kontrol di bagian bawah."""
        footer_surf = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        footer_surf.fill((10, 25, 50, 180))
        self.screen.blit(footer_surf, (0, SCREEN_HEIGHT - 70))
        
        font = pygame.font.Font(None, 24)
        ctrls = [("CLICK", "Select"), ("SPACE", "Confirm" if self.both_ready else "Wait"), ("ESC", "Menu")]
        for i, (key, act) in enumerate(ctrls):
            x = (SCREEN_WIDTH - 800) // 2 + i * 266
            pygame.draw.rect(self.screen, (40, 70, 120, 200), (x + 40, SCREEN_HEIGHT - 52, 90, 24), border_radius=4)
            self.screen.blit(font.render(key, True, GOLD), (x + 60, SCREEN_HEIGHT - 48))
            self.screen.blit(font.render(act, True, WHITE), (x + 60, SCREEN_HEIGHT - 25))
            
    def draw(self):
        """Main draw function - Menggabungkan seluruh elemen visual ke layar."""
        if self.background: self.screen.blit(self.background, (0, 0))
        else: self.screen.fill((10, 20, 40))
        
        self.draw_header()
        for slot in self.slots: slot.draw(self.screen)
        
        # Draw Badges (P1 & P2/AI)
        if self.selected_index_p1 is not None and self.p1_badge:
            self.screen.blit(self.p1_badge, (self.slots[self.selected_index_p1].x + 5, self.slots[self.selected_index_p1].y + 5))
        if self.selected_index_p2 is not None and self.p2_badge:
            s = self.slots[self.selected_index_p2]
            self.screen.blit(self.p2_badge, (s.x + s.slot_width - 55, s.y + 5))
            
        self.draw_footer()
        pygame.display.flip()

    def handle_click(self, mouse_pos):
        """Mengelola logika seleksi karakter saat slot diklik."""
        for i, slot in enumerate(self.slots):
            if slot.get_rect().collidepoint(mouse_pos):
                # Deselect P1
                if self.selected_index_p1 == i:
                    slot.is_selected_p1 = False
                    self.selected_index_p1 = None
                    if self.game_mode == 'ai' and self.selected_index_p2 is not None:
                        self.slots[self.selected_index_p2].is_selected_p2 = False
                        self.selected_index_p2 = None
                    return

                # P2 Selection (PvP)
                if self.game_mode == 'pvp' and self.selected_index_p1 is not None:
                    if self.selected_index_p2 == i:
                        slot.is_selected_p2 = False
                        self.selected_index_p2 = None
                    elif self.selected_index_p2 is None and i != self.selected_index_p1:
                        self.selected_index_p2 = i
                        slot.is_selected_p2 = True
                    return

                # Initial P1 Selection & AI Auto-pick
                if self.selected_index_p1 is None:
                    self.selected_index_p1 = i
                    slot.is_selected_p1 = True
                    if self.game_mode == 'ai':
                        available = [idx for idx in range(len(self.slots)) if idx != i]
                        self.selected_index_p2 = random.choice(available)
                        self.slots[self.selected_index_p2].is_selected_p2 = True
                    return
            
    def run(self):
        """
        Loop utama layar pemilihan karakter.
        
        Returns:
            tuple: (Nama Karakter P1, Nama Karakter P2/AI) jika sukses.
            None: Jika dibatalkan (ESC atau Quit).
        """
        clock = pygame.time.Clock()
        while True:
            m_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.MOUSEBUTTONDOWN: self.handle_click(m_pos)
                if event.type == pygame.MOUSEMOTION:
                    for s in self.slots: s.is_hovered = s.get_rect().collidepoint(m_pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.both_ready:
                        return self.slots[self.selected_index_p1].name, self.slots[self.selected_index_p2].name
                    if event.key == pygame.K_ESCAPE: return None
            self.update()
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    result = CharacterSelection(game_mode='pvp').run()
    if result: print(f"Match: {result[0]} vs {result[1]}")