import pygame
import sys
from battle.fighter_base import Fighter
from battle.ai_controller import AIController

pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (100, 200, 255)
ORANGE = (255, 150, 80)

CHARACTER_DATA = {
    'Samurai': {
        'folder': 'character/assets/Samurai',
        'scale': 2.5,
        'offset': [40, 30],
        'animation_files': ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        # Idle=768/128=6, Run=1024/128=8, Jump=1536/128=12, Attack1=768/128=6, Attack2=512/128=4, Attack3=384/128=3, Hurt=256/128=2, Dead=384/128=3
        'animation_steps': [6, 8, 12, 6, 4, 3, 2, 3]
    },
    'Shinobi': {
        'folder': 'character/assets/Shinobi',
        'scale': 2.5,
        'offset': [40, 30],
        'animation_files': ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        # Idle=768/128=6, Run=1024/128=8, Jump=1536/128=12, Attack1=640/128=5, Attack2=384/128=3, Attack3=512/128=4, Hurt=256/128=2, Dead=512/128=4
        'animation_steps': [6, 8, 12, 5, 3, 4, 2, 4]
    },
    'Fighter': {
        'folder': 'character/assets/Fighter',
        'scale': 2.5,
        'offset': [40, 30],
        'animation_files': ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        # Idle=768/128=6, Run=1024/128=8, Jump=1280/128=10, Attack1=512/128=4, Attack2=384/128=3, Attack3=512/128=4, Hurt=384/128=3, Dead=384/128=3
        'animation_steps': [6, 8, 10, 4, 3, 4, 3, 3]
    },
    'Converted Vampire': {
        'folder': 'character/assets/Vampire1',
        'scale': 2.0,
        'offset': [60, 50],
        'animation_files': ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        # Idle=640/128=5, Run=1024/128=8, Jump=896/128=7, Attack1=640/128=5, Attack2=384/128=3, Attack3=512/128=4, Hurt=128/128=1, Dead=1024/128=8
        'animation_steps': [5, 8, 7, 5, 3, 4, 1, 8]
    },
    'Countess Vampire': {
        'folder': 'character/assets/Vampire2',
        'scale': 2.0,
        'offset': [60, 50],
        'animation_files': ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        # Idle=640/128=5, Run=768/128=6, Jump=768/128=6, Attack1=768/128=6, Attack2=384/128=3, Attack3=128/128=1, Hurt=256/128=2, Dead=1024/128=8
        'animation_steps': [5, 6, 6, 6, 3, 1, 2, 8]
    },
    'Vampire Girl': {
        'folder': 'character/assets/Vampire3',
        'scale': 2.0,
        'offset': [60, 50],
        'animation_files': ['Idle.png', 'Run.png', 'Jump.png', 'Attack_1.png', 'Attack_2.png', 'Attack_3.png', 'Hurt.png', 'Dead.png'],
        # Idle=640/128=5, Run=768/128=6, Jump=768/128=6, Attack1=640/128=5, Attack2=512/128=4, Attack3=256/128=2, Hurt=256/128=2, Dead=1280/128=10
        'animation_steps': [5, 6, 6, 5, 4, 2, 2, 10]
    }
}


class BattleSystem:
    """
    Main battle system untuk fighting game.
    
    Args:
        char_p1: String nama karakter player 1
        char_p2: String nama karakter player 2
        arena: String nama arena
        mode: String mode game ('pvp' atau 'ai')
    """
    
    def __init__(self, char_p1, char_p2, arena, mode='pvp'):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle Arena")
        self.clock = pygame.time.Clock()
        
        self.char_p1_name = char_p1
        self.char_p2_name = char_p2
        self.arena_name = arena
        self.mode = mode
        
        self.bg_image = self.load_arena(arena)
        
        self.fighter_1 = self.create_fighter(char_p1, 200, 450, False)
        self.fighter_2 = self.create_fighter(char_p2, 1000, 450, True)
        
        self.ai_controller = None
        if mode == 'ai':
            self.ai_controller = AIController(self.fighter_2, self.fighter_1)
        
        self.intro_count = 3
        self.last_count_update = pygame.time.get_ticks()
        self.round_over = False
        self.round_over_time = 0
        self.winner = None
    
    def load_arena(self, arena_name):
        """
        Load arena background image.
        
        Args:
            arena_name: String nama arena
        
        Returns:
            Pygame surface atau None jika gagal load
        """
        arena_paths = {
            'Keputih': 'arena/assets/Keputih.png',
            'San Antonio': 'arena/assets/SanAntonio.png',
            'Taman Apsari': 'arena/assets/TamanApsari.png',
            'Tunjungan': 'arena/assets/Tunjungan.png'
        }
        
        try:
            bg = pygame.image.load(arena_paths.get(arena_name, 'arena/assets/Keputih.png')).convert()
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return bg
        except:
            return None
    
    def create_fighter(self, char_name, x, y, flip):
        """
        Create fighter instance berdasarkan character name.
        
        Args:
            char_name: String nama karakter
            x: Posisi x awal
            y: Posisi y awal
            flip: Boolean flip sprite
        
        Returns:
            Fighter instance
        """
        char_data = CHARACTER_DATA.get(char_name, CHARACTER_DATA['Samurai'])
        
        animation_list = []
        for anim_file, num_frames in zip(char_data['animation_files'], char_data['animation_steps']):
            try:
                sprite_sheet = pygame.image.load(f"{char_data['folder']}/{anim_file}").convert_alpha()
                frame_width = sprite_sheet.get_width() // num_frames
                frame_height = sprite_sheet.get_height()
                
                frames = []
                for i in range(num_frames):
                    frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                    scaled_frame = pygame.transform.scale(frame, 
                        (int(frame_width * char_data['scale']), int(frame_height * char_data['scale'])))
                    frames.append(scaled_frame)
                animation_list.append(frames)
            except Exception as e:
                dummy_frame = pygame.Surface((100, 100), pygame.SRCALPHA)
                dummy_frame.fill((255, 0, 255))
                animation_list.append([dummy_frame] * num_frames)
        
        fighter = Fighter(char_name, x, y, flip, char_data, animation_list)
        return fighter
    
    def draw_bg(self):
        """Render background arena"""
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((50, 50, 50))
    
    def draw_health_bar(self, health, x, y, color):
        """
        Render health bar.
        
        Args:
            health: Integer nilai health (0-100)
            x: Posisi x health bar
            y: Posisi y health bar
            color: Tuple RGB color health bar
        """
        ratio = health / 100
        
        pygame.draw.rect(self.screen, (50, 50, 50), (x - 2, y - 2, 404, 34))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, 400, 30))
        pygame.draw.rect(self.screen, color, (x, y, 400 * ratio, 30))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 400, 30), 3)
    
    def draw_text(self, text, font, color, x, y):
        """
        Render text ke screen.
        
        Args:
            text: String text yang akan dirender
            font: Pygame font object
            color: Tuple RGB color
            x: Posisi x
            y: Posisi y
        """
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))
    
    def draw_ui(self):
        """Render semua UI elements (health bars, names, timer)"""
        health_color_p1 = CYAN if self.fighter_1.health > 50 else (RED if self.fighter_1.health < 25 else YELLOW)
        health_color_p2 = ORANGE if self.fighter_2.health > 50 else (RED if self.fighter_2.health < 25 else YELLOW)
        
        self.draw_health_bar(self.fighter_1.health, 50, 50, health_color_p1)
        self.draw_health_bar(self.fighter_2.health, SCREEN_WIDTH - 450, 50, health_color_p2)
        
        font_name = pygame.font.Font(None, 32)
        self.draw_text(f"P1: {self.char_p1_name}", font_name, CYAN, 50, 20)
        mode_text = "P2" if self.mode == 'pvp' else "AI"
        self.draw_text(f"{mode_text}: {self.char_p2_name}", font_name, ORANGE, SCREEN_WIDTH - 450, 20)
        
        font_small = pygame.font.Font(None, 20)
        controls_p1 = "P1: A/D-Move W-Jump R/T/Y-Attack"
        controls_p2 = "P2: Arrows-Move Up-Jump Num1/2/3-Attack" if self.mode == 'pvp' else "AI Controlled"
        self.draw_text(controls_p1, font_small, (200, 200, 200), 50, SCREEN_HEIGHT - 30)
        self.draw_text(controls_p2, font_small, (200, 200, 200), SCREEN_WIDTH - 400, SCREEN_HEIGHT - 30)
    
    def check_round_over(self):
        """
        Check apakah round sudah selesai.
        
        Returns:
            Boolean True jika round over
        """
        if not self.round_over:
            if not self.fighter_1.alive:
                self.round_over = True
                self.round_over_time = pygame.time.get_ticks()
                self.winner = 2
            elif not self.fighter_2.alive:
                self.round_over = True
                self.round_over_time = pygame.time.get_ticks()
                self.winner = 1
        
        return self.round_over
    
    def draw_round_over_screen(self):
        """Render victory screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 50)
        
        if self.winner == 1:
            winner_text = f"{self.char_p1_name} WINS!"
            color = CYAN
        else:
            winner_name = f"{self.char_p2_name} ({'AI' if self.mode == 'ai' else 'P2'})"
            winner_text = f"{winner_name} WINS!"
            color = ORANGE
        
        text = font_large.render(winner_text, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        instruction = font_medium.render("Press ESC to return to menu", True, WHITE)
        inst_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction, inst_rect)
    
    def draw_intro_countdown(self):
        """
        Render countdown intro sebelum battle dimulai.
        
        Returns:
            Boolean True jika countdown masih berjalan
        """
        if self.intro_count > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            if pygame.time.get_ticks() - self.last_count_update > 1000:
                self.intro_count -= 1
                self.last_count_update = pygame.time.get_ticks()
            
            font = pygame.font.Font(None, 200)
            if self.intro_count > 0:
                text = font.render(str(self.intro_count), True, YELLOW)
            else:
                text = font.render("FIGHT!", True, RED)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            
            return True
        return False
    
    def run(self):
        """
        Main game loop untuk battle.
        
        Returns:
            Boolean True jika exit to menu, False jika quit game
        """
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
            
            self.draw_bg()
            
            if not self.draw_intro_countdown():
                if self.mode == 'ai' and self.ai_controller:
                    self.ai_controller.update(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen, self.round_over)
                else:
                    self.fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen, self.fighter_1, self.round_over)
                
                self.fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen, self.fighter_2, self.round_over)
                
                self.fighter_1.update()
                self.fighter_2.update()
                
                self.check_round_over()
            
            self.fighter_1.draw(self.screen)
            self.fighter_2.draw(self.screen)
            
            self.draw_ui()
            
            if self.round_over:
                self.draw_round_over_screen()
            
            pygame.display.update()
        
        return True


if __name__ == "__main__":
    battle = BattleSystem("Samurai", "Shinobi", "Keputih", "pvp")
    battle.run()
