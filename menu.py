import pygame 
import sys
from pygame import mixer
from character.select_character import CharacterSelection
from arena.select_arena import ArenaSelection
from battle.mode_selection import ModeSelection
from battle.battle_system import BattleSystem

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

# load display surface
pygame.init()

menu_state = "main"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Menu")
background = pygame.image.load('background.png').convert_alpha()

# load logo image
logo = pygame.image.load('logo.png').convert_alpha()
# logo scaling
logo = pygame.transform.scale(logo, (int(logo.get_width() * 0.9), int(logo.get_height() * 0.9)))
icon = pygame.image.load('iconn.png').convert_alpha()
pygame.display.set_icon(icon)

# background music
mixer.music.load('menu.mp3')
mixer.music.play(-1)
mixer.music.set_volume(0.05)
mixer.music.set_pos(2.4)

# load button images
play_image = pygame.image.load('play.png').convert_alpha()
exit_image = pygame.image.load('exit.png').convert_alpha()

#button class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False  # Initialize clicked attribute
        
    def draw(self, surface): 
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos() 
        
        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            # Check for left click
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True # Button was clicked this frame
        
        # Reset clicked state when the left mouse button is released
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            
        # draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))
        
        return action
        
#button instances     
play_button = Button(560, 400, play_image, 1)
exit_button = Button(560, 550, exit_image, 1)
        
#game loop
run = True
while run:
    
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    screen.blit(logo, ((SCREEN_WIDTH - logo.get_width()) // 2, 10))
    
    if menu_state == "main":
        # We call draw and check for the return value (the click action)
        if play_button.draw(screen):
            
            mixer.music.load('menu.mp3')
            mixer.music.play(-1)
            mixer.music.set_volume(0.05)
            mixer.music.set_pos(2.4)
            
            mode_selection = ModeSelection()
            selected_mode = mode_selection.run()
            
            if selected_mode:
                
                char_selection = CharacterSelection()
                selected_chars = char_selection.run()
                
                if selected_chars:
                    selected_char_p1, selected_char_p2 = selected_chars
                    
                    arena_selection = ArenaSelection()
                    selected_arena = arena_selection.run()
                    
                    if selected_arena:
                        
                        battle = BattleSystem(selected_char_p1, selected_char_p2, selected_arena, selected_mode)
                        battle.run()
            
            menu_state = "main"
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Game Menu")
        
        if exit_button.draw(screen):
            run = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()
    
pygame.quit()
sys.exit()