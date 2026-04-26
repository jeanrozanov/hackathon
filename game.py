import pygame as pg
import random
import math

pg.init()

FPS = 60
WIDTH, HEIGHT = 1900, 1000
speed = 4

pg.mixer.music.load('sounds/background_music.wav')
pg.mixer.music.play(-1)

pause_sound = pg.mixer.Sound('sounds/pause_sound.wav') # звук паузы
pistol_sound = pg.mixer.Sound('sounds/pistol_shot.wav') # звук выстрела
grab_sound = pg.mixer.Sound('sounds/grab_sound.wav') # звук взятия предмета

# основные цвета интерфейса
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


# игрок
class Player:
    def __init__(self):
        # загрузка анимации движения
        self.frames = []
        for i in range(6):
            img = pg.image.load(f'images/player_{i}.png').convert_alpha()
            img = pg.transform.scale(img, (img.get_width() * 1.3, img.get_height() * 1.3))
            self.frames.append(img)

        # спрайт игрока в бездействии
        idle = pg.image.load('images/player_idle.png').convert_alpha()
        self.idle_img = pg.transform.scale(idle, (idle.get_width() // 8, idle.get_height() // 8))

        self.frame_index = 0
        self.anim_speed = 0.2
        self.image = self.idle_img

        self.rect = self.image.get_rect(center=(WIDTH // 8, HEIGHT // 1.2))
        self.mask = pg.mask.from_surface(self.image)

        self.moving = False
        self.facing_right = True

    def move(self, dx=0, dy=0):
        # определяем движение и направление
        self.moving = dx != 0 or dy != 0

        if dx < 0:
            self.facing_right = False
        elif dx > 0:
            self.facing_right = True

        # движение с ограничением по экрану
        new = self.rect.move(dx * speed, dy * speed)
        if 0 < new.left and new.right < WIDTH:
            self.rect.x = new.x
        if 0 < new.top and new.bottom < HEIGHT:
            self.rect.y = new.y

    def update(self):
        # переключение кадров анимации
        if self.moving:
            self.frame_index += self.anim_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            img = self.frames[int(self.frame_index)]
        else:
            img = self.idle_img

        # отражение персонажа
        if not self.facing_right:
            img = pg.transform.flip(img, True, False)

        # сохраняем центр при смене изображения
        center = self.rect.center
        self.image = img
        self.rect = self.image.get_rect(center=center)

        self.mask = pg.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# камни
class Gem:
    def __init__(self):
        # спавн камней только в опасной зоне
        img = pg.image.load("images/diamond.png").convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 9, img.get_height() // 9))
        x = random.randint(WIDTH // 2 + 50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        self.rect = self.img.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.img)

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class Enemy:
    def __init__(self, chaos=False):
        # враги становятся быстрее и сильнее в режиме "без правил"
        img = pg.image.load('images/enemy.png').convert_alpha()
        self.img = pg.transform.flip(img, True, False)
        self.img = pg.transform.scale(self.img, (self.img.get_width() // 9, self.img.get_height() // 9))
        x = random.randint(WIDTH // 2 + 50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        self.rect = self.img.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.img)

        if chaos:
            self.speed = 3
            self.damage = 40
        else:
            self.speed = 2
            self.damage = 25

        self.cd = 0  # задержка между атаками

    def update(self, player, chaos=False):
        # движение к игроку
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 1)

        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

        # ограничение врагов в зоне
        if not chaos and self.rect.centerx < WIDTH // 2:
            self.rect.centerx = WIDTH // 2 + 5

        if self.cd > 0:
            self.cd -= 1

    def attack(self, player):
        # урон при пересечении масок
        offset = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.mask.overlap(player.mask, offset) and self.cd == 0:
            self.cd = 60
            return self.damage
        return 0

    def draw(self, screen):
        screen.blit(self.img, self.rect)


# оружие
class Weapon:
    def __init__(self, name, dmg, cd, spd, price):
        self.name = name
        self.damage = dmg
        self.cooldown = cd
        self.speed = spd
        self.price = price


class Bullet:
    def __init__(self, x, y, tx, ty, bul_speed, damage):
        # простая пуля круг
        self.img = pg.Surface((6, 6), pg.SRCALPHA)
        pg.draw.circle(self.img, (255, 220, 50), (3, 3), 3)
        self.rect = self.img.get_rect(center=(x, y))
        self.mask = pg.mask.from_surface(self.img)

        # расчет направления
        dx, dy = tx - x, ty - y
        dist = max(math.hypot(dx, dy), 1)
        self.vx = bul_speed * dx / dist
        self.vy = bul_speed * dy / dist
        self.damage = damage

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, screen):
        screen.blit(self.img, self.rect)


# магазин
class Shop:
    def __init__(self):
        img = pg.image.load('images/shop.png').convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 4, img.get_height() // 4))
        self.rect = self.img.get_rect(center=(WIDTH // 6, HEIGHT // 6))

    def draw(self, screen):
        screen.blit(self.img, self.rect)


class Border:
    def __init__(self):
        # граница между опасной и безопасной зоной
        img = pg.image.load('images/border.png').convert_alpha()
        self.img = pg.transform.scale(img, (img.get_width() // 2, int(img.get_height() * 1.3)))
        self.rect = self.img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def draw(self, screen):
        screen.blit(self.img, self.rect)


def mask_collide(a, b):
    # проверка столкновения
    offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
    return a.mask.overlap(b.mask, offset)


background = pg.image.load('images/test_backgr.png')
background = pg.transform.scale(background, (WIDTH, HEIGHT))

player = Player()
shop = Shop()
border = Border()

# список оружия
weapons = [
    Weapon("Пистолет", 10, 20, 8, 0),
    Weapon("Ружье", 20, 10, 10, 50),
    Weapon("Дробовик", 15, 40, 7, 80),
    Weapon("Винтовка", 50, 80, 15, 120),
]
current_weapon = weapons[0]

bullets = []
gems = []
enemies = []

# таймеры спавна и стрельбы
spawn_t = 0
enemy_t = 0
shoot_cd = 0

# состояние игрока
inventory = 0
inventory_limit = 5
money = 0
hp = 100
max_hp = 100

zone = "safe"
shop_open = False
tutorial = True
paused = False

# игровое время и событие "без правил"
game_minutes = 0
time_tick = 0
chaos_event = False


# главный цикл
running = True
while running:
    clock.tick(FPS)

    # обработка событий (ввод, пауза, магазин, взаимодействие)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:

            if tutorial and event.key == pg.K_SPACE:
                tutorial = False

            elif event.key == pg.K_ESCAPE and not tutorial:
                pause_sound.play()
                paused = not paused

            if not tutorial and not paused:
                # взаимодействие с границей и магазином
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

                # подбор камней
                if event.key == pg.K_r:
                    grab_sound.play()
                    for g in gems[:]:
                        if mask_collide(player, g) and inventory < inventory_limit:
                            gems.remove(g)
                            inventory += 1

                # действия в магазине
                if shop_open and event.key == pg.K_SPACE:
                    money += inventory * 10
                    inventory = 0

                if shop_open and event.key == pg.K_h and money >= 30:
                    hp = min(max_hp, hp + 50)
                    money -= 30

                if shop_open and event.key == pg.K_f and money >= 50:
                    inventory_limit += 5
                    money -= 50

                # смена оружия
                for i, w in enumerate(weapons):
                    if event.key == pg.K_1 + i and money >= w.price:
                        current_weapon = w
                        money -= w.price

    # обновление логики игры
    if not tutorial and not paused:

        # игровое время
        time_tick += 1
        if time_tick >= FPS // 60:
            game_minutes += 1
            time_tick = 0

        # запуск события "без правил" раз в сутки
        if game_minutes >= 24 * 60:
            chaos_event = True
            game_minutes = 0

        # движение игрока
        if not shop_open:
            keys = pg.key.get_pressed()
            dx = (keys[pg.K_d] - keys[pg.K_a])
            dy = (keys[pg.K_s] - keys[pg.K_w])
            player.move(dx, dy)
            player.update()

        # ограничение зон
        if not chaos_event:
            if zone == "safe" and player.rect.centerx > WIDTH // 2:
                player.rect.centerx = WIDTH // 2 - 5
            if zone == "danger" and player.rect.centerx < WIDTH // 2:
                player.rect.centerx = WIDTH // 2 + 5

        # спавн врагов и ресурсов
        if zone == "danger" or chaos_event:
            spawn_t += 1
            enemy_t += 1

            if spawn_t > (120 if chaos_event else 230):
                gems.append(Gem())
                spawn_t = 0

            if enemy_t > (120 if chaos_event else 230):
                enemies.append(Enemy(chaos_event))
                enemy_t = 0

        # обновление врагов и получение урона
        for en in enemies:
            en.update(player, chaos_event)
            hp -= en.attack(player)

        # стрельба
        if shoot_cd > 0:
            shoot_cd -= 1

        if pg.mouse.get_pressed()[0] and shoot_cd == 0 and not shop_open:
            pistol_sound.play()
            mx, my = pg.mouse.get_pos()

            # дробовик стреляет веером
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

        # обновление пуль и столкновения
        for bullet in bullets[:]:
            bullet.update()

            for en in enemies[:]:
                if mask_collide(bullet, en):
                    enemies.remove(en)
                    bullets.remove(bullet)
                    break

            if not screen.get_rect().colliderect(bullet.rect):
                bullets.remove(bullet)

    # отрисовка
    screen.blit(background, (0, 0))

    # визуальные эффекты зон
    if zone == "danger":
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((60, 0, 80, 120))
        screen.blit(overlay, (0, 0))

    if chaos_event:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((120, 0, 0, 80))
        screen.blit(overlay, (0, 0))

    border.draw(screen)
    shop.draw(screen)

    for g in gems: g.draw(screen)
    for en in enemies: en.draw(screen)
    for bullet in bullets: bullet.draw(screen)

    player.draw(screen)

    # интерфейс
    if not tutorial:
        h = game_minutes // 60
        m = game_minutes % 60
        screen.blit(font.render(f"{h:02}:{m:02}", True, WHITE), (WIDTH - 120, 20))

        screen.blit(font.render(f"Здоровье: {hp}", True, RED), (20, 20))
        screen.blit(font.render(f"$: {money}", True, GREEN), (20, 60))
        screen.blit(font.render(f"Камни: {inventory}/{inventory_limit}", True, BLUE), (20, 100))
        screen.blit(font.render(f"Оружие: {current_weapon.name}", True, WHITE), (20, 140))

    # окно магазина
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

    # экран обучения
    if tutorial:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        txt = ["WASD - движение", "E - взаимодействие", "R - взять",
               "M1 - стрелять", "ESC - пауза", "SPACE - старт игры"]

        for i, t in enumerate(txt):
            screen.blit(font.render(t, True, WHITE), (WIDTH // 2 - 200, 300 + i * 50))

    # пауза
    if paused:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        screen.blit(font.render("Пауза", True, WHITE), (WIDTH // 2 - 80, HEIGHT // 2 - 40))

    # конец игры
    if hp <= 0:
        screen.fill((0, 0, 0))
        screen.blit(font.render("Игра окончена", True, RED), (WIDTH // 2 - 100, HEIGHT // 2))
        pg.display.update()
        pg.time.delay(3000)
        running = False

    pg.display.update()

pg.quit()
