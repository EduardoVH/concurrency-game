import pygame
import threading
import random
import sys

# Pygame initialization
pygame.init()

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
NUM_OBJECTS = 5
WINNING_COUNT = 15
TIME_LIMIT = 25000  # 25 seconds in milliseconds

# Define global variables for concurrent elements
cooperative_threads = []
barriers = [threading.Barrier(2) for _ in range(3)]
notifications = [threading.Event() for _ in range(3)]
semaphores = [threading.Semaphore(1) for _ in range(3)]
events = [threading.Event() for _ in range(3)]

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5

    def update(self, keys):
        # Save player's previous position
        prev_rect = self.rect.copy()

        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Check if the player goes off-screen
        if not (0 <= self.rect.x <= SCREEN_WIDTH - PLAYER_SIZE) or not (0 <= self.rect.y <= SCREEN_HEIGHT - PLAYER_SIZE):
            # Restore player's previous position
            self.rect = prev_rect

# Game Object class
class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

# Function to draw the screen
def draw_screen(time_left):
    screen.fill(WHITE)
    all_sprites.draw(screen)
    font = pygame.font.Font(None, 36)
    text = font.render(f"Collected Objects: {collected_objects}", True, BLUE)
    screen.blit(text, (10, 10))
    text = font.render(f"Time Left: {time_left} seconds", True, BLUE)
    screen.blit(text, (10, 50))
    pygame.display.flip()

# Function to handle collision between player and objects
def check_collision():
    global collected_objects
    collisions = pygame.sprite.spritecollide(player, objects, True)
    for obj in collisions:
        collected_objects += 1
        obj.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        new_obj = GameObject()
        while not screen.get_rect().colliderect(new_obj.rect):
            new_obj.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        objects.add(new_obj)
        all_sprites.add(new_obj)

# Function to generate objects within the screen
def generate_objects():
    global objects
    objects = pygame.sprite.Group()
    for _ in range(NUM_OBJECTS):
        obj = GameObject()
        # Make sure objects appear within the screen
        while not screen.get_rect().colliderect(obj.rect):
            obj.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        objects.add(obj)

# Function to simulate cooperative threads
def cooperative_thread_function(thread_id, barrier, notification, semaphore, event):
    print(f"Cooperative thread {thread_id} started.")
    # Wait at barrier
    barrier.wait()
    print(f"Cooperative thread {thread_id} passed the barrier.")
    # Set notification
    notification.set()
    # Wait for semaphore
    semaphore.acquire()
    print(f"Cooperative thread {thread_id} acquired the semaphore.")
    # Release semaphore after some time
    pygame.time.delay(1000)
    semaphore.release()
    print(f"Cooperative thread {thread_id} released the semaphore.")
    # Set event
    event.set()
    print(f"Cooperative thread {thread_id} finished.")

# Main function
def main():
    # Create the screen
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Concurrent Game")

    # Create the player
    global player
    player = Player()

    # Create the objects
    global all_sprites
    all_sprites = pygame.sprite.Group()
    generate_objects()
    all_sprites.add(player, objects)

    clock = pygame.time.Clock()

    # Counter for collected objects
    global collected_objects
    collected_objects = 0

    # Start the timer
    start_time = pygame.time.get_ticks()

    # Start cooperative threads
    for i in range(2):
        thread = threading.Thread(target=cooperative_thread_function, args=(i, barriers[i], notifications[i], semaphores[i], events[i]))
        thread.start()
        cooperative_threads.append(thread)

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get pressed keys
        keys = pygame.key.get_pressed()

        # Update player's position
        player.update(keys)

        # Check collision between player and objects
        check_collision()

        # Calculate time left
        elapsed_time = pygame.time.get_ticks() - start_time
        time_left = max((TIME_LIMIT - elapsed_time) // 1000, 0)

        # Draw the screen
        draw_screen(time_left)

        # Check if winning condition or time limit reached
        if collected_objects >= WINNING_COUNT or elapsed_time >= TIME_LIMIT:
            if collected_objects >= WINNING_COUNT:
                message = "You Win!"
            else:
                message = "Time's Up!"
            font = pygame.font.Font(None, 48)
            text = font.render(message, True, BLUE)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
            pygame.display.flip()
            pygame.time.delay(2000)
            running = False

        clock.tick(60)

    # Join cooperative threads
    for thread in cooperative_threads:
        thread.join()

    pygame.quit()

if __name__ == "__main__":
    main()
