import pygame as pg
import random
import math

pg.init()

FPS = 60
WIDTH, HEIGHT = 1900, 1000
speed = 4

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 200, 200)
RED = (255, 80, 80)
DARK = (20, 20, 30)
CARD = (40, 40, 60)

pg.display.set_caption("Boundary of Existence")
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
font = pg.font.SysFont(None, 36)


class Player: # класс игрока, игрок может двигаться, стрелять, собирать камни
    def __init__(self):
        img = pg.image.load('images/player.png').convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 8, img.get_height() // 8))
        self.rect = self.img.get_rect(center=(WIDTH // 4, HEIGHT // 1.2))
        self.mask = pg.mask.from_surface(self.img)

    def move(self, dx=0, dy=0): # движение
        new = self.rect.move(dx * speed, dy * speed)
        if 0 < new.left and new.right < WIDTH: self.rect.x = new.x
        if 0 < new.top and new.bottom < HEIGHT: self.rect.y = new.y

    def draw(self, screen): # отрисовка
        screen.blit(self.img, self.rect)


class Gem: # класс камней, их можно собирать и продавать
    def __init__(self):
        img = pg.image.load("images/diamond.png").convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 9, img.get_height() // 9))
        x = random.randint(WIDTH // 2 + 50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        self.rect = self.img.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.img)

    def draw(self, screen):
        screen.blit(self.img, self.rect) # отрисовка


class Enemy: # класс врагов, они появляются в случайных местах опасной зоны
    def __init__(self):
        img = pg.image.load('images/enemy.png').convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 9, img.get_height() // 9))
        x = random.randint(WIDTH // 2 + 50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        self.rect = self.img.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.img)

        self.speed = 2
        self.damage = 25
        self.cd = 0

    def update(self, player): # функция позволяет врагам бегать за игроком
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 1)
        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

        if self.rect.centerx < WIDTH // 2:
            self.rect.centerx = WIDTH // 2 + 5

        if self.cd > 0: self.cd -= 1

    def attack(self, player): # позволяет врагам атаковать игрока
        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.mask.overlap(player.mask, offset) and self.cd == 0:
            self.cd = 60
            return self.damage
        return 0

    def draw(self, screen): # отрисовка
        screen.blit(self.img, self.rect)


class Weapon: # оружие, 4 вида с разной ценой, уроном и временем
    def __init__(self, name, dmg, cd, spd, price):
        self.name = name
        self.damage = dmg
        self.cooldown = cd
        self.speed = spd
        self.price = price


class Bullet: # пуля
    def __init__(self, x, y, tx, ty, bul_speed, damage):
        self.img = pg.Surface((6, 6), pg.SRCALPHA)
        pg.draw.circle(self.img, (255, 220, 50), (3, 3), 3)
        self.rect = self.img.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.img)

        dx, dy = tx - x, ty - y
        dist = max(math.hypot(dx, dy), 1)
        self.vx = bul_speed * dx / dist
        self.vy = bul_speed * dy / dist
        self.damage = damage

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, screen): # отрисовка
        screen.blit(self.img, self.rect)


class Shop: # магазин, можно продать камни, купить оружие, восстановить здоровье, улучшить мешок
    def __init__(self):
        img = pg.image.load('images/shop.png').convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 4, img.get_height() // 4))
        self.rect = self.img.get_rect(center=(WIDTH // 6, HEIGHT // 6))

    def draw(self, screen): # отрисовка
        screen.blit(self.img, self.rect)


class Border: # граница, нужна для перехода между зонами, а также через нее не могут пройти враги
    def __init__(self):
        img = pg.image.load('images/border.png').convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 2, int(img.get_height() * 1.3)))
        self.rect = self.img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def draw(self, screen):
        screen.blit(self.img, self.rect) # отрисовка


def mask_collide(a, b):
    offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
    return a.mask.overlap(b.mask, offset)


background = pg.image.load('images/test_backgr.png')
background = pg.transform.scale(background, (WIDTH, HEIGHT))

player = Player()
shop = Shop()
border = Border()

weapons = [
    Weapon("Пистолет", 10, 20, 8, 0),
    Weapon("Ружье", 20, 10, 10, 50),
    Weapon("Дробовик", 15, 40, 7, 80),
    Weapon("Винтовка", 50, 80, 15, 120),
]
current_weapon = weapons[0]

pause_sound = pg.mixer.Sound('sounds/pause_sound.wav')
pistol_sound = pg.mixer.Sound('sounds/pistol_shot.wav')
grab_sound = pg.mixer.Sound('sounds/grab_sound.wav')

bullets = []
gems = []
enemies = []

spawn_t = 0
enemy_t = 0
shoot_cd = 0

inventory = 0
inventory_limit = 5
money = 0
hp = 100
max_hp = 100

zone = "safe"
shop_open = False
tutorial = True
paused = False

running = True
while running:
    clock.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:

            if tutorial and event.key == pg.K_SPACE:
                tutorial = False

            elif event.key == pg.K_ESCAPE and not tutorial:
                paused = not paused
                pause_sound.play()

            if not tutorial and not paused:

                if event.key == pg.K_e:
                    if player.rect.colliderect(border.rect):
                        if zone == "safe":
                            zone = "danger"
                            player.rect.center = (WIDTH * 0.75, HEIGHT / 1.2)
                        else:
                            zone = "safe"
                            player.rect.center = (WIDTH * 0.25, HEIGHT / 1.2)

                    elif player.rect.colliderect(shop.rect):
                        shop_open = not shop_open

                if event.key == pg.K_r:
                    grab_sound.play()
                    for g in gems[:]:
                        if mask_collide(player, g) and inventory < inventory_limit:
                            gems.remove(g)
                            inventory += 1

                if shop_open and event.key == pg.K_SPACE:
                    money += inventory * 10
                    inventory = 0

                if shop_open and event.key == pg.K_h and money >= 30:
                    hp = min(max_hp, hp + 50)
                    money -= 30

                if shop_open and event.key == pg.K_f and money >= 50:
                    inventory_limit += 5
                    money -= 50

                for i, w in enumerate(weapons):
                    if event.key == pg.K_1 + i and money >= w.price:
                        current_weapon = w
                        money -= w.price

    if not tutorial and not paused:

        if not shop_open:
            k = pg.key.get_pressed()
            if k[pg.K_d]: player.move(1)
            if k[pg.K_a]: player.move(-1)
            if k[pg.K_w]: player.move(0, -1)
            if k[pg.K_s]: player.move(0, 1)

        if zone == "safe" and player.rect.centerx > WIDTH // 2:
            player.rect.centerx = WIDTH // 2 - 5
        if zone == "danger" and player.rect.centerx < WIDTH // 2:
            player.rect.centerx = WIDTH // 2 + 5

        if zone == "danger":
            spawn_t += 1
            enemy_t += 1

            if spawn_t > 230:
                gems.append(Gem())
                spawn_t = 0

            if enemy_t > 230:
                enemies.append(Enemy())
                enemy_t = 0

        for en in enemies:
            en.update(player)
            hp -= en.attack(player)

        if shoot_cd > 0:
            shoot_cd -= 1

        m = pg.mouse.get_pressed()
        if m[0] and shoot_cd == 0 and not shop_open:
            mx, my = pg.mouse.get_pos()
            pistol_sound.play()

            if current_weapon.name == "Дробовик":
                for a in [-0.2, 0, 0.2]:
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery,
                                          mx + a * 100, my + a * 100,
                                          current_weapon.speed, current_weapon.damage))
            else:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery,
                                      mx, my,
                                      current_weapon.speed, current_weapon.damage))

            shoot_cd = current_weapon.cooldown

        for b in bullets[:]:
            b.update()

            for en in enemies[:]:
                if mask_collide(b, en):
                    enemies.remove(en)
                    bullets.remove(b)
                    break

            if not screen.get_rect().colliderect(b.rect):
                bullets.remove(b)

    screen.blit(background, (0, 0))

    if zone == "danger":
        s = pg.Surface((WIDTH, HEIGHT))
        s.set_alpha(120)
        s.fill((60, 0, 80))
        screen.blit(s, (0, 0))

    border.draw(screen)
    shop.draw(screen)

    for g in gems: g.draw(screen)
    for en in enemies: en.draw(screen)
    for b in bullets: b.draw(screen)

    player.draw(screen)

    if not tutorial:
        screen.blit(font.render(f"Здоровье: {hp}", True, RED), (20, 20))
        screen.blit(font.render(f"$: {money}", True, GREEN), (20, 60))
        screen.blit(font.render(f"Камни: {inventory}/{inventory_limit}", True, BLUE), (20, 100))
        screen.blit(font.render(f"Оружие: {current_weapon.name}", True, WHITE), (20, 140))

    if shop_open:
        panel = pg.Surface((900, 550))
        panel.fill(DARK)
        screen.blit(panel, (WIDTH // 2 - 450, HEIGHT // 2 - 275))

        screen.blit(font.render("Магазин", True, WHITE), (WIDTH // 2 - 40, HEIGHT // 2 - 250))

        for i, w in enumerate(weapons):
            x = WIDTH // 2 - 400 + i * 200
            y = HEIGHT // 2 - 150

            r = pg.Rect(x, y, 180, 220)
            pg.draw.rect(screen, CARD, r)
            pg.draw.rect(screen, WHITE, r, 2)

            screen.blit(font.render(w.name, True, WHITE), (x + 20, y + 10))
            screen.blit(font.render(f"Урон {w.damage}", True, WHITE), (x + 20, y + 50))
            screen.blit(font.render(f"${w.price}", True, GREEN), (x + 40, y + 170))
            screen.blit(font.render(f"[{i + 1}]", True, WHITE), (x + 70, y + 190))

        screen.blit(font.render("SPACE - продать камни", True, WHITE),
                    (WIDTH // 2 - 200, HEIGHT // 2 + 120))
        screen.blit(font.render("H - восстановить здоровье (30$)", True, WHITE),
                    (WIDTH // 2 - 200, HEIGHT // 2 + 160))
        screen.blit(font.render("F - улучшить мешок (50$)", True, WHITE),
                    (WIDTH // 2 - 200, HEIGHT // 2 + 200))

    if tutorial:
        s = pg.Surface((WIDTH, HEIGHT))
        s.set_alpha(220)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        txt = ["WASD - движение", "E - взаимодействие", "R - взять", "M1 - стрелять", "ESC - пауза",
               "SPACE - старт игры"]
        for i, t in enumerate(txt):
            screen.blit(font.render(t, True, WHITE), (WIDTH // 2 - 200, 300 + i * 50))

    if paused:
        s = pg.Surface((WIDTH, HEIGHT))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        screen.blit(font.render("Пауза", True, WHITE), (WIDTH // 2 - 80, HEIGHT // 2 - 40))
        screen.blit(font.render("ESC - продолжить", True, WHITE), (WIDTH // 2 - 150, HEIGHT // 2 + 20))

    if hp <= 0:
        screen.fill((0, 0, 0))
        screen.blit(font.render("Игра окончена", True, RED), (WIDTH // 2 - 100, HEIGHT // 2))
        pg.display.update()
        pg.time.delay(3000)
        running = False

    pg.display.update()

pg.quit()
