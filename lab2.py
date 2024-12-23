import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
SPACESHIP_SPEED = 5
ASTEROID_SPEED = 2
CRYSTAL_RADIUS = 25
ASTEROID_SIZE = 50
MAX_ASTEROID_SIZE = 100
ASTEROID_GROWTH_RATE = 0.5
ENERGY_CRYSTAL_MIN_COUNT = 8
ENERGY_CRYSTAL_MAX_COUNT = 15
DIFFICULTY_INCREASE_STEP = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Scavenger")

spaceship_img = pygame.image.load("assets/spaceship.png")
spaceship_img = pygame.transform.scale(spaceship_img, (40, 40))
spaceship_rect = spaceship_img.get_rect()
energy_crystal_img = pygame.image.load("assets/energy_crystal.png")
asteroid_img = pygame.image.load("assets/asteroid.png")
crash_sound = pygame.mixer.Sound("assets/clash_sound.wav")


def load_background_music():
    try:
        pygame.mixer.music.load("assets/background_music.wav")
    except pygame.error:
        return False
    return True


font = pygame.font.SysFont('Arial', 30)


class Asteroid:
    def __init__(self, size):
        self.size = size
        self.x = random.randint(WIDTH // 2, WIDTH - self.size)
        self.y = random.randint(0, HEIGHT // 2)
        self.speed_x = ASTEROID_SPEED
        self.speed_y = ASTEROID_SPEED

    def move(self):
        self.x -= self.speed_x
        self.y += self.speed_y

    def draw(self):
        screen.blit(pygame.transform.scale(asteroid_img, (self.size, self.size)), (self.x, self.y))


class EnergyCrystal:
    def __init__(self):
        self.x = random.randint(0, WIDTH - CRYSTAL_RADIUS)
        self.y = random.randint(0, HEIGHT - CRYSTAL_RADIUS)

    def draw(self):
        screen.blit(pygame.transform.scale(energy_crystal_img, (CRYSTAL_RADIUS, CRYSTAL_RADIUS)), (self.x, self.y))


def reset_game():
    global spaceship_rect, asteroid_list, crystal_list, spaceship_speed, collected_crystals, crash_sound_played, initial_crystal_count, start_time
    spaceship_rect = spaceship_img.get_rect()
    spaceship_rect.center = (WIDTH // 2, HEIGHT - 50)
    asteroid_list = [Asteroid(ASTEROID_SIZE) for _ in range(5)]
    initial_crystal_count = random.randint(ENERGY_CRYSTAL_MIN_COUNT, ENERGY_CRYSTAL_MAX_COUNT)
    crystal_list = [EnergyCrystal() for _ in range(initial_crystal_count)]
    spaceship_speed = SPACESHIP_SPEED
    collected_crystals = 0
    crash_sound_played = False
    start_time = time.time()

    if load_background_music():
        pygame.mixer.music.play(-1)
    else:
        print("Background music failed to load. The game will continue without it.")


def game_loop():
    global spaceship_rect, asteroid_list, crystal_list, spaceship_speed, collected_crystals, crash_sound_played, initial_crystal_count, start_time

    game_over = False
    game_won = False

    while True:
        screen.fill(BLACK)
        pygame.time.Clock().tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over or game_won:
                    reset_game()
                    game_over = False
                    game_won = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            spaceship_rect.x -= spaceship_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            spaceship_rect.x += spaceship_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            spaceship_rect.y -= spaceship_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            spaceship_rect.y += spaceship_speed

        spaceship_rect.x = max(0, min(spaceship_rect.x, WIDTH - spaceship_rect.width))
        spaceship_rect.y = max(0, min(spaceship_rect.y, HEIGHT - spaceship_rect.height))

        screen.blit(spaceship_img, spaceship_rect)

        for asteroid in asteroid_list:
            asteroid.move()
            asteroid.draw()
            if asteroid.y > HEIGHT or asteroid.x < 0:
                asteroid.y = -asteroid.size
                asteroid.x = random.randint(WIDTH // 2, round(WIDTH - asteroid.size))

            asteroid_collision_rect = pygame.Rect(asteroid.x + 5, asteroid.y + 5, asteroid.size - 10,
                                                  asteroid.size - 10)

            if not game_won and spaceship_rect.colliderect(asteroid_collision_rect):
                if not crash_sound_played:
                    crash_sound.play()
                    crash_sound_played = True
                game_over = True
                pygame.mixer.music.stop()

        for crystal in crystal_list[:]:
            crystal.draw()
            if spaceship_rect.colliderect(pygame.Rect(crystal.x, crystal.y, CRYSTAL_RADIUS, CRYSTAL_RADIUS)):
                crystal_list.remove(crystal)
                collected_crystals += 1

        if collected_crystals == initial_crystal_count:
            game_won = True
            pygame.mixer.music.stop()

        elapsed_time = int(time.time() - start_time)

        if elapsed_time % DIFFICULTY_INCREASE_STEP == 0 and elapsed_time > 0:
            for asteroid in asteroid_list:
                if asteroid.size < MAX_ASTEROID_SIZE:
                    asteroid.size += ASTEROID_GROWTH_RATE

        if elapsed_time % DIFFICULTY_INCREASE_STEP == 0 and elapsed_time > 0:
            spaceship_speed += 0.025

        if game_over:
            screen.fill(RED)
            message = font.render("Game Over! Click to Restart.", True, WHITE)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2))
        elif game_won:
            screen.fill(BLUE)
            message = font.render("You Won! Click to Restart.", True, WHITE)
            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2))

        pygame.display.update()


reset_game()
game_loop()
