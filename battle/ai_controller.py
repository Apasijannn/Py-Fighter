"""
FILE: ai_controller.py
DESKRIPSI: Otak AI menggunakan Finite State Machine (FSM)
DIGUNAKAN OLEH: battle_system.py (membuat AIController untuk mode AI)
MENGGUNAKAN: fighter_base.py (mengontrol Fighter via ai_move)

ALUR PROGRAM:
1. BattleSystem membuat AIController(fighter_p2, fighter_p1)
2. Setiap frame, AIController.update() dipanggil
3. AI mengevaluasi situasi -> pilih state -> pilih action
4. Action dikonversi ke input -> Fighter.ai_move() dipanggil

- Enum (State Pattern): AIState untuk representasi state FSM
- Composition: AIController memiliki Fighter (bukan inheritance)
- Encapsulation: Logic AI tersembunyi dari BattleSystem
"""
import pygame
import random
from enum import Enum


class AIState(Enum):
    """
    Enum untuk state FSM (Finite State Machine)
    
    State menentukan perilaku umum AI:
    - AGGRESSIVE: Serang terus, maju ke lawan
    - DEFENSIVE: Mundur, hindari serangan
    - PURSUIT: Kejar lawan yang jauh
    - RETREAT: Mundur karena HP rendah
    - PUNISH: Serang saat lawan vulnerable
    """
    AGGRESSIVE = "aggressive"   # HP tinggi, serang aktif
    DEFENSIVE = "defensive"     # Lawan menyerang, bertahan
    PURSUIT = "pursuit"         # Lawan jauh, kejar
    RETREAT = "retreat"         # HP rendah, mundur
    PUNISH = "punish"           # Lawan vulnerable, counter


class AIController:
    """
    Controller untuk AI Fighter menggunakan FSM
    
    Attributes:
        fighter: Fighter yang dikontrol (P2)
        target: Fighter lawan (P1)
        state: State FSM saat ini
    
    Dipanggil dari: BattleSystem saat mode == 'ai'
    Mempengaruhi: Fighter P2 via ai_move()
    """
    
    def __init__(self, fighter, target):
        """
        Constructor - Setup AI controller
        
        Args:
            fighter: Fighter yang akan dikontrol oleh AI (biasanya P2)
            target: Fighter lawan yang jadi target (biasanya P1)
        
        Dipanggil dari: BattleSystem.__init__() jika mode == 'ai'
        """
        # === REFERENSI KE FIGHTERS ===
        self.fighter = fighter      # Fighter yang dikontrol AI
        self.target = target        # Fighter lawan (target)
        
        # === FSM STATE ===
        self.state = AIState.PURSUIT    # Mulai dengan mengejar lawan
        self.state_timer = 0            # Timer untuk evaluasi ulang state
        
        # === SETTINGS AI ===
        self.attack_range = 120     # Jarak maksimal untuk menyerang
        self.safe_distance = 200    # Jarak aman dari lawan
        self.reaction_time = 10     # Delay antara keputusan (dalam frame)
        self.cooldown = 0           # Cooldown keputusan saat ini
        self.action = 'move_forward'    # Action yang sedang dilakukan
    
    
    def get_distance(self):
        """
        Hitung jarak horizontal ke target
        
        Returns:
            int: Jarak absolut antara center AI dan center target
        
        Digunakan oleh: evaluate_situation(), get_action()
        """
        return abs(self.fighter.rect.centerx - self.target.rect.centerx)
    
    
    def is_target_vulnerable(self):
        """
        Cek apakah target sedang dalam kondisi vulnerable
        
        Returns:
            bool: True jika target kena hit atau sedang jump
        
        Vulnerable = kesempatan bagus untuk menyerang
        Digunakan oleh: evaluate_situation()
        """
        return self.target.hit or self.target.jump
    
    
    def evaluate_situation(self):
        """
        Evaluasi situasi pertempuran dan tentukan state baru
        
        Returns:
            AIState: State yang sesuai dengan situasi
        
        Prioritas evaluasi (dari tinggi ke rendah):
            1. PUNISH - jika lawan vulnerable dan dalam range
            2. RETREAT - jika HP rendah (<25)
            3. DEFENSIVE - jika lawan sedang menyerang
            4. PURSUIT - jika lawan jauh
            5. AGGRESSIVE - jika HP >= HP lawan
            6. DEFENSIVE - default
        
        Dipanggil dari: update() setiap 30 frame
        """
        dist = self.get_distance()
        my_hp = self.fighter.health
        enemy_hp = self.target.health
        
        # === PRIORITAS STATE ===
        
        # 1. Punish lawan yang vulnerable
        if self.is_target_vulnerable() and dist < self.attack_range:
            return AIState.PUNISH
        
        # 2. HP kritis, mundur!
        if my_hp < 25:
            return AIState.RETREAT
        
        # 3. Lawan menyerang, hindari
        if self.target.attacking and dist < 200:
            return AIState.DEFENSIVE
        
        # 4. Lawan jauh, kejar
        if dist > self.safe_distance:
            return AIState.PURSUIT
        
        # 5. HP lebih tinggi, serang!
        if my_hp >= enemy_hp:
            return AIState.AGGRESSIVE
        
        # 6. Default: bertahan
        return AIState.DEFENSIVE
    
    
    def get_action(self):
        """
        Pilih action berdasarkan state saat ini
        
        Returns:
            str: Action yang akan dilakukan
                 'move_forward', 'move_back', 'jump',
                 'attack1', 'attack2', 'attack3'
        
        Setiap state punya behavior berbeda:
        - AGGRESSIVE: Serang jika dekat, maju jika jauh
        - DEFENSIVE: Mundur, sesekali serang
        - PURSUIT: Maju terus
        - RETREAT: Mundur terus
        - PUNISH: Serang dengan attack kuat
        
        Dipanggil dari: update() setiap reaction_time frame
        """
        dist = self.get_distance()
        
        # === BEHAVIOR PER STATE ===
        
        if self.state == AIState.AGGRESSIVE:
            # Serang jika dalam range, kalau tidak maju
            if dist < self.attack_range:
                return random.choice(['attack1', 'attack2', 'attack3'])
            return 'move_forward'
        
        elif self.state == AIState.DEFENSIVE:
            # Mundur jika lawan menyerang
            if self.target.attacking:
                return 'move_back'
            # Sesekali serang balik (30% chance)
            if dist < self.attack_range and random.random() < 0.3:
                return 'attack1'
            return 'move_back'
        
        elif self.state == AIState.PURSUIT:
            # Kejar lawan
            return 'move_forward'
        
        elif self.state == AIState.RETREAT:
            # Mundur, tapi kadang maju (fake out)
            if dist < 150:
                return 'move_back'
            return 'move_back' if random.random() > 0.3 else 'move_forward'
        
        elif self.state == AIState.PUNISH:
            # Serang dengan attack kuat
            if dist < self.attack_range:
                return random.choice(['attack2', 'attack3'])
            return 'move_forward'
        
        return 'move_forward'
    
    
    def update(self, screen_w, screen_h, round_over):
        """
        Main update loop AI - Dipanggil setiap frame
        
        Args:
            screen_w, screen_h: Ukuran layar
            round_over: True jika pertandingan selesai
        
        Proses:
            1. Update state FSM (setiap 30 frame)
            2. Pilih action (setiap reaction_time frame)
            3. Convert action ke input dictionary
            4. Panggil fighter.ai_move() dengan input
        
        Dipanggil dari: BattleSystem.run() jika mode == 'ai'
        Mempengaruhi: self.fighter via ai_move()
        """
        # Skip jika game selesai atau AI mati
        if round_over or not self.fighter.alive:
            return
        
        # === UPDATE STATE FSM (setiap 30 frame) ===
        self.state_timer += 1
        if self.state_timer >= 30:
            self.state = self.evaluate_situation()
            self.state_timer = 0
        
        # === PILIH ACTION (setiap reaction_time frame) ===
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.action = self.get_action()
            self.cooldown = self.reaction_time
        
        # === CONVERT ACTION KE INPUT ===
        ai_input = {
            'left': False, 
            'right': False, 
            'jump': False,
            'attack1': False, 
            'attack2': False, 
            'attack3': False
        }
        
        # Tentukan arah (AI di kanan atau kiri target?)
        facing_right = self.fighter.rect.centerx < self.target.rect.centerx
        
        if self.action == 'move_forward':
            # Maju = ke arah target
            ai_input['right' if facing_right else 'left'] = True
        elif self.action == 'move_back':
            # Mundur = menjauhi target
            ai_input['left' if facing_right else 'right'] = True
        elif self.action == 'jump':
            ai_input['jump'] = True
        elif self.action.startswith('attack'):
            ai_input[self.action] = True
        
        # === KIRIM INPUT KE FIGHTER ===
        # ai_move() ada di fighter_base.py
        self.fighter.ai_move(screen_w, screen_h, self.target, round_over, ai_input)
