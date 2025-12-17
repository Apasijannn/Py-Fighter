import pygame
import random
from enum import Enum

class AIState(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    NEUTRAL = "neutral"
    PURSUIT = "pursuit"
    RETREAT = "retreat"
    PUNISH = "punish"
    PRESSURE = "pressure"


class AIController:
    def __init__(self, fighter, target):
        self.fighter = fighter
        self.target = target
        
        # FSM State
        self.current_state = AIState.PURSUIT
        self.previous_state = AIState.PURSUIT
        self.state_timer = 0
        self.state_duration = 30
        
        # Action management
        self.decision_cooldown = 1
        self.current_action = 'move_forward'
        self.action_timer = 10
        
        # Combat tracking
        self.last_target_health = 100
        self.last_self_health = 100
        self.hits_landed = 0
        self.hits_received = 0
        
        # Distance settings
        self.safe_distance = 220
        self.attack_range = 180
        self.optimal_range = 150
        
        # Combo system
        self.combo_patterns = [
            ['attack1', 'attack1', 'attack2'],
            ['attack1', 'attack2', 'attack3'],
            ['attack2', 'attack1', 'attack3'],
            ['attack3'],
            ['attack1', 'attack1', 'attack1'],
        ]
        self.current_combo = None
        self.combo_index = 0
        
        # AI behavior settings
        self.reaction_time = 15
        self.attack_accuracy = 0.6
        self.defense_reaction = 0.55
        self.combo_chance = 0.45
        self.prediction_skill = 0.5
        self.aggression_base = 0.45
        self.optimal_play_chance = 0.55
    
    def get_distance(self):
        return abs(self.fighter.rect.centerx - self.target.rect.centerx)
    
    def get_health_ratio(self):
        ai_health = max(self.fighter.health, 1)
        target_health = max(self.target.health, 1)
        return ai_health / target_health
    
    def is_in_attack_range(self):
        return self.get_distance() <= self.attack_range
    
    def is_target_vulnerable(self):
        return (self.target.hit or 
                (self.target.attacking and self.target.attack_cooldown > 10) or
                self.target.jump)
    
    def is_target_threatening(self):
        distance = self.get_distance()
        return (self.target.attacking and distance < 250) or \
               (self.target.running and distance < 200 and not self.target.attacking)
    
    def should_be_aggressive(self):
        health_ratio = self.get_health_ratio()
        distance = self.get_distance()
        
        conditions = [
            health_ratio > 1.3,
            self.target.health < 30,
            self.is_target_vulnerable(),
            distance < self.optimal_range and not self.target.attacking,
            self.hits_landed > self.hits_received + 2
        ]
        
        aggression_score = sum(conditions) / len(conditions)
        return random.random() < (self.aggression_base + aggression_score * 0.4)
    
    def evaluate_situation(self):
        distance = self.get_distance()
        health_ratio = self.get_health_ratio()
        ai_health = self.fighter.health
        target_health = self.target.health
        
        if self.is_target_vulnerable() and self.is_in_attack_range():
            if random.random() < self.prediction_skill:
                return AIState.PUNISH
        
        if ai_health < 25 and health_ratio < 0.8:
            if random.random() < self.defense_reaction:
                return AIState.RETREAT
        
        if target_health < 30 and health_ratio > 0.8:
            return AIState.PRESSURE
        
        if self.is_target_threatening():
            if random.random() < self.defense_reaction:
                return AIState.DEFENSIVE
        
        if distance > self.safe_distance:
            return AIState.PURSUIT
        
        if self.should_be_aggressive() and distance < self.attack_range:
            return AIState.AGGRESSIVE
        
        return AIState.NEUTRAL
    
    def transition_state(self, new_state):
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_timer = 0
            self.current_combo = None
            self.combo_index = 0
    
    def behavior_aggressive(self):
        distance = self.get_distance()
        
        if self.current_combo and self.combo_index < len(self.current_combo):
            action = self.current_combo[self.combo_index]
            self.combo_index += 1
            return action
        
        if distance <= self.attack_range:
            if random.random() < self.combo_chance and not self.fighter.attacking:
                self.current_combo = random.choice(self.combo_patterns)
                self.combo_index = 1
                return self.current_combo[0]
            
            if random.random() < self.attack_accuracy + 0.2:
                if distance < 100:
                    return random.choice(['attack1', 'attack2'])
                else:
                    return random.choice(['attack1', 'attack3'])
            
            return 'attack1'
        
        return 'move_forward'
    
    def behavior_defensive(self):
        distance = self.get_distance()
        
        if self.target.attacking:
            if distance < 150:
                if random.random() < 0.7:
                    return 'move_back'
                elif not self.fighter.jump:
                    return 'jump'
            return 'move_back'
        
        if not self.target.attacking and distance < self.attack_range:
            if random.random() < self.attack_accuracy * 0.7:
                return 'attack1'
        
        if distance < self.safe_distance - 50:
            return 'move_back'
        elif distance > self.safe_distance + 50:
            return 'move_forward'
        
        return 'move_back'
    
    def behavior_neutral(self):
        distance = self.get_distance()
        
        if distance > self.optimal_range + 30:
            return 'move_forward'
        elif distance < self.optimal_range - 30:
            if random.random() < 0.6:
                return 'move_back'
        
        if distance < self.attack_range and random.random() < self.attack_accuracy * 0.5:
            return random.choice(['attack1', 'attack2'])
        
        if random.random() < 0.7:
            return random.choice(['move_forward', 'move_forward', 'move_back'])
        
        return 'move_forward'
    
    def behavior_pursuit(self):
        distance = self.get_distance()
        
        if distance > 300 and not self.fighter.jump and random.random() < 0.15:
            return 'jump'
        
        return 'move_forward'
    
    def behavior_retreat(self):
        distance = self.get_distance()
        
        if distance < 150:
            if not self.fighter.jump and random.random() < 0.2:
                return 'jump'
            return 'move_back'
        
        if distance > self.safe_distance:
            if random.random() < 0.3:
                return 'move_forward'
        
        return 'move_back'
    
    def behavior_punish(self):
        distance = self.get_distance()
        
        if self.current_combo and self.combo_index < len(self.current_combo):
            action = self.current_combo[self.combo_index]
            self.combo_index += 1
            return action
        
        if distance <= self.attack_range:
            if random.random() < self.optimal_play_chance:
                self.current_combo = ['attack2', 'attack3']
                self.combo_index = 1
                return self.current_combo[0]
            return 'attack3'
        
        return 'move_forward'
    
    def behavior_pressure(self):
        distance = self.get_distance()
        
        if self.current_combo and self.combo_index < len(self.current_combo):
            action = self.current_combo[self.combo_index]
            self.combo_index += 1
            return action
        
        if distance <= self.attack_range:
            if random.random() < self.optimal_play_chance:
                self.current_combo = ['attack1', 'attack1', 'attack2', 'attack3']
                self.combo_index = 1
                return self.current_combo[0]
            return random.choice(['attack1', 'attack2', 'attack3'])
        
        return 'move_forward'
    
    def decide_action(self):
        self.state_timer += 1
        self._track_combat_stats()
        
        if self.state_timer >= self.state_duration or self._should_reevaluate():
            new_state = self.evaluate_situation()
            
            if random.random() > self.optimal_play_chance:
                if random.random() < 0.5:
                    new_state = self.current_state
            
            self.transition_state(new_state)
        
        behavior_map = {
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
        health_changed = abs(self.fighter.health - self.last_self_health) > 15 or \
                        abs(self.target.health - self.last_target_health) > 15
        
        threat_level_changed = self.is_target_threatening() and \
                              self.current_state not in [AIState.DEFENSIVE, AIState.RETREAT]
        
        opportunity = self.is_target_vulnerable() and \
                     self.current_state not in [AIState.PUNISH, AIState.AGGRESSIVE]
        
        return health_changed or threat_level_changed or opportunity
    
    def _track_combat_stats(self):
        if self.fighter.health < self.last_self_health:
            self.hits_received += 1
        
        if self.target.health < self.last_target_health:
            self.hits_landed += 1
        
        self.last_self_health = self.fighter.health
        self.last_target_health = self.target.health
    
    def update(self, screen_width, screen_height, surface, round_over):
        if round_over or not self.fighter.alive:
            return
        
        self.decision_cooldown -= 1
        self.action_timer -= 1
        
        if self.decision_cooldown <= 0:
            self.current_action = self.decide_action()
            self.decision_cooldown = self.reaction_time
            
            if self.current_action.startswith('attack'):
                self.action_timer = 5
            elif self.current_action in ['move_forward', 'move_back']:
                self.action_timer = random.randint(8, 20)
            else:
                self.action_timer = random.randint(5, 15)
        
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
        
        self.fighter.ai_move(screen_width, screen_height, surface, self.target, round_over, ai_input)
