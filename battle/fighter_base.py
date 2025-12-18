"""
DESKRIPSI: Class utama untuk karakter fighter dalam game
DIGUNAKAN OLEH: battle_system.py (membuat instance Fighter)
MENGGUNAKAN: pygame (untuk rendering dan input)

ALUR PROGRAM:
1. BattleSystem membuat Fighter via create_fighter()
2. Setiap frame, Fighter.move() atau Fighter.ai_move() dipanggil
3. Fighter.update() mengupdate animasi berdasarkan state
4. Fighter.draw() menggambar karakter ke layar

- Encapsulation: Semua atribut karakter dibungkus dalam class
- Method: move(), ai_move(), attack(), update(), draw()
"""
import pygame


class Fighter:
    """
    Class Fighter - Representasi karakter yang bisa bertarung
    
    Attributes:
        name (str): Nama karakter
        rect (Rect): Posisi dan ukuran hitbox karakter
        health (int): HP karakter (0-100)
        alive (bool): Status hidup/mati
        animations (list): Kumpulan sprite animasi
    """
    
    def __init__(self, name, x, y, flip, data, animations):
        """
        Constructor - Dipanggil saat membuat Fighter baru
        
        Args:
            name: Nama karakter (untuk display)
            x, y: Posisi awal di layar
            flip: True jika menghadap kiri (P2)
            data: Dictionary berisi scale dan offset sprite
            animations: List of sprite frames untuk setiap action
        
        Dipanggil dari: BattleSystem.create_fighter()
        """
        # === DATA KARAKTER ===
        self.name = name
        self.flip = flip                    # True = hadap kiri, False = hadap kanan
        self.animations = animations        # Sprite animations dari battle_system.py
        self.scale = data['scale']
        self.offset = data['offset']        # Offset untuk positioning sprite
        
        # === POSISI & FISIKA ===
        self.rect = pygame.Rect(x, y, 80, 180)  # Hitbox karakter (x, y, width, height)
        self.vel_y = 0                          # Kecepatan vertikal (untuk jump)
        
        # === STATUS KARAKTER ===
        self.health = 100           # HP: 0 = mati, 100 = full
        self.alive = True           # False jika HP <= 0
        self.running = False        # True jika sedang bergerak
        self.jump = False           # True jika sedang di udara
        self.attacking = False      # True jika sedang animasi attack
        self.attack_type = 0        # 1=Attack1, 2=Attack2, 3=Attack3
        self.attack_cooldown = 0    # Delay antar serangan (dalam frames)
        self.hit = False            # True jika baru terkena serangan
        
        # === ANIMASI ===
        self.action = 0             # Index animasi saat ini (0=idle, 1=run, dst)
        self.frame_index = 0        # Frame ke-berapa dalam animasi
        self.image = self.animations[0][0]  # Sprite yang sedang ditampilkan
        self.update_time = pygame.time.get_ticks()  # Waktu update frame terakhir
    
    
    def move(self, screen_w, screen_h, target, round_over):
        """
        Handle input keyboard untuk Player (manusia)
        
        Args:
            screen_w, screen_h: Ukuran layar (untuk batas gerak)
            target: Fighter lawan (untuk collision & attack)
            round_over: True jika pertandingan sudah selesai
        
        Controls:
            P1 (flip=False): WASD + R/T/Y untuk attack
            P2 (flip=True): Arrow keys + Numpad 1/2/3 untuk attack
        
        Dipanggil dari: BattleSystem.run() setiap frame
        """
        SPEED = 10      # Kecepatan gerak horizontal (pixel/frame)
        GRAVITY = 2     # Kecepatan jatuh (untuk jump)
        dx, dy = 0, 0   # Perpindahan frame ini
        self.running = False
        
        # Hanya bisa bergerak jika tidak sedang attack dan masih hidup
        if not self.attacking and self.alive and not round_over:
            self.attack_type = 0
            key = pygame.key.get_pressed()
            
            # === TENTUKAN KONTROL BERDASARKAN PLAYER ===
            if not self.flip:  # Player 1 (kiri)
                left, right, up = pygame.K_a, pygame.K_d, pygame.K_w
                atk_keys = [pygame.K_r, pygame.K_t, pygame.K_y]  # Attack 1, 2, 3
            else:              # Player 2 (kanan)
                left, right, up = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP
                atk_keys = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3]  # Numpad 1, 2, 3
            
            # === HANDLE INPUT GERAK ===
            if key[left]: 
                dx = -SPEED
                self.running = True
            if key[right]: 
                dx = SPEED
                self.running = True
            if key[up] and not self.jump: 
                self.vel_y = -30    # Lompat ke atas
                self.jump = True
            
            # === HANDLE INPUT ATTACK ===
            for i, k in enumerate(atk_keys):
                if key[k]:
                    self.attack(target)         # -> Panggil method attack()
                    self.attack_type = i + 1    # 1, 2, atau 3
        
        # Terapkan fisika (gravity, collision, batas layar)
        self._apply_physics(dx, dy, screen_w, screen_h, target, GRAVITY)
    
    
    def ai_move(self, screen_w, screen_h, target, round_over, ai_input):
        """
        Handle gerakan untuk AI (bukan keyboard, tapi dari AIController)
        
        Args:
            ai_input: Dictionary dari AIController berisi:
                      {'left': bool, 'right': bool, 'jump': bool,
                       'attack1': bool, 'attack2': bool, 'attack3': bool}
        
        Dipanggil dari: AIController.update() -> fighter.ai_move()
        """
        SPEED, GRAVITY = 10, 2
        dx, dy = 0, 0
        self.running = False
        
        if not self.attacking and self.alive and not round_over:
            self.attack_type = 0
            
            # === BACA INPUT DARI AI ===
            if ai_input.get('left'): 
                dx, self.running = -SPEED, True
            if ai_input.get('right'): 
                dx, self.running = SPEED, True
            if ai_input.get('jump') and not self.jump: 
                self.vel_y, self.jump = -30, True
            
            # === CEK ATTACK INPUT ===
            for i in range(1, 4):
                if ai_input.get(f'attack{i}'):
                    self.attack(target)
                    self.attack_type = i
        
        self._apply_physics(dx, dy, screen_w, screen_h, target, GRAVITY)
    
    
    def _apply_physics(self, dx, dy, screen_w, screen_h, target, gravity):
        """
        Private method - Terapkan fisika dan collision
        
        Args:
            dx, dy: Perpindahan yang diinginkan
            target: Lawan (untuk collision)
            gravity: Konstanta gravitasi
        
        Proses:
            1. Terapkan gravitasi ke vel_y
            2. Cek batas layar (kiri, kanan, bawah)
            3. Cek collision dengan lawan
            4. Auto-flip menghadap lawan
        """
        # === GRAVITASI ===
        self.vel_y += gravity   # Tambah kecepatan jatuh
        dy += self.vel_y        # Terapkan ke perpindahan
        
        # === BATAS LAYAR ===
        if self.rect.left + dx < 0:                     # Batas kiri
            dx = -self.rect.left
        if self.rect.right + dx > screen_w:            # Batas kanan
            dx = screen_w - self.rect.right
        if self.rect.bottom + dy > screen_h - 110:     # Batas bawah (lantai)
            self.vel_y = 0
            self.jump = False
            dy = screen_h - 110 - self.rect.bottom
        
        # === COLLISION DENGAN LAWAN ===
        future = self.rect.copy()
        future.x += dx
        if future.colliderect(target.rect):
            if dx > 0:      # Gerak ke kanan, tabrak lawan
                dx = target.rect.left - self.rect.right - 10
            elif dx < 0:    # Gerak ke kiri, tabrak lawan
                dx = target.rect.right - self.rect.left + 10
        
        # === AUTO-FLIP MENGHADAP LAWAN ===
        if abs(target.rect.centerx - self.rect.centerx) > 20:
            self.flip = target.rect.centerx < self.rect.centerx
        
        # === UPDATE COOLDOWN & POSISI ===
        if self.attack_cooldown > 0: 
            self.attack_cooldown -= 1
        self.rect.x += dx
        self.rect.y += dy
    
    
    def attack(self, target):
        """
        Lakukan serangan ke target
        
        Args:
            target: Fighter lawan
        
        Proses:
            1. Cek cooldown (tidak bisa spam attack)
            2. Buat attack hitbox di depan karakter
            3. Jika hitbox kena target, kurangi HP target
        
        Dipanggil dari: move() atau ai_move() saat tekan tombol attack
        Mempengaruhi: target.health, target.hit
        """
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_cooldown = 20   # Delay 20 frame sebelum bisa attack lagi
            
            # === BUAT ATTACK HITBOX ===
            if self.flip:   # Hadap kiri
                atk_x = self.rect.left - self.rect.width
            else:           # Hadap kanan
                atk_x = self.rect.right
            
            atk_rect = pygame.Rect(atk_x, self.rect.y, 
                                   self.rect.width * 1.5, self.rect.height)
            
            # === CEK HIT ===
            if atk_rect.colliderect(target.rect):
                target.health -= 10     # Kurangi HP lawan
                target.hit = True       # Trigger animasi hurt
    
    
    def update(self):
        """
        Update animasi berdasarkan state karakter
        
        Index animasi:
            0 = Idle (diam)
            1 = Run (lari)
            2 = Jump (lompat)
            3 = Attack 1
            4 = Attack 2
            5 = Attack 3
            6 = Hurt (kena hit)
            7 = Death (mati)
        
        Dipanggil dari: BattleSystem.run() setiap frame
        """
        # === TENTUKAN ANIMASI BERDASARKAN STATE ===
        if self.health <= 0:
            self.health = 0
            self.alive = False
            new_action = 7              # Death animation
        elif self.hit: 
            new_action = 6              # Hurt animation
        elif self.attacking: 
            new_action = 2 + self.attack_type   # Attack 1/2/3 = index 3/4/5
        elif self.jump: 
            new_action = 2              # Jump animation
        elif self.running: 
            new_action = 1              # Run animation
        else: 
            new_action = 0              # Idle animation
        
        # === GANTI ANIMASI JIKA BERBEDA ===
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0        # Reset ke frame pertama
            self.update_time = pygame.time.get_ticks()
        
        # === UPDATE FRAME ANIMASI ===
        self.image = self.animations[self.action][self.frame_index]
        
        if pygame.time.get_ticks() - self.update_time > 50:  # 50ms per frame
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        
        # === HANDLE ANIMASI SELESAI ===
        if self.frame_index >= len(self.animations[self.action]):
            if not self.alive:
                # Mati: tetap di frame terakhir
                self.frame_index = len(self.animations[self.action]) - 1
            else:
                self.frame_index = 0    # Loop animasi
                if self.action in [3, 4, 5]:    # Attack selesai
                    self.attacking = False
                if self.action == 6:            # Hurt selesai
                    self.hit = False
    
    
    def draw(self, surface):
        """
        Gambar karakter ke layar
        
        Args:
            surface: Pygame surface (screen) untuk menggambar
        
        Proses:
            1. Flip sprite jika karakter menghadap kiri
            2. Blit sprite ke posisi dengan offset
        
        Dipanggil dari: BattleSystem.run() setiap frame
        """
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - self.offset[0], 
                          self.rect.y - self.offset[1]))
