import pygame
import threading
import random
import sys

pygame.init()

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
NUM_OBJECTS = 5
WINNING_COUNT = 15
TIME_LIMIT = 20000

cooperative_threads = []
barriers = [threading.Barrier(2) for _ in range(3)]
notifications = [threading.Event() for _ in range(3)]
semaphores = [threading.Semaphore(1) for _ in range(3)]
events = [threading.Event() for _ in range(3)]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5

    def update(self, keys):
        prev_rect = self.rect.copy()

        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if not (0 <= self.rect.x <= SCREEN_WIDTH - PLAYER_SIZE) or not (0 <= self.rect.y <= SCREEN_HEIGHT - PLAYER_SIZE):
            self.rect = prev_rect

class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

def draw_screen(time_left):
    screen.fill(BLACK)
    all_sprites.draw(screen)
    font = pygame.font.Font(None, 36)
    text = font.render(f"Collected Objects: {collected_objects}", True, WHITE)
    screen.blit(text, (10, 10))
    text = font.render(f"Time Left: {time_left} seconds", True, WHITE)
    screen.blit(text, (10, 50))
    pygame.display.flip()

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

def generate_objects():
    global objects
    objects = pygame.sprite.Group()
    for _ in range(NUM_OBJECTS):
        obj = GameObject()
        while not screen.get_rect().colliderect(obj.rect):
            obj.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        objects.add(obj)

def cooperative_thread_function(thread_id, barrier, notification, semaphore, event):
    print(f"Cooperative thread {thread_id} started.")
    barrier.wait()
    print(f"Cooperative thread {thread_id} passed the barrier.")
    notification.set()
    semaphore.acquire()
    print(f"Cooperative thread {thread_id} acquired the semaphore.")
    pygame.time.delay(1000)
    semaphore.release()
    print(f"Cooperative thread {thread_id} released the semaphore.")
    event.set()
    print(f"Cooperative thread {thread_id} finished.")

def main():
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Concurrent Game")

    global player
    player = Player()

    global all_sprites
    all_sprites = pygame.sprite.Group()
    generate_objects()
    all_sprites.add(player, objects)

    clock = pygame.time.Clock()

    global collected_objects
    collected_objects = 0

    start_time = pygame.time.get_ticks()

    for i in range(2):
        thread = threading.Thread(target=cooperative_thread_function, args=(i, barriers[i], notifications[i], semaphores[i], events[i]))
        thread.start()
        cooperative_threads.append(thread)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        player.update(keys)

        check_collision()

        elapsed_time = pygame.time.get_ticks() - start_time
        time_left = max((TIME_LIMIT - elapsed_time) // 1000, 0)

        draw_screen(time_left)

        if collected_objects >= WINNING_COUNT or elapsed_time >= TIME_LIMIT:
            if collected_objects >= WINNING_COUNT:
                message = "You Win!"
            else:
                message = "Time's Up!"
            font = pygame.font.Font(None, 48)
            text = font.render(message, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
            pygame.display.flip()
            pygame.time.delay(2000)
            running = False

        clock.tick(60)

    for thread in cooperative_threads:
        thread.join()

    pygame.quit()

if __name__ == "__main__":
    main()
