import pygame
import sys

# Inisialisasi Pygame
pygame.init()

# Konstanta
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
ANIMATION_SPEED = 10  # Frame berganti setiap 10 frame game

# Warna
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)

# Setup layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Animasi Spritesheet")
clock = pygame.time.Clock()

# Load spritesheet
try:
    spritesheet = pygame.image.load('assets\Vampire3\Idle.png').convert_alpha()
except:
    print("Error: File 'spritesheet.png' tidak ditemukan!")
    print("Pastikan file spritesheet ada di folder yang sama dengan script ini.")
    pygame.quit()
    sys.exit()

# Informasi sprite
SPRITE_WIDTH = spritesheet.get_width() // 5  # 6 frame dalam spritesheet
SPRITE_HEIGHT = spritesheet.get_height()
NUM_FRAMES = 5

# Ekstrak setiap frame dari spritesheet
frames = []
for i in range(NUM_FRAMES):
    frame = spritesheet.subsurface(pygame.Rect(
        i * SPRITE_WIDTH, 
        0, 
        SPRITE_WIDTH, 
        SPRITE_HEIGHT
    ))
    # Scale up 3x agar lebih besar
    frame = pygame.transform.scale(frame, 
                                   (SPRITE_WIDTH * 3, SPRITE_HEIGHT * 3))
    frames.append(frame)

# Variabel animasi
current_frame = 0
frame_counter = 0

# Posisi sprite
sprite_x = SCREEN_WIDTH // 2 - (SPRITE_WIDTH * 3) // 2
sprite_y = SCREEN_HEIGHT // 2 - (SPRITE_HEIGHT * 3) // 2

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Update animasi
    frame_counter += 1
    if frame_counter >= ANIMATION_SPEED:
        frame_counter = 0
        current_frame = (current_frame + 1) % NUM_FRAMES
    
    # Render
    screen.fill(SKY_BLUE)
    
    # Gambar shadow sederhana
    shadow_surf = pygame.Surface((SPRITE_WIDTH * 3, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), shadow_surf.get_rect())
    screen.blit(shadow_surf, (sprite_x, sprite_y + SPRITE_HEIGHT * 3 - 10))
    
    # Gambar sprite
    screen.blit(frames[current_frame], (sprite_x, sprite_y))
    
    # Informasi
    font = pygame.font.Font(None, 36)
    text = font.render(f"Frame: {current_frame + 1}/{NUM_FRAMES}", True, (50, 50, 50))
    screen.blit(text, (10, 10))
    
    info_font = pygame.font.Font(None, 24)
    info_text = info_font.render("ESC untuk keluar", True, (50, 50, 50))
    screen.blit(info_text, (10, SCREEN_HEIGHT - 30))
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Cleanup
pygame.quit()
sys.exit()