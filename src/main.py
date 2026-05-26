from array import array
import json
import math
from pathlib import Path
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
HIGH_SCORE_FILE = Path(__file__).resolve().parents[1] / "data" / "highscore.json"


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

    def draw(self, surface: pygame.Surface, phase: int) -> None:
        if not self.alive:
            return
        body = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (255, 120, 90), body, border_radius=8)
        pygame.draw.circle(surface, (50, 10, 10), (self.x + 12, self.y + 12), 3)
        pygame.draw.circle(surface, (50, 10, 10), (self.x + 32, self.y + 12), 3)
        leg_y = self.y + self.height - 2
        spread = 6 if phase == 0 else 10
        pygame.draw.line(surface, (255, 160, 130), (self.x + 10, leg_y), (self.x + 10 - spread, leg_y + 8), 2)
        pygame.draw.line(surface, (255, 160, 130), (self.x + 22, leg_y), (self.x + 22, leg_y + 8), 2)
        pygame.draw.line(surface, (255, 160, 130), (self.x + 34, leg_y), (self.x + 34 + spread, leg_y + 8), 2)


class SoundBank:
    def __init__(self) -> None:
        self.enabled = True
        try:
            self.shoot = make_tone(820, 70, 0.25)
            self.explode = make_tone(220, 130, 0.35)
            self.hit = make_tone(150, 190, 0.35)
            self.win = make_tone(960, 240, 0.3)
            self.lose = make_tone(110, 300, 0.35)
        except pygame.error:
            self.enabled = False

    def play(self, sound_name: str) -> None:
        if not self.enabled:
            return
        sound = getattr(self, sound_name, None)
        if sound:
            sound.play()


def make_tone(frequency: int, duration_ms: int, volume: float) -> pygame.mixer.Sound:
    sample_rate = 44100
    total = int(sample_rate * duration_ms / 1000)
    amp = int(32767 * volume)
    fade = max(1, int(total * 0.07))
    samples = array("h")

    for i in range(total):
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > total - fade:
            env = (total - i) / fade
        val = int(amp * env * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        samples.append(val)

    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_enemy_grid(rows: int = ENEMY_ROWS, cols: int = ENEMY_COLS) -> list[Enemy]:
    enemies: list[Enemy] = []
    margin_x = 90
    margin_y = 90
    spacing_x = 75
    spacing_y = 60
    for row in range(rows):
        for col in range(cols):
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


def draw_menu_scene(
    surface: pygame.Surface,
    tick: int,
    title_font: pygame.font.Font,
    mid_font: pygame.font.Font,
    tiny_font: pygame.font.Font,
    high_score: int,
) -> None:
    draw_starfield(surface, tick)
    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(6):
        pad = 60 + i * 25
        color = (20 + i * 16, 90 + i * 10, 180, 22)
        pygame.draw.ellipse(glow, color, (pad, 110, SCREEN_WIDTH - 2 * pad, 300), width=2)
    surface.blit(glow, (0, 0))

    panel = pygame.Surface((700, 280), pygame.SRCALPHA)
    panel.fill((10, 18, 40, 190))
    surface.blit(panel, (100, 190))

    title = title_font.render("SPACE INVADERS", True, (180, 245, 255))
    prompt = mid_font.render("Press ENTER to launch", True, (255, 235, 150))
    controls = tiny_font.render("A/D or LEFT/RIGHT move | SPACE shoots | P pauses", True, (230, 230, 255))
    score_line = tiny_font.render(f"BEST SCORE: {high_score}", True, (145, 255, 185))
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 250))
    surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 328))
    surface.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 370))
    surface.blit(score_line, (SCREEN_WIDTH // 2 - score_line.get_width() // 2, 408))


def load_high_score() -> int:
    try:
        data = json.loads(HIGH_SCORE_FILE.read_text(encoding="utf-8"))
        return int(data.get("high_score", 0))
    except (FileNotFoundError, OSError, json.JSONDecodeError, ValueError, TypeError):
        return 0


def save_high_score(score: int) -> None:
    try:
        HIGH_SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
        HIGH_SCORE_FILE.write_text(json.dumps({"high_score": score}, indent=2), encoding="utf-8")
    except OSError:
        return


def start_wave(wave: int) -> tuple[list[Enemy], int, float, float]:
    rows = min(ENEMY_ROWS + wave // 3, 6)
    speed = ENEMY_BASE_SPEED + min(4.0, (wave - 1) * 0.35)
    fire_chance = min(0.03 + (wave - 1) * 0.004, 0.09)
    return make_enemy_grid(rows=rows), 1, speed, fire_chance


def reset_game() -> tuple[Player, list[Enemy], list[Bullet], list[Bullet], int, float, int, int, float]:
    wave = 1
    enemies, enemy_direction, enemy_speed, enemy_fire_chance = start_wave(wave)
    return Player(), enemies, [], [], enemy_direction, enemy_speed, 0, wave, enemy_fire_chance


def run() -> None:
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.display.set_caption("Space Invaders")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("consolas", 42, bold=True)
    mid_font = pygame.font.SysFont("consolas", 28, bold=True)
    ui_font = pygame.font.SysFont("consolas", 22)
    tiny_font = pygame.font.SysFont("consolas", 18)
    sounds = SoundBank()
    high_score = load_high_score()

    player, enemies, player_bullets, enemy_bullets, enemy_direction, enemy_speed, shot_cooldown, wave, enemy_fire_chance = reset_game()

    score = 0
    lives = 3
    tick = 0
    state = "menu"
    wave_banner = 120

    while True:
        dt = clock.tick(FPS)
        tick += dt
        anim_phase = (tick // 260) % 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    player, enemies, player_bullets, enemy_bullets, enemy_direction, enemy_speed, shot_cooldown, wave, enemy_fire_chance = reset_game()
                    score = 0
                    lives = 3
                    state = "playing"
                    wave_banner = 120
                elif state == "playing" and event.key == pygame.K_p:
                    state = "paused"
                elif state == "paused" and event.key == pygame.K_p:
                    state = "playing"
                elif state == "paused" and event.key == pygame.K_ESCAPE:
                    state = "menu"
                elif state == "game_over" and event.key == pygame.K_r:
                    player, enemies, player_bullets, enemy_bullets, enemy_direction, enemy_speed, shot_cooldown, wave, enemy_fire_chance = reset_game()
                    score = 0
                    lives = 3
                    state = "playing"
                    wave_banner = 120
                elif state == "game_over" and event.key == pygame.K_ESCAPE:
                    state = "menu"

        keys = pygame.key.get_pressed()

        if state == "playing":
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
                sounds.play("shoot")
                shot_cooldown = 12

            living = [enemy for enemy in enemies if enemy.alive]
            if not living:
                sounds.play("win")
                wave += 1
                enemies, enemy_direction, enemy_speed, enemy_fire_chance = start_wave(wave)
                player_bullets.clear()
                enemy_bullets.clear()
                shot_cooldown = 15
                wave_banner = 120
                living = [enemy for enemy in enemies if enemy.alive]

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
                        state = "game_over"
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                        sounds.play("lose")

            if living and random.random() < enemy_fire_chance:
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
                        sounds.play("explode")
                        if bullet in player_bullets:
                            player_bullets.remove(bullet)
                        break

            for bullet in list(enemy_bullets):
                if bullet.rect.colliderect(player.rect):
                    enemy_bullets.remove(bullet)
                    lives -= 1
                    sounds.play("hit")
                    if lives <= 0:
                        state = "game_over"
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                        sounds.play("lose")

            if wave_banner > 0:
                wave_banner -= 1

        if state == "menu":
            draw_menu_scene(screen, tick, title_font, mid_font, tiny_font, high_score)
        else:
            draw_starfield(screen, tick)
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen, int(anim_phase))
            for bullet in player_bullets + enemy_bullets:
                bullet.draw(screen)

            score_text = ui_font.render(f"SCORE: {score}", True, (230, 230, 255))
            lives_text = ui_font.render(f"LIVES: {lives}", True, (230, 230, 255))
            wave_text = ui_font.render(f"WAVE: {wave}", True, (255, 230, 140))
            best_text = tiny_font.render(f"BEST: {high_score}", True, (145, 255, 185))
            screen.blit(score_text, (24, 20))
            screen.blit(lives_text, (SCREEN_WIDTH - 150, 20))
            screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, 20))
            screen.blit(best_text, (SCREEN_WIDTH // 2 - best_text.get_width() // 2, 50))

            if wave_banner > 0 and state == "playing":
                banner = mid_font.render(f"WAVE {wave}", True, (180, 240, 255))
                screen.blit(banner, (SCREEN_WIDTH // 2 - banner.get_width() // 2, 95))

        if state == "paused":
            paused_text = mid_font.render("PAUSED", True, (255, 230, 120))
            hint_text = ui_font.render("Press P to continue or ESC for menu", True, (240, 240, 240))
            screen.blit(paused_text, (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        if state == "game_over":
            status_text = mid_font.render("GAME OVER", True, (255, 120, 120))
            hint_text = ui_font.render("Press R to restart or ESC for menu", True, (240, 240, 240))
            wave_text = tiny_font.render(f"Waves survived: {wave}", True, (230, 230, 255))
            score_text = tiny_font.render(f"Best score: {high_score}", True, (145, 255, 185))
            screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT // 2 + 8))
            screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2 + 38))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 64))

        pygame.display.flip()


if __name__ == "__main__":
    run()
