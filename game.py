import pygame as pg
import random


FPS = 60
WIDTH, HEIGHT = 2000, 1000
speed = 4


class Player: # персонаж, игрок. им можно управлять, он может стрелять в монстров и таскать ресурсы
    def __init__(self):
        self.surf = pg.image.load('images/player.png').convert_alpha()
        self.image = pg.transform.scale(
            self.surf,
            (self.surf.get_width() // 8, self.surf.get_height() // 8)
        )
        self.rect = self.image.get_rect(center=(WIDTH // 4, HEIGHT // 1.2))

    def move(self, dx=0, dy=0):
        new_rect = self.rect.move(dx * speed, dy * speed)

        if 0 < new_rect.left and new_rect.right < WIDTH:
            self.rect.x = new_rect.x
        if 0 < new_rect.top and new_rect.bottom < HEIGHT:
            self.rect.y = new_rect.y

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Diamond: # в опасной зоне будут полезные ископаемые. их можно будет продавать для покупки оружия и не только
    # не обязательно именно алмазы! можно сделать разновидность ресурсов, с разными ценами и свойствами
    def __init__(self):
        self.image = pg.image.load("images/diamond.png").convert_alpha()
        self.image = pg.transform.scale(
            self.image,
            (self.image.get_width() // 9, self.image.get_height() // 9)
        )

        x = random.randint(WIDTH // 2 + 50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Shop: # магазин, можно купить оружие и апгрейд для персонажа, а также продать ресурсы
    def __init__(self):
        self.image = pg.image.load('images/shop.png').convert_alpha()
        self.image = pg.transform.scale(
            self.image,
            (self.image.get_width() // 4, self.image.get_height() // 4)
        )
        self.rect = self.image.get_rect(center=(WIDTH // 6, HEIGHT // 6))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Border: # граница, позволяет выйти в опасную зону и обратно
    def __init__(self):
        self.image = pg.image.load('images/border.png').convert_alpha()
        self.image = pg.transform.scale(
            self.image,
            (self.image.get_width() // 2,
             int(self.image.get_height() * 1.3))
        )
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def check_collision(a, b):
    return a.rect.colliderect(b.rect)



pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

background = pg.image.load('images/test_backgr.png') # задний фон
background = pg.transform.scale(background, (WIDTH, HEIGHT))

player = Player()
border = Border()
shop = Shop()

font = pg.font.SysFont(None, 36)

current_zone = "safe"
inventory = 0
money = 0

diamonds = []
spawn_timer = 0

shop_open = False
tutorial_open = True

running = True
while running:
    clock.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:

            # закрыть обучение
            if tutorial_open and event.key == pg.K_SPACE:
                tutorial_open = False

            if not tutorial_open:
                # переход зоны
                if event.key == pg.K_e:
                    if check_collision(border, player):
                        if current_zone == "safe":
                            current_zone = "danger"
                            player.rect.center = (WIDTH * 0.75, HEIGHT / 1.2)
                        else:
                            current_zone = "safe"
                            player.rect.center = (WIDTH * 0.25, HEIGHT / 1.2)

                    elif check_collision(shop, player):
                        shop_open = not shop_open

                # подбор алмазов на R
                if event.key == pg.K_r:
                    for d in diamonds[:]:
                        if player.rect.colliderect(d.rect):
                            diamonds.remove(d)
                            inventory += 1

                # продажа
                if shop_open and event.key == pg.K_SPACE:
                    money += inventory * 10
                    inventory = 0

    # если обучение закрыто - игра работает
    if not tutorial_open:

        if not shop_open:
            keys = pg.key.get_pressed()
            if keys[pg.K_d]:
                player.move(dx=1)
            if keys[pg.K_a]:
                player.move(dx=-1)
            if keys[pg.K_s]:
                player.move(dy=1)
            if keys[pg.K_w]:
                player.move(dy=-1)

        # граница
        if current_zone == "safe" and player.rect.centerx > WIDTH // 2:
            player.rect.centerx = WIDTH // 2 - 5
        if current_zone == "danger" and player.rect.centerx < WIDTH // 2:
            player.rect.centerx = WIDTH // 2 + 5

        # спавн
        if current_zone == "danger":
            spawn_timer += 1
            if spawn_timer > 120:
                diamonds.append(Diamond())
                spawn_timer = 0

    # отрисовка
    screen.blit(background, (0, 0))

    if current_zone == "danger":
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((60, 0, 80))
        screen.blit(overlay, (0, 0))

    border.draw(screen)
    shop.draw(screen)

    for d in diamonds:
        d.draw(screen)

    player.draw(screen)

    # подсказки
    if not tutorial_open:

        if check_collision(border, player):
            screen.blit(font.render("E - перейти", True, (255,255,255)),
                        (player.rect.x, player.rect.y - 40))

        if check_collision(shop, player):
            screen.blit(font.render("E - магазин", True, (255,255,255)),
                        (player.rect.x, player.rect.y - 70))

        # подсказка для алмазов
        for d in diamonds:
            if player.rect.colliderect(d.rect.inflate(40, 40)):
                screen.blit(font.render("R - взять", True, (255,255,255)),
                            (d.rect.x, d.rect.y - 30))

        screen.blit(font.render(f"Алмазы: {inventory}", True, (255,255,255)), (20, 20))
        screen.blit(font.render(f"Деньги: {money}", True, (255,255,255)), (20, 60))

    # экран магазина
    if shop_open:
        panel = pg.Surface((600, 300))
        panel.fill((30, 30, 30))
        screen.blit(panel, (WIDTH//2 - 300, HEIGHT//2 - 150))

        screen.blit(font.render("МАГАЗИН", True, (255,255,255)),
                    (WIDTH//2 - 80, HEIGHT//2 - 120))
        screen.blit(font.render("SPACE - продать все", True, (255,255,255)),
                    (WIDTH//2 - 200, HEIGHT//2))
        screen.blit(font.render(f"У тебя: {inventory}", True, (255,255,255)),
                    (WIDTH//2 - 100, HEIGHT//2 + 50))

    # обучение
    if tutorial_open:
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        lines = [
            "ОБУЧЕНИЕ",
            "",
            "WASD — движение",
            "E — взаимодействие / переход / магазин",
            "R — подобрать ресурс",
            "SPACE — закрыть это окно / продать в магазине",
            "",
            "Иди в опасную зону, собирай ресурсы",
            "и продавай их в магазине!",
            "",
            "Нажми SPACE чтобы начать"
        ]

        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - 300, 200 + i*40))

    pg.display.update()

pg.quit()
