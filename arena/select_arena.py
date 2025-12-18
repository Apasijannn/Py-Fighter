"""
DESKRIPSI: UI untuk memilih arena pertarungan (Battle Arena)
DIGUNAKAN OLEH: menu.py atau game_manager.py
MENGGUNAKAN: pygame (untuk UI)

ALUR PROGRAM:
1. ArenaSelection().run() dipanggil
2. User melihat grid berisi pilihan arena (Keputih, San Antonio, dll)
3. User klik salah satu slot arena untuk memilih
4. User menekan SPACE untuk konfirmasi pilihan
5. Fungsi return string nama arena yang dipilih atau None jika batal

OOP CONCEPTS:
- Encapsulation: Logika slot arena dan pemilihan dibungkus dalam class
- Composition: ArenaSelection mengelola list objek ArenaSlot
"""

import pygame
import sys
import math
import os

# Base directory untuk assets (parent folder dari arena)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === KONSTANTA ===
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# === WARNA ===
WHITE = (255, 255, 255)
GOLD = (255, 200, 100)
ORANGE = (255, 150, 80)
CYAN = (100, 200, 255)

# === DATA ARENA ===
ARENAS = [
    {"name": "Keputih", "path": os.path.join(BASE_DIR, "assets/arena/Keputih.png")},
    {"name": "San Antonio", "path": os.path.join(BASE_DIR, "assets/arena/SanAntonio.png")},
    {"name": "Taman Apsari", "path": os.path.join(BASE_DIR, "assets/arena/TamanApsari.png")},
    {"name": "Tunjungan", "path": os.path.join(BASE_DIR, "assets/arena/Tunjungan.png")},
]

class ArenaSlot:
    """
    Class untuk merepresentasikan satu kartu/slot pilihan arena.
    
    Attributes:
        name: Nama arena
        x, y: Posisi koordinat slot
        slot_width, slot_height: Ukuran box slot
        is_hovered: Boolean status mouse di atas slot
        is_selected: Boolean status slot sedang dipilih
        hover_alpha: Intensitas transparansi saat hover (untuk animasi)
        hover_scale: Faktor pembesaran gambar saat hover
        image: Surface gambar arena yang sudah di-resize
    """
    
    def __init__(self, arena_data, x, y, slot_width=300, slot_height=200):
        """
        Constructor - Setup data slot arena dan muat aset gambar.
        
        Args:
            arena_data: Dictionary berisi 'name' dan 'path'
            x, y: Koordinat posisi
            slot_width, slot_height: Dimensi slot
        """
        self.name = arena_data["name"]
        self.x = x
        self.y = y
        self.slot_width = slot_width
        self.slot_height = slot_height
        self.is_hovered = False
        self.is_selected = False
        self.hover_alpha = 0
        self.select_alpha = 0
        self.hover_scale = 1.0
        
        try:
            self.original_image = pygame.image.load(arena_data["path"]).convert()
            padding = 20
            target_width = slot_width - padding * 2
            target_height = slot_height - 60
            
            img_width = self.original_image.get_width()
            img_height = self.original_image.get_height()
            scale = min(target_width / img_width, target_height / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            self.image_width = new_width
            self.image_height = new_height
            self.loaded = True
        except Exception as e:
            print(f"Gagal memuat arena {self.name}: {e}")
            self.loaded = False
    
    def update(self):
        """
        Update logika animasi internal slot (transparansi dan scaling).
        Dipanggil setiap frame di loop utama.
        """
        # Update hover animation
        if self.is_hovered:
            self.hover_alpha = min(255, self.hover_alpha + 25)
            self.hover_scale = min(1.05, self.hover_scale + 0.01)
        else:
            self.hover_alpha = max(0, self.hover_alpha - 25)
            self.hover_scale = max(1.0, self.hover_scale - 0.01)
        
        # Update selection animation
        if self.is_selected:
            self.select_alpha = min(255, self.select_alpha + 20)
        else:
            self.select_alpha = max(0, self.select_alpha - 20)
    
    def draw(self, screen):
        """
        Render komponen slot ke layar.
        
        Args:
            screen: Pygame surface utama
        """
        card_rect = pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
        
        # 1. Base Card Background
        card_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (20, 40, 80, 180), card_surf.get_rect(), border_radius=15)
        screen.blit(card_surf, (self.x, self.y))
        
        # 2. Selection Glow Effect
        if self.select_alpha > 0:
            for i in range(3):
                glow_surf = pygame.Surface((self.slot_width + 8 + i*4, self.slot_height + 8 + i*4), pygame.SRCALPHA)
                glow_rect = glow_surf.get_rect(center=(self.x + self.slot_width//2, self.y + self.slot_height//2))
                pygame.draw.rect(glow_surf, (*ORANGE, self.select_alpha // (4 + i)), 
                               glow_surf.get_rect(), border_radius=15)
                screen.blit(glow_surf, glow_rect)
            pygame.draw.rect(screen, (*ORANGE, self.select_alpha), card_rect, 4, border_radius=15)
        
        # 3. Hover Frame Effect
        if self.hover_alpha > 0:
            hover_surf = pygame.Surface((self.slot_width, self.slot_height), pygame.SRCALPHA)
            pygame.draw.rect(hover_surf, (*CYAN, self.hover_alpha // 5), hover_surf.get_rect(), border_radius=15)
            screen.blit(hover_surf, (self.x, self.y))
            pygame.draw.rect(screen, (*CYAN, self.hover_alpha), card_rect, 3, border_radius=15)
        
        # 4. Arena Image & Frame
        if self.loaded:
            scaled_w = int(self.image_width * self.hover_scale)
            scaled_h = int(self.image_height * self.hover_scale)
            scaled_image = pygame.transform.scale(self.image, (scaled_w, scaled_h))
            
            frame_padding = 10
            frame_rect = pygame.Rect(
                self.x + (self.slot_width - scaled_w) // 2 - frame_padding,
                self.y + 15 - frame_padding,
                scaled_w + frame_padding * 2,
                scaled_h + frame_padding * 2
            )
            
            # Image Frame Background
            frame_surf = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(frame_surf, (15, 30, 60, 200), frame_surf.get_rect(), border_radius=10)
            screen.blit(frame_surf, frame_rect.topleft)
            
            # Blit Scaled Image
            image_rect = scaled_image.get_rect(centerx=self.x + self.slot_width // 2, 
                                              centery=self.y + 15 + scaled_h // 2)
            screen.blit(scaled_image, image_rect)
            
            # Frame Border
            f_color = ORANGE if self.is_selected else (100, 130, 180, 150)
            pygame.draw.rect(screen, f_color, frame_rect, 2 if self.is_selected else 1, border_radius=10)
        
        # 5. Arena Name Label
        name_bg_rect = pygame.Rect(self.x + 5, self.y + self.slot_height - 45, self.slot_width - 10, 40)
        name_bg_surf = pygame.Surface((self.slot_width - 10, 40), pygame.SRCALPHA)
        pygame.draw.rect(name_bg_surf, (15, 30, 60, 220), name_bg_surf.get_rect(), border_radius=8)
        screen.blit(name_bg_surf, (self.x + 5, self.y + self.slot_height - 45))
        
        font = pygame.font.Font(None, 28)
        name_color = ORANGE if self.is_selected else WHITE
        name_text = font.render(self.name, True, name_color)
        screen.blit(name_text, name_text.get_rect(center=name_bg_rect.center))

    def get_rect(self):
        """Returns: pygame.Rect area dari slot ini."""
        return pygame.Rect(self.x, self.y, self.slot_width, self.slot_height)
    
    def check_hover(self, mouse_pos):
        """Update status hover berdasarkan posisi mouse."""
        self.is_hovered = self.get_rect().collidepoint(mouse_pos)
        return self.is_hovered


class ArenaSelection:
    """
    Screen utama untuk pemilihan arena.
    
    Menampilkan daftar arena dalam format grid dan menangani input user.
    """
    
    def __init__(self):
        """
        Constructor - Inisialisasi screen, aset background, dan grid arena.
        """
        self.slots = []
        self.selected_index = None
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arena Selection")
        self.time = 0
        
        self.load_background()
        self.load_arenas()
    
    def load_background(self):
        """Muat gambar background utama"""
        try:
            self.background = pygame.image.load(os.path.join(BASE_DIR, 'assets/menu/background.png')).convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
    
    def load_arenas(self):
        """Generate grid ArenaSlot berdasarkan data ARENAS."""
        arenas_per_row = 2
        slot_w, slot_h = 300, 200
        sp_x, sp_y = 80, 100
        
        total_w = (slot_w * arenas_per_row) + (sp_x * (arenas_per_row - 1))
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 200
        
        for i, arena_data in enumerate(ARENAS):
            row, col = i // arenas_per_row, i % arenas_per_row
            x = start_x + col * (slot_w + sp_x)
            y = start_y + row * (slot_h + sp_y)
            self.slots.append(ArenaSlot(arena_data, x, y, slot_w, slot_h))
    
    def update(self):
        """Update frame counter dan semua slot arena."""
        self.time += 1
        for slot in self.slots:
            slot.update()
    
    def draw_header(self):
        """Render judul dan animasi garis."""
        header_surf = pygame.Surface((SCREEN_WIDTH, 170), pygame.SRCALPHA)
        header_surf.fill((10, 25, 50, 150))
        self.screen.blit(header_surf, (0, 0))
        
        title_font = pygame.font.Font(None, 80)
        title_text = "SELECT BATTLE ARENA"
        
        # Title Glow & Main Text
        for i in range(3):
            glow = title_font.render(title_text, True, (*ORANGE, 60 - i*15))
            self.screen.blit(glow, glow.get_rect(center=(SCREEN_WIDTH // 2 + i, 70 + i)))
        title = title_font.render(title_text, True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))
        
        # Decorative Line
        line_w = 600
        lx = (SCREEN_WIDTH - line_w) // 2
        for i in range(3):
            off = math.sin(self.time * 0.05 + i) * 2
            pygame.draw.line(self.screen, (*ORANGE, 150 - i*40), (lx, 110 + off), (lx + line_w, 110 + off), 2 + i)
        
        # Confirmation Hint
        if self.selected_index is not None:
            inst_font = pygame.font.Font(None, 28)
            inst = inst_font.render("Press SPACE to confirm selection", True, GOLD)
            pulse = abs(math.sin(self.time * 0.1))
            inst.set_alpha(int(200 + pulse * 55))
            self.screen.blit(inst, inst.get_rect(center=(SCREEN_WIDTH // 2, 145)))

    def draw_footer(self):
        """Render panel instruksi kontrol di bagian bawah screen."""
        footer_surf = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        footer_surf.fill((10, 25, 50, 180))
        self.screen.blit(footer_surf, (0, SCREEN_HEIGHT - 60))
        
        font = pygame.font.Font(None, 24)
        controls = [("MOUSE", "Select Arena"), ("SPACE", "Confirm"), ("ESC", "Back")]
        
        start_x = (SCREEN_WIDTH - 700) // 2
        for i, (key, act) in enumerate(controls):
            x = start_x + i * (700 // len(controls))
            pygame.draw.rect(self.screen, (40, 70, 120, 200), (x + 20, SCREEN_HEIGHT - 45, 80, 22), border_radius=4)
            self.screen.blit(font.render(key, True, ORANGE), (x + 35, SCREEN_HEIGHT - 42))
            self.screen.blit(font.render(act, True, WHITE), (x + 30, SCREEN_HEIGHT - 20))

    def run(self):
        """
        Main loop untuk screen pemilihan arena.
        
        Returns:
            str: Nama arena yang dipilih jika dikonfirmasi.
            None: Jika user keluar atau menekan ESC.
        """
        clock = pygame.time.Clock()
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_SPACE and self.selected_index is not None:
                        return self.slots[self.selected_index].name
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, slot in enumerate(self.slots):
                        if slot.get_rect().collidepoint(mouse_pos):
                            if self.selected_index is not None:
                                self.slots[self.selected_index].is_selected = False
                            self.selected_index = i
                            slot.is_selected = True
                
                if event.type == pygame.MOUSEMOTION:
                    for slot in self.slots: slot.check_hover(mouse_pos)

            # Drawing logic
            if self.background:
                self.screen.blit(self.background, (0, 0))
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100)); self.screen.blit(overlay, (0, 0))
            else: self.screen.fill((20, 45, 90))
            
            self.update()
            self.draw_header()
            for slot in self.slots: slot.draw(self.screen)
            self.draw_footer()
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    result = ArenaSelection().run()
    print(f"Arena terpilih: {result}")