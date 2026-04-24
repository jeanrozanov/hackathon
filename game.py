import pygame as pg

# картинки фона и границы взяты из интернета, просто для набросков кода, будут изменены
# здесь определяются константы, функции и классы
FPS = 60
WIDTH, HEIGHT = 1000, 1000
BLUE = (151, 210, 240)
BLACK = (0, 0, 0)
speed = 3


class Player:  # персонаж, игрок. им можно управлять, он может стрелять в монстров и таскать ресурсы
    def __init__(self):
        self.surf = pg.image.load('images/player.png').convert_alpha()
        self.new_surf = pg.transform.scale(self.surf, (self.surf.get_width() / 8, self.surf.get_height() / 8))

        self.rect = self.new_surf.get_rect(center=(WIDTH / 1.2, HEIGHT / 1.2))
        self.player_mask = pg.mask.from_surface(self.new_surf)

    def move(self, dx=0, dy=0):  # движение персонажа
        if (self.rect.left + dx * speed) > 0 and (self.rect.right + dx * speed) < WIDTH:
            self.rect.x += dx * speed
        if (self.rect.bottom + dy * speed) > 0 and (self.rect.top + dy * speed) < HEIGHT:
            self.rect.y += dy * speed

    def draw(self, screen):  # отрисовка персонажа
        screen.blit(self.new_surf, self.rect)


class Border:  # граница, позволяет выйти в опасную зону и обратно
    def __init__(self):
        self.border_surf = pg.image.load('images/border.png').convert_alpha()
        self.new_border_surf = pg.transform.scale(self.border_surf, (self.border_surf.get_width() * 5,
                                                                     self.border_surf.get_height() * 5))
        self.border_rect = self.new_border_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.border_mask = pg.mask.from_surface(self.new_border_surf)

    def draw(self, screen):  # отрисовка границы
        screen.blit(self.new_border_surf, self.border_rect)


class Monster: # монстры будут нападать на игрока, но их можно будет убить
    def __init__(self):
        pass


class Diamond:  # в опасной зоне будут полезные ископаемые. их можно будет продавать для покупки оружия и не только
    # не обязательно именно алмазы! можно сделать разновидность ресурсов, с разными ценами и свойствами
    def __init__(self):
        self.diamond_surf = None
        self.diamond_rect = None
        self.diamond_mask = pg.mask.from_surface(self.diamond_surf)

    def draw(self, screen):  # отрисовка
        screen.blit(self.diamond_surf, self.diamond_rect)


class Shop:  # магазин, можно купить оружие и апгрейд для персонажа
    def __init__(self):
        self.shop_surf = None
        self.shop_rect = None
        self.shop_mask = pg.mask.from_surface(self.shop_surf)

    def draw(self, screen):  # отрисовка магазина
        screen.blit(self.shop_surf, self.shop_rect)


def check_collision_with_border(border, player):  # проверка коллизий с игроком и границей для выхода
    offset_1 = (border.border_rect.x - player.rect.x, border.border_rect.y - player.rect.y)
    if player.player_mask.overlap(border.border_mask, offset_1) is not None:
        return True

def check_collision_with_resource(diamond, player): # проверка коллизий с игроком и ресурсами (чтобы он мог их таскать)
    offset_2 = (diamond.diamond_rect.x - player.rect.x, diamond.diamond_rect.y - player.rect.y)
    if player.player_mask.overlap(border.border_mask, offset_2) is not None:
        return True


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Игра")
clock = pg.time.Clock()

background = pg.image.load('images/background.png')  # задний фон
background = pg.transform.scale(background, (background.get_width() * 2,
                                             background.get_height() * 2))
border = Border()
player = Player()

player.draw(screen)
border.draw(screen)

pg.display.update()

# шрифты
font = pg.font.SysFont(None, 24)
interaction_text = font.render("Нажмите E для перехода", True, (255, 255, 255))
# главный цикл
flag_play = True
while flag_play:
    # настраиваем частоту итераций в секунду
    clock.tick(FPS)

    # цикл обработки событий
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            flag_play = False
            break
    if not flag_play:
        break

    if check_collision_with_border(border, player):
        screen.blit(interaction_text, (20, 20))

    keys = pg.key.get_pressed()
    if keys[pg.K_RIGHT]:
        player.move(dx=1)
    if keys[pg.K_LEFT]:
        player.move(dx=-1)
    if keys[pg.K_DOWN]:
        player.move(dy=1)
    if keys[pg.K_UP]:
        player.move(dy=-1)

    screen.blit(background, (0, 0))
    player.draw(screen)
    border.draw(screen)

    pg.display.update()
