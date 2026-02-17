import pygame
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

bgColor = (111, 135, 135)
groundColor = (64, 82, 65)

font = pygame.font.SysFont("arial", 24, True)

# ---------------- PLATFORM ----------------
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(groundColor)
        self.rect = self.image.get_rect(topleft=(x, y))

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        try:
            img = pygame.image.load("man.png").convert_alpha()
            self.image = pygame.transform.scale(img, (80, 80))
        except:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.centerx = 200
        self.rect.bottom = 640

        self.vel_x = 0
        self.vel_y = 0
        self.accel = 0.8
        self.friction = 0.85
        self.gravity = 0.8
        self.jump_power = -12
        self.on_ground = False

        self.max_health = 100
        self.health = self.max_health
        self.invincible_timer = 0

        self.rolling = False
        self.roll_speed = 12
        self.roll_time = 0
        self.roll_cooldown = 0
        self.facing = 1

    def update(self, platforms):
        if self.health <= 0:
            return

        keys = pygame.key.get_pressed()

        if not self.rolling:
            if keys[pygame.K_a]:
                self.vel_x -= self.accel
                self.facing = -1
            if keys[pygame.K_d]:
                self.vel_x += self.accel
                self.facing = 1

        self.vel_x *= self.friction
        self.vel_y += self.gravity

        if keys[pygame.K_SPACE] and self.on_ground and not self.rolling:
            self.vel_y = self.jump_power

        if self.rolling:
            self.vel_x = self.facing * self.roll_speed
            self.roll_time -= 1
            if self.roll_time <= 0:
                self.rolling = False

        self.rect.x += int(self.vel_x)
        self.collide(platforms, "x")

        self.rect.y += int(self.vel_y)
        self.on_ground = False
        self.collide(platforms, "y")

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.roll_cooldown > 0:
            self.roll_cooldown -= 1

    def start_roll(self):
        if self.roll_cooldown == 0 and not self.rolling:
            self.rolling = True
            self.roll_time = 12
            self.roll_cooldown = 40
            self.invincible_timer = 15

    def collide(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):

                if direction == "x":
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    if self.vel_x < 0:
                        self.rect.left = platform.rect.right
                    self.vel_x = 0

                if direction == "y":
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                    if self.vel_y < 0:
                        self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def take_damage(self, amount):
        if self.invincible_timer == 0 and self.health > 0:
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.invincible_timer = 60

    def draw_health_bar(self, surface):
        width = 250
        height = 20
        x = 20
        y = 20

        pygame.draw.rect(surface, (60,60,60), (x, y, width, height))
        ratio = self.health / self.max_health
        pygame.draw.rect(surface, (30,200,30),
                         (x, y, width * ratio, height))
        pygame.draw.rect(surface, (255,255,255),
                         (x, y, width, height), 2)

        label = font.render("Player", True, (255,255,255))
        surface.blit(label, (x, y - 22))


# ---------------- BOSS ----------------
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.original_image = pygame.image.load("evil.png").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (220, 220))
        except:
            self.original_image = pygame.Surface((200, 200))
            self.original_image.fill((255, 0, 0))

        self.image = self.original_image
        self.rect = self.image.get_rect(midbottom=(1000, 640))

        self.max_health = 400
        self.health = self.max_health

        self.speed = 2
        self.angle = 0
        self.spin_duration = 0
        self.spin_cooldown = 120

    def update(self, player):
        if self.health <= 0:
            return

        if self.spin_duration == 0:
            if player.rect.centerx < self.rect.centerx - 5:
                self.rect.x -= self.speed
            elif player.rect.centerx > self.rect.centerx + 5:
                self.rect.x += self.speed

        if self.spin_cooldown <= 0 and random.randint(0, 180) == 1:
            self.spin_duration = 60
            self.spin_cooldown = 180

        if self.spin_duration > 0:
            self.angle += 25
            center = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=center)
            self.spin_duration -= 1

            if self.rect.colliderect(player.rect):
                player.take_damage(30)
        else:
            self.image = self.original_image

        if self.spin_cooldown > 0:
            self.spin_cooldown -= 1

        self.rect.bottom = 640

        if self.rect.colliderect(player.rect):
            player.take_damage(5)

    def draw_health_bar(self, surface):
        bar_width = 600
        bar_height = 25
        x = 340
        y = 30

        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, (200, 30, 30),
                         (x, y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(surface, (255,255,255),
                         (x, y, bar_width, bar_height), 2)

        label = font.render("Evil Man", True, (255,255,255))
        surface.blit(label, (x + bar_width//2 - label.get_width()//2, y - 30))


# ---------------- OBJECTS ----------------
player = Player()
boss = Boss()

platforms = pygame.sprite.Group()
platforms.add(Platform(0, 640, 1280, 80))

attack_cooldown = 0

# ---------------- GAME LOOP ----------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                player.start_roll()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and attack_cooldown == 0 and player.health > 0:
                attack_cooldown = 15
                attack_rect = player.rect.inflate(90, 60)
                if attack_rect.colliderect(boss.rect):
                    boss.health -= 25

    screen.fill(bgColor)
    pygame.display.set_caption("Jesus Is Coming")

    player.update(platforms)
    boss.update(player)

    if attack_cooldown > 0:
        attack_cooldown -= 1

    platforms.draw(screen)

    if player.health > 0 or player.invincible_timer % 10 < 5:
        screen.blit(player.image, player.rect)

    if boss.health > 0:
        screen.blit(boss.image, boss.rect)
        boss.draw_health_bar(screen)

    player.draw_health_bar(screen)

    # PLAYER DEATH MESSAGE
    if player.health <= 0:
        death_text = font.render("PLAYER DEFEATED", True, (255, 50, 50))
        screen.blit(death_text, (520, 360))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
