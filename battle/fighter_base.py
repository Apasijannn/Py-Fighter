import pygame
import os

class Fighter:
    """
    Base class untuk semua karakter fighting game.
    
    Args:
        character_name: Nama karakter (Samurai, Shinobi, Fighter, dll)
        x: Posisi x awal
        y: Posisi y awal
        flip: Boolean untuk flip sprite (True = menghadap kiri)
        data: Dictionary berisi stats karakter
        animation_list: List of lists berisi pygame surfaces untuk animasi
    """
    
    def __init__(self, character_name, x, y, flip, data, animation_list):
        self.character_name = character_name
        self.scale = data['scale']
        self.offset = data['offset']
        self.flip = flip
        self.animation_list = animation_list
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.hit = False
        self.health = 100
        self.alive = True
        self.glitch_effect = False
        self.glitch_timer = 0
        self.glitch_offset_x = 0
        self.glitch_offset_y = 0
    
    def move(self, screen_width, screen_height, surface, target, round_over):
        """
        Handle pergerakan karakter berdasarkan input.
        
        Args:
            screen_width: Lebar layar game
            screen_height: Tinggi layar game
            surface: Surface untuk render
            target: Fighter lawan (untuk collision detection)
            round_over: Boolean apakah round sudah selesai
        """
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0
        
        key = pygame.key.get_pressed()
        
        if self.attacking == False and self.alive == True and round_over == False:
            # P1 (flip=False, di kiri) menggunakan A/D/W dan R/T/Y
            # P2 (flip=True, di kanan) menggunakan Arrow keys dan Numpad
            if not self.flip:
                # P1 controls
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_r] or key[pygame.K_t] or key[pygame.K_y]:
                    self.attack(target)
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2
                    if key[pygame.K_y]:
                        self.attack_type = 3
            else:
                # P2 controls
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_KP1] or key[pygame.K_KP2] or key[pygame.K_KP3]:
                    self.attack(target)
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2
                    if key[pygame.K_KP3]:
                        self.attack_type = 3
        
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom
        
        # Collision detection dengan target (mencegah overlap/tumpang tindih)
        future_rect = self.rect.copy()
        future_rect.x += dx
        if future_rect.colliderect(target.rect):
            # Jika akan bertabrakan, hentikan pergerakan horizontal
            if dx > 0:  # Bergerak ke kanan
                dx = target.rect.left - self.rect.right
            elif dx < 0:  # Bergerak ke kiri
                dx = target.rect.right - self.rect.left
        
        # Flip hanya jika jarak cukup jauh (threshold 20 pixel) untuk mencegah glitch
        distance_x = abs(target.rect.centerx - self.rect.centerx)
        if distance_x > 20:  # Hanya flip jika jarak lebih dari 20 pixel
            if target.rect.centerx > self.rect.centerx:
                self.flip = False
            else:
                self.flip = True
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.glitch_timer > 0:
            self.glitch_timer -= 1
            if self.glitch_timer == 0:
                self.glitch_effect = False
                self.glitch_offset_x = 0
                self.glitch_offset_y = 0
        
        self.rect.x += dx
        self.rect.y += dy
    
    def trigger_glitch(self):
        """
        Trigger glitch effect saat jump.
        """
        import random
        self.glitch_effect = True
        self.glitch_timer = 10
        self.glitch_offset_x = random.randint(-5, 5)
        self.glitch_offset_y = random.randint(-5, 5)
    
    def update(self):
        """
        Update animasi karakter berdasarkan state saat ini.
        Animasi: 0=idle, 1=run, 2=jump, 3=attack1, 4=attack2, 5=attack3, 6=hit, 7=death
        """
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(7)
        elif self.hit == True:
            self.update_action(6)
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)
            elif self.attack_type == 3:
                self.update_action(5)
        elif self.jump == True:
            self.update_action(2)
        elif self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)
        
        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4 or self.action == 5:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 6:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20
    
    def attack(self, target):
        """
        Eksekusi serangan ke target.
        
        Args:
            target: Fighter yang diserang
        """
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
    
    def update_action(self, new_action):
        """
        Update action state dan reset frame jika action berubah.
        
        Args:
            new_action: Integer index animasi baru
        """
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def draw(self, surface):
        """
        Render karakter ke surface.
        
        Args:
            surface: Pygame surface untuk drawing
        """
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - self.offset[0], self.rect.y - self.offset[1]))
    
    def ai_move(self, screen_width, screen_height, surface, target, round_over, ai_input):
        """
        Handle pergerakan karakter berdasarkan AI input (tanpa keyboard).
        
        Args:
            screen_width: Lebar layar game
            screen_height: Tinggi layar game
            surface: Surface untuk render
            target: Fighter lawan
            round_over: Boolean apakah round sudah selesai
            ai_input: Dictionary dengan keys 'left', 'right', 'jump', 'attack1', 'attack2', 'attack3'
        """
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0
        
        if self.attacking == False and self.alive == True and round_over == False:
            if ai_input.get('left', False):
                dx = -SPEED
                self.running = True
            if ai_input.get('right', False):
                dx = SPEED
                self.running = True
            if ai_input.get('jump', False) and self.jump == False:
                self.vel_y = -30
                self.jump = True
            if ai_input.get('attack1', False) or ai_input.get('attack2', False) or ai_input.get('attack3', False):
                self.attack(target)
                if ai_input.get('attack1', False):
                    self.attack_type = 1
                if ai_input.get('attack2', False):
                    self.attack_type = 2
                if ai_input.get('attack3', False):
                    self.attack_type = 3
        
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom
        
        # Collision detection dengan target
        future_rect = self.rect.copy()
        future_rect.x += dx
        if future_rect.colliderect(target.rect):
            if dx > 0:
                dx = target.rect.left - self.rect.right
            elif dx < 0:
                dx = target.rect.right - self.rect.left
        
        # Flip berdasarkan posisi target
        distance_x = abs(target.rect.centerx - self.rect.centerx)
        if distance_x > 20:
            if target.rect.centerx > self.rect.centerx:
                self.flip = False
            else:
                self.flip = True
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.glitch_timer > 0:
            self.glitch_timer -= 1
            if self.glitch_timer == 0:
                self.glitch_effect = False
                self.glitch_offset_x = 0
                self.glitch_offset_y = 0
        
        self.rect.x += dx
        self.rect.y += dy
