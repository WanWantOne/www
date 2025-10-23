import pygame
import sys
import random
import math

# Inisialisasi Pygame
pygame.init()

# Konstanta
WIDTH, HEIGHT = 800, 600
FPS = 60
ROAD_WIDTH = 400
CAR_WIDTH, CAR_HEIGHT = 40, 70
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
SPEED = 5
DRIFT_FACTOR = 0.1
FRICTION = 0.95

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# Setup layar
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Mobil Drift")
clock = pygame.time.Clock()

# Kelas Mobil
class Car:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.speed = 0
        self.angle = 0  # Sudut dalam derajat
        self.velocity_x = 0
        self.velocity_y = 0
        self.drift = 0
        self.color = RED
    
    def draw(self, surface):
        # Membuat surface untuk mobil dengan rotasi
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, self.width, self.height))
        
        # Menambahkan detail pada mobil
        pygame.draw.rect(car_surface, BLACK, (5, 5, self.width-10, 15))  # Kaca depan
        pygame.draw.rect(car_surface, BLACK, (5, self.height-20, self.width-10, 15))  # Kaca belakang
        pygame.draw.rect(car_surface, YELLOW, (5, 20, 10, 10))  # Lampu kiri
        pygame.draw.rect(car_surface, YELLOW, (self.width-15, 20, 10, 10))  # Lampu kanan
        
        # Rotasi mobil
        rotated_car = pygame.transform.rotate(car_surface, self.angle)
        rotated_rect = rotated_car.get_rect(center=(self.x, self.y))
        
        # Menggambar mobil
        surface.blit(rotated_car, rotated_rect.topleft)
        
        # Menggambar efek drift (garis di belakang mobil)
        if abs(self.drift) > 0.1:
            drift_length = 50
            drift_angle = self.angle + 90  # Sudut tegak lurus dengan mobil
            drift_x = self.x + math.cos(math.radians(drift_angle)) * drift_length
            drift_y = self.y - math.sin(math.radians(drift_angle)) * drift_length
            pygame.draw.line(surface, WHITE, (self.x, self.y), (drift_x, drift_y), 3)
    
    def update(self, keys):
        # Kontrol mobil
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5
        if keys[pygame.K_UP]:
            self.speed += 0.2
        if keys[pygame.K_DOWN]:
            self.speed -= 0.2
        
        # Batasi kecepatan
        self.speed = max(-3, min(self.speed, 10))
        
        # Hitung drift
        if keys[pygame.K_SPACE] and abs(self.speed) > 1:
            self.drift = DRIFT_FACTOR * self.speed
        else:
            self.drift *= 0.9
        
        # Hitung kecepatan berdasarkan sudut dan drift
        rad_angle = math.radians(self.angle)
        self.velocity_x = math.sin(rad_angle) * self.speed
        self.velocity_y = math.cos(rad_angle) * self.speed
        
        # Terapkan drift
        drift_rad = math.radians(self.angle + 90)
        self.velocity_x += math.sin(drift_rad) * self.drift
        self.velocity_y += math.cos(drift_rad) * self.drift
        
        # Update posisi
        self.x += self.velocity_x
        self.y -= self.velocity_y  # Kurangi karena koordinat y meningkat ke bawah
        
        # Batasi mobil di dalam jalan
        road_left = (WIDTH - ROAD_WIDTH) // 2
        road_right = road_left + ROAD_WIDTH
        
        if self.x < road_left + self.width // 2:
            self.x = road_left + self.width // 2
            self.speed *= 0.5  # Kurangi kecepatan saat menabrak tepi
        elif self.x > road_right - self.width // 2:
            self.x = road_right - self.width // 2
            self.speed *= 0.5
        
        # Batasi mobil di dalam layar (vertikal)
        if self.y < self.height // 2:
            self.y = self.height // 2
        elif self.y > HEIGHT - self.height // 2:
            self.y = HEIGHT - self.height // 2
    
    def get_rect(self):
        # Mendapatkan persegi panjang yang mewakili mobil (untuk tabrakan)
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

# Kelas Rintangan
class Obstacle:
    def __init__(self):
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        road_left = (WIDTH - ROAD_WIDTH) // 2
        self.x = random.randint(road_left + self.width // 2, road_left + ROAD_WIDTH - self.width // 2)
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.color = BLUE
    
    def update(self):
        self.y += self.speed
        return self.y > HEIGHT
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

# Fungsi untuk menggambar jalan
def draw_road(surface):
    road_left = (WIDTH - ROAD_WIDTH) // 2
    road_right = road_left + ROAD_WIDTH
    
    # Gambar jalan
    pygame.draw.rect(surface, GRAY, (road_left, 0, ROAD_WIDTH, HEIGHT))
    
    # Gambar garis tengah jalan
    line_width = 10
    line_height = 30
    line_gap = 20
    for y in range(0, HEIGHT, line_height + line_gap):
        pygame.draw.rect(surface, YELLOW, (WIDTH // 2 - line_width // 2, y, line_width, line_height))
    
    # Gambar tepi jalan
    pygame.draw.rect(surface, WHITE, (road_left, 0, 5, HEIGHT))
    pygame.draw.rect(surface, WHITE, (road_right - 5, 0, 5, HEIGHT))

# Fungsi utama game
def main():
    car = Car()
    obstacles = []
    score = 0
    game_over = False
    obstacle_timer = 0
    font = pygame.font.SysFont(None, 36)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Restart game
                    car = Car()
                    obstacles = []
                    score = 0
                    game_over = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            car.update(keys)
            
            # Spawn rintangan
            obstacle_timer += 1
            if obstacle_timer >= 60:  # Spawn rintangan setiap 60 frame (1 detik)
                obstacles.append(Obstacle())
                obstacle_timer = 0
            
            # Update rintangan
            for obstacle in obstacles[:]:
                if obstacle.update():
                    obstacles.remove(obstacle)
                    score += 1
            
            # Deteksi tabrakan
            car_rect = car.get_rect()
            for obstacle in obstacles:
                if car_rect.colliderect(obstacle.get_rect()):
                    game_over = True
        
        # Menggambar
        screen.fill(BLACK)
        draw_road(screen)
        
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        car.draw(screen)
        
        # Menampilkan skor
        score_text = font.render(f"Skor: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER! Tekan R untuk restart", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 180, HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()