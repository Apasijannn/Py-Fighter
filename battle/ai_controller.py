import pygame
import random
from enum import Enum

class AIState(Enum):
    """
    Enum untuk state FSM AI.
    """
    IDLE = "idle"
    AGGRESSIVE = "aggressive"      # Menyerang aktif
    DEFENSIVE = "defensive"        # Bertahan/menghindari
    NEUTRAL = "neutral"            # Observasi dan posisi
    PURSUIT = "pursuit"            # Mengejar lawan
    RETREAT = "retreat"            # Mundur untuk recovery
    PUNISH = "punish"              # Counter attack saat lawan vulnerable
    PRESSURE = "pressure"          # Tekan lawan yang low health


class AIController:
    """
    AI controller dengan FSM (Finite State Machine) yang lebih cerdas.
    Menggunakan evaluasi situasi, combo system, dan strategi adaptif.
    
    Args:
        fighter: Fighter object yang dikontrol AI
        target: Fighter object lawan (player 1)
        difficulty: String tingkat kesulitan ('easy', 'medium', 'hard')
    """
    
    def __init__(self, fighter, target, difficulty='medium'):
        self.fighter = fighter
        self.target = target
        self.difficulty = difficulty
        
        # FSM State
        self.current_state = AIState.PURSUIT  # Start dengan mengejar
        self.previous_state = AIState.PURSUIT
        self.state_timer = 0
        self.state_duration = 30  # Lebih responsif state transition
        
        # Action management
        self.decision_cooldown = 1  # Langsung ambil keputusan
        self.current_action = 'move_forward'  # Langsung bergerak
        self.action_timer = 10
        self.action_queue = []  # Queue untuk combo attacks
        
        # Combat tracking
        self.last_target_health = 100
        self.last_self_health = 100
        self.hits_landed = 0
        self.hits_received = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
        
        # Timing dan prediction
        self.target_attack_cooldown_estimate = 0
        self.safe_distance = 220
        self.attack_range = 180
        self.optimal_range = 150
        
        # Combo system
        self.combo_patterns = [
            ['attack1', 'attack1', 'attack2'],      # Light combo
            ['attack1', 'attack2', 'attack3'],      # Standard combo
            ['attack2', 'attack1', 'attack3'],      # Mix-up combo
            ['attack3'],                             # Heavy single
            ['attack1', 'attack1', 'attack1'],      # Rush combo
        ]
        self.current_combo = None
        self.combo_index = 0
        
        # Difficulty settings
        self._setup_difficulty(difficulty)
    
    def _setup_difficulty(self, difficulty):
        """
        Setup parameter berdasarkan difficulty level.
        
        Args:
            difficulty: String 'easy', 'medium', atau 'hard'
        """
        if difficulty == 'easy':
            self.reaction_time = 25
            self.attack_accuracy = 0.4      # Chance untuk attack decision yang benar
            self.defense_reaction = 0.3     # Chance untuk bereaksi defensif
            self.combo_chance = 0.2         # Chance untuk memulai combo
            self.prediction_skill = 0.2     # Kemampuan prediksi lawan
            self.aggression_base = 0.3
            self.optimal_play_chance = 0.3  # Chance bermain optimal
        elif difficulty == 'hard':
            self.reaction_time = 8
            self.attack_accuracy = 0.85
            self.defense_reaction = 0.8
            self.combo_chance = 0.7
            self.prediction_skill = 0.8
            self.aggression_base = 0.6
            self.optimal_play_chance = 0.85
        else:  # medium
            self.reaction_time = 15
            self.attack_accuracy = 0.6
            self.defense_reaction = 0.55
            self.combo_chance = 0.45
            self.prediction_skill = 0.5
            self.aggression_base = 0.45
            self.optimal_play_chance = 0.55
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def get_distance(self):
        """
        Hitung jarak horizontal antara AI fighter dan target.
        
        Returns:
            Integer jarak absolut dalam pixels
        """
        return abs(self.fighter.rect.centerx - self.target.rect.centerx)
    
    def get_health_ratio(self):
        """
        Hitung rasio health AI vs target.
        
        Returns:
            Float ratio (>1 berarti AI lebih sehat)
        """
        ai_health = max(self.fighter.health, 1)
        target_health = max(self.target.health, 1)
        return ai_health / target_health
    
    def is_in_attack_range(self):
        """
        Check apakah target dalam jangkauan serangan.
        
        Returns:
            Boolean True jika dalam range
        """
        return self.get_distance() <= self.attack_range
    
    def is_target_vulnerable(self):
        """
        Check apakah target dalam kondisi vulnerable (bisa di-punish).
        
        Returns:
            Boolean True jika target vulnerable
        """
        # Target vulnerable jika sedang dalam animasi hit, atau baru selesai attack
        return (self.target.hit or 
                (self.target.attacking and self.target.attack_cooldown > 10) or
                self.target.jump)
    
    def is_target_threatening(self):
        """
        Check apakah target sedang dalam posisi mengancam.
        
        Returns:
            Boolean True jika target mengancam
        """
        distance = self.get_distance()
        return (self.target.attacking and distance < 250) or \
               (self.target.running and distance < 200 and not self.target.attacking)
    
    def should_be_aggressive(self):
        """
        Evaluasi apakah AI harus agresif.
        
        Returns:
            Boolean True jika kondisi mendukung agresi
        """
        health_ratio = self.get_health_ratio()
        distance = self.get_distance()
        
        # Agresif jika: health lebih tinggi, target low health, atau dalam range optimal
        conditions = [
            health_ratio > 1.3,                          # Health advantage
            self.target.health < 30,                     # Target low health
            self.is_target_vulnerable(),                 # Target vulnerable
            distance < self.optimal_range and not self.target.attacking,  # Good position
            self.hits_landed > self.hits_received + 2    # Momentum advantage
        ]
        
        aggression_score = sum(conditions) / len(conditions)
        return random.random() < (self.aggression_base + aggression_score * 0.4)
    
    # ==================== FSM STATE EVALUATION ====================
    
    def evaluate_situation(self):
        """
        Evaluasi situasi pertarungan dan tentukan state yang tepat.
        
        Returns:
            AIState yang sesuai dengan situasi
        """
        distance = self.get_distance()
        health_ratio = self.get_health_ratio()
        ai_health = self.fighter.health
        target_health = self.target.health
        
        # Priority checks (kondisi kritis)
        
        # 1. PUNISH - Target vulnerable dan dalam range
        if self.is_target_vulnerable() and self.is_in_attack_range():
            if random.random() < self.prediction_skill:
                return AIState.PUNISH
        
        # 2. RETREAT - AI low health dan perlu recover
        if ai_health < 25 and health_ratio < 0.8:
            if random.random() < self.defense_reaction:
                return AIState.RETREAT
        
        # 3. PRESSURE - Target low health, finish them!
        if target_health < 30 and health_ratio > 0.8:
            return AIState.PRESSURE
        
        # 4. DEFENSIVE - Target attacking dan dekat
        if self.is_target_threatening():
            if random.random() < self.defense_reaction:
                return AIState.DEFENSIVE
        
        # 5. PURSUIT - Target jauh, kejar
        if distance > self.safe_distance:
            return AIState.PURSUIT
        
        # 6. AGGRESSIVE - Kondisi menguntungkan untuk attack
        if self.should_be_aggressive() and distance < self.attack_range:
            return AIState.AGGRESSIVE
        
        # 7. NEUTRAL - Default state, posisi dan observasi
        return AIState.NEUTRAL
    
    def transition_state(self, new_state):
        """
        Transisi ke state baru dengan proper handling.
        
        Args:
            new_state: AIState target
        """
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_timer = 0
            self.action_queue = []  # Clear action queue saat state berubah
            self.current_combo = None
            self.combo_index = 0
    
    # ==================== STATE BEHAVIORS ====================
    
    def behavior_aggressive(self):
        """
        Behavior untuk state AGGRESSIVE - fokus menyerang.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Jika sudah dalam combo, lanjutkan
        if self.current_combo and self.combo_index < len(self.current_combo):
            action = self.current_combo[self.combo_index]
            self.combo_index += 1
            return action
        
        # Dalam range attack
        if distance <= self.attack_range:
            # Mulai combo baru?
            if random.random() < self.combo_chance and not self.fighter.attacking:
                self.current_combo = random.choice(self.combo_patterns)
                self.combo_index = 1
                return self.current_combo[0]
            
            # Single attack - lebih agresif
            if random.random() < self.attack_accuracy + 0.2:
                # Pilih attack berdasarkan situasi
                if distance < 100:
                    return random.choice(['attack1', 'attack2'])  # Fast attacks close range
                else:
                    return random.choice(['attack1', 'attack3'])  # Mix range
            
            # Jika tidak attack, tetap serang
            return 'attack1'
        
        # Perlu mendekat - selalu maju
        return 'move_forward'
    
    def behavior_defensive(self):
        """
        Behavior untuk state DEFENSIVE - fokus menghindari dan counter.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Jika target attacking, mundur atau jump
        if self.target.attacking:
            if distance < 150:
                if random.random() < 0.7:
                    return 'move_back'
                elif not self.fighter.jump:
                    return 'jump'
            return 'move_back'
        
        # Counter attack jika ada opening
        if not self.target.attacking and distance < self.attack_range:
            if random.random() < self.attack_accuracy * 0.7:
                return 'attack1'  # Quick counter
        
        # Maintain safe distance
        if distance < self.safe_distance - 50:
            return 'move_back'
        elif distance > self.safe_distance + 50:
            return 'move_forward'
        
        return 'move_back'  # Default mundur saat defensive
    
    def behavior_neutral(self):
        """
        Behavior untuk state NEUTRAL - observasi dan positioning.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Maintain optimal range
        if distance > self.optimal_range + 30:
            return 'move_forward'
        elif distance < self.optimal_range - 30:
            if random.random() < 0.6:
                return 'move_back'
        
        # Occasional poke attack
        if distance < self.attack_range and random.random() < self.attack_accuracy * 0.5:
            return random.choice(['attack1', 'attack2'])
        
        # Lebih aktif bergerak daripada diam
        if random.random() < 0.7:
            return random.choice(['move_forward', 'move_forward', 'move_back'])
        
        return 'move_forward'
    
    def behavior_pursuit(self):
        """
        Behavior untuk state PURSUIT - mengejar target.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Jump untuk closing distance lebih cepat
        if distance > 300 and not self.fighter.jump and random.random() < 0.15:
            return 'jump'
        
        # Terus maju
        return 'move_forward'
    
    def behavior_retreat(self):
        """
        Behavior untuk state RETREAT - mundur dan recovery.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Jika target mendekat, lebih agresif mundur
        if distance < 150:
            if not self.fighter.jump and random.random() < 0.2:
                return 'jump'
            return 'move_back'
        
        # Sudah cukup jauh, bisa sedikit rileks
        if distance > self.safe_distance:
            if random.random() < 0.3:
                return 'idle'
        
        return 'move_back'
    
    def behavior_punish(self):
        """
        Behavior untuk state PUNISH - maksimalkan damage saat target vulnerable.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Start heavy combo untuk punish
        if self.current_combo and self.combo_index < len(self.current_combo):
            action = self.current_combo[self.combo_index]
            self.combo_index += 1
            return action
        
        if distance <= self.attack_range:
            # Use punish combo (heavy damage)
            if random.random() < self.optimal_play_chance:
                self.current_combo = ['attack2', 'attack3']  # Heavy punish combo
                self.combo_index = 1
                return self.current_combo[0]
            return 'attack3'  # Heavy attack
        
        return 'move_forward'
    
    def behavior_pressure(self):
        """
        Behavior untuk state PRESSURE - agresif tekan lawan yang low health.
        
        Returns:
            String action
        """
        distance = self.get_distance()
        
        # Lanjutkan combo jika ada
        if self.current_combo and self.combo_index < len(self.current_combo):
            action = self.current_combo[self.combo_index]
            self.combo_index += 1
            return action
        
        # Sangat agresif - terus serang
        if distance <= self.attack_range:
            if random.random() < self.optimal_play_chance:
                # Rush combo untuk finish
                self.current_combo = ['attack1', 'attack1', 'attack2', 'attack3']
                self.combo_index = 1
                return self.current_combo[0]
            return random.choice(['attack1', 'attack2', 'attack3'])
        
        # Kejar dengan cepat
        return 'move_forward'
    
    # ==================== MAIN DECISION LOGIC ====================
    
    def decide_action(self):
        """
        Main decision making dengan FSM.
        Evaluasi situasi, transisi state, dan tentukan action.
        
        Returns:
            String action
        """
        # Update state timer
        self.state_timer += 1
        
        # Track health changes untuk analisis
        self._track_combat_stats()
        
        # Evaluasi situasi dan kemungkinan state transition
        if self.state_timer >= self.state_duration or self._should_reevaluate():
            new_state = self.evaluate_situation()
            
            # Chance untuk tidak bermain optimal (humanize AI)
            if random.random() > self.optimal_play_chance:
                # Kadang tetap di state sekarang atau pilih suboptimal
                if random.random() < 0.5:
                    new_state = self.current_state
            
            self.transition_state(new_state)
        
        # Execute behavior berdasarkan current state
        behavior_map = {
            AIState.IDLE: self.behavior_pursuit,  # Jangan pernah idle, kejar saja
            AIState.AGGRESSIVE: self.behavior_aggressive,
            AIState.DEFENSIVE: self.behavior_defensive,
            AIState.NEUTRAL: self.behavior_neutral,
            AIState.PURSUIT: self.behavior_pursuit,
            AIState.RETREAT: self.behavior_retreat,
            AIState.PUNISH: self.behavior_punish,
            AIState.PRESSURE: self.behavior_pressure,
        }
        
        behavior_func = behavior_map.get(self.current_state, self.behavior_pursuit)
        return behavior_func()
    
    def _should_reevaluate(self):
        """
        Check apakah perlu re-evaluate state lebih awal.
        
        Returns:
            Boolean True jika perlu reevaluate
        """
        # Re-evaluate jika ada perubahan signifikan
        health_changed = abs(self.fighter.health - self.last_self_health) > 15 or \
                        abs(self.target.health - self.last_target_health) > 15
        
        # Re-evaluate jika target state berubah drastis
        threat_level_changed = self.is_target_threatening() and self.current_state not in [AIState.DEFENSIVE, AIState.RETREAT]
        
        # Re-evaluate jika dapat opportunity
        opportunity = self.is_target_vulnerable() and self.current_state not in [AIState.PUNISH, AIState.AGGRESSIVE]
        
        return health_changed or threat_level_changed or opportunity
    
    def _track_combat_stats(self):
        """
        Track combat statistics untuk adaptive behavior.
        """
        # Detect jika AI kena hit
        if self.fighter.health < self.last_self_health:
            self.hits_received += 1
        
        # Detect jika AI berhasil hit
        if self.target.health < self.last_target_health:
            self.hits_landed += 1
        
        self.last_self_health = self.fighter.health
        self.last_target_health = self.target.health
    
    def simulate_keys(self, round_over):
        """
        Simulate key presses untuk mengontrol fighter.
        
        Args:
            round_over: Boolean apakah round sudah selesai
        
        Returns:
            Dictionary dengan key pygame constants sebagai keys dan boolean sebagai values
        """
        keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_KP1: False,
            pygame.K_KP2: False,
            pygame.K_KP3: False
        }
        
        if round_over or not self.fighter.alive:
            return keys
        
        self.decision_cooldown -= 1
        self.action_timer -= 1
        
        # Decision making dengan timing yang tepat
        if self.decision_cooldown <= 0:
            self.current_action = self.decide_action()
            self.decision_cooldown = self.reaction_time
            
            # Action timer bervariasi berdasarkan action type
            if self.current_action.startswith('attack'):
                self.action_timer = 5  # Quick execution untuk attack
            elif self.current_action in ['move_forward', 'move_back']:
                self.action_timer = random.randint(8, 20)
            else:
                self.action_timer = random.randint(5, 15)
        
        if self.action_timer > 0:
            if self.current_action == 'move_forward':
                if self.target.rect.centerx > self.fighter.rect.centerx:
                    keys[pygame.K_RIGHT] = True
                else:
                    keys[pygame.K_LEFT] = True
            
            elif self.current_action == 'move_back':
                if self.target.rect.centerx > self.fighter.rect.centerx:
                    keys[pygame.K_LEFT] = True
                else:
                    keys[pygame.K_RIGHT] = True
            
            elif self.current_action == 'jump':
                keys[pygame.K_UP] = True
                self.action_timer = 0
            
            elif self.current_action == 'attack1':
                keys[pygame.K_KP1] = True
                self.action_timer = 0
            
            elif self.current_action == 'attack2':
                keys[pygame.K_KP2] = True
                self.action_timer = 0
            
            elif self.current_action == 'attack3':
                keys[pygame.K_KP3] = True
                self.action_timer = 0
        
        return keys
    
    def update(self, screen_width, screen_height, surface, round_over):
        """
        Update AI dan execute actions.
        
        Args:
            screen_width: Lebar layar game
            screen_height: Tinggi layar game
            surface: Surface untuk render
            round_over: Boolean apakah round sudah selesai
        """
        if round_over or not self.fighter.alive:
            return
        
        self.decision_cooldown -= 1
        self.action_timer -= 1
        
        # Decision making dengan timing yang tepat
        if self.decision_cooldown <= 0:
            self.current_action = self.decide_action()
            self.decision_cooldown = self.reaction_time
            
            # Action timer bervariasi berdasarkan action type
            if self.current_action.startswith('attack'):
                self.action_timer = 5
            elif self.current_action in ['move_forward', 'move_back']:
                self.action_timer = random.randint(8, 20)
            else:
                self.action_timer = random.randint(5, 15)
        
        # Build AI input
        ai_input = {
            'left': False,
            'right': False,
            'jump': False,
            'attack1': False,
            'attack2': False,
            'attack3': False
        }
        
        if self.action_timer > 0:
            if self.current_action == 'move_forward':
                if self.target.rect.centerx > self.fighter.rect.centerx:
                    ai_input['right'] = True
                else:
                    ai_input['left'] = True
            
            elif self.current_action == 'move_back':
                if self.target.rect.centerx > self.fighter.rect.centerx:
                    ai_input['left'] = True
                else:
                    ai_input['right'] = True
            
            elif self.current_action == 'jump':
                ai_input['jump'] = True
                self.action_timer = 0
            
            elif self.current_action == 'attack1':
                ai_input['attack1'] = True
                self.action_timer = 0
            
            elif self.current_action == 'attack2':
                ai_input['attack2'] = True
                self.action_timer = 0
            
            elif self.current_action == 'attack3':
                ai_input['attack3'] = True
                self.action_timer = 0
        
        # Gunakan ai_move langsung
        self.fighter.ai_move(screen_width, screen_height, surface, self.target, round_over, ai_input)
    
    def get_debug_info(self):
        """
        Get debug information tentang AI state (untuk debugging/development).
        
        Returns:
            Dictionary dengan debug info
        """
        return {
            'state': self.current_state.value,
            'action': self.current_action,
            'distance': self.get_distance(),
            'health_ratio': round(self.get_health_ratio(), 2),
            'hits_landed': self.hits_landed,
            'hits_received': self.hits_received,
            'combo': self.current_combo,
            'combo_index': self.combo_index
        }
