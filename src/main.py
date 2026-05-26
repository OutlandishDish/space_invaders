import math
import random
import sys

import pygame


SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

PLAYER_SPEED = 7
BULLET_SPEED = 11
ENEMY_BASE_SPEED = 2
ENEMY_DROP = 34
ENEMY_ROWS = 4
ENEMY_COLS = 9


class Player:
    def __init__(self) -> None:
        self.width = 60
        self.height = 26
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 80
        self.speed = PLAYER_SPEED

    def move(self, direction: int) -> None:
        self.x += direction * self.speed
        self.x = max(20, min(SCREEN_WIDTH - self.width - 20, self.x))

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (100, 230, 120), self.rect, border_radius=6)
        turret = pygame.Rect(self.x + self.width // 2 - 7, self.y - 12, 14, 16)
        pygame.draw.rect(surface, (150, 255, 180), turret, border_radius=5)


class Bullet:
    def __init__(self, x: int, y: int, speed: int, from_player: bool) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.from_player = from_player
        self.radius = 4

    def update(self) -> None:
        self.y += self.speed

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface: pygame.Surface) -> None:
        color = (255, 250, 180) if self.from_player else (255, 80, 80)
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)


class Enemy:
    def __init__(self, x: int, y: int) -> None:
        self.width = 44
        self.height = 28
        self.x = x
        self.y = y
        self.alive = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        body = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (255, 120, 90), body, border_radius=8)
        pygame.draw.circle(surface, (50, 10, 10), (self.x + 12, self.y + 12), 3)
        pygame.draw.circle(surface, (50, 10, 10), (self.x + 32, self.y + 12), 3)


def make_enemy_grid() -> list[Enemy]:
    enemies: list[Enemy] = []
    margin_x = 90
    margin_y = 90
    spacing_x = 75
    spacing_y = 60
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemies.append(Enemy(margin_x + col * spacing_x, margin_y + row * spacing_y))
    return enemies


def draw_starfield(surface: pygame.Surface, tick: int) -> None:
    surface.fill((10, 14, 32))
    for i in range(85):
        x = (i * 97) % SCREEN_WIDTH
        y = (i * 53 + tick // 2) % SCREEN_HEIGHT
        b = 120 + (i * 13) % 120
        surface.set_at((x, y), (b, b, b))
    for i in range(10):
        cx = (i * 131 + tick // 3) % SCREEN_WIDTH
        cy = 80 + int(20 * math.sin((tick + i * 40) / 45))
        pygame.draw.circle(surface, (60, 80, 170), (cx, cy), 14, width=2)


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Space Invaders")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("consolas", 28, bold=True)
    ui_font = pygame.font.SysFont("consolas", 22)

    player = Player()
    enemies = make_enemy_grid()
    player_bullets: list[Bullet] = []
    enemy_bullets: list[Bullet] = []

    enemy_direction = 1
    enemy_speed = ENEMY_BASE_SPEED

    score = 0
    lives = 3
    tick = 0
    shot_cooldown = 0
    game_over = False
    victory = False

    while True:
        dt = clock.tick(FPS)
        tick += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_r:
                run()

        keys = pygame.key.get_pressed()

        if not game_over:
            direction = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                direction -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                direction += 1
            player.move(direction)

            if shot_cooldown > 0:
                shot_cooldown -= 1
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and shot_cooldown == 0:
                player_bullets.append(Bullet(player.x + player.width // 2, player.y - 8, -BULLET_SPEED, True))
                shot_cooldown = 12

            living = [enemy for enemy in enemies if enemy.alive]
            if not living:
                game_over = True
                victory = True

            boundary_hit = False
            for enemy in living:
                enemy.x += enemy_direction * enemy_speed
                if enemy.x <= 22 or enemy.x + enemy.width >= SCREEN_WIDTH - 22:
                    boundary_hit = True

            if boundary_hit:
                enemy_direction *= -1
                for enemy in living:
                    enemy.y += ENEMY_DROP
                    if enemy.y + enemy.height >= player.y:
                        game_over = True
                        victory = False

            if living and random.random() < 0.03:
                shooter = random.choice(living)
                enemy_bullets.append(Bullet(shooter.x + shooter.width // 2, shooter.y + shooter.height + 4, 7, False))

            for bullet in player_bullets:
                bullet.update()
            for bullet in enemy_bullets:
                bullet.update()

            player_bullets = [b for b in player_bullets if b.y > -20]
            enemy_bullets = [b for b in enemy_bullets if b.y < SCREEN_HEIGHT + 20]

            for bullet in list(player_bullets):
                for enemy in living:
                    if enemy.alive and bullet.rect.colliderect(enemy.rect):
                        enemy.alive = False
                        score += 100
                        if bullet in player_bullets:
                            player_bullets.remove(bullet)
                        break

            for bullet in list(enemy_bullets):
                if bullet.rect.colliderect(player.rect):
                    enemy_bullets.remove(bullet)
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                        victory = False

        draw_starfield(screen, tick)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in player_bullets + enemy_bullets:
            bullet.draw(screen)

        score_text = ui_font.render(f"SCORE: {score}", True, (230, 230, 255))
        lives_text = ui_font.render(f"LIVES: {lives}", True, (230, 230, 255))
        screen.blit(score_text, (24, 20))
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 20))

        if game_over:
            status = "YOU WIN" if victory else "GAME OVER"
            status_color = (120, 255, 160) if victory else (255, 120, 120)
            status_text = title_font.render(status, True, status_color)
            hint_text = ui_font.render("Press R to restart", True, (240, 240, 240))
            screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT // 2 + 8))

        pygame.display.flip()


if __name__ == "__main__":
    run()
