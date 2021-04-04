import os
import random
import sqlite3
import sys
import pygame
import pygame as pg

TOP = "top"
REST = 'rest'
LEFT = 'left'
RIGHT = 'right'
CIRCLE_SIZE = 39
CIRCLE_POINTS_SIZE = 40
SPRITE_SIZE1 = 50
SPRITE_SIZE2 = 60
SPRITE_SIZE3 = 90
size = width, height = 400, 500
pygame.init()
pygame.display.set_caption('Balls VS Blocks')
screen = pygame.display.set_mode(size)
wall_sprites = pygame.sprite.Group()
ball_sprites = pygame.sprite.Group()
point_sprites = pygame.sprite.Group()
square_sprites = pygame.sprite.Group()
main_menu_sprites = pygame.sprite.Group()
rating_sprites = pygame.sprite.Group()
skins_sprites = pygame.sprite.Group()
pause_spr = pygame.sprite.Group()
pause_sprites = pygame.sprite.Group()
game_over_sprites = pygame.sprite.Group()
video_sprites = pygame.sprite.Group()
game_over = False
sprite_speed = 5
points = {}
points1 = {}
segment_entities = []
clock = pygame.time.Clock()
FPS = 50
score = 0
time_delay = 0
safe = True
con = sqlite3.connect('db/balls vs blocks.db')
cur = con.cursor()
len_table = cur.execute('''SELECT COUNT(*) FROM user''').fetchall()[0][0]
if len_table == 0:
    cur.execute('''INSERT INTO user(name, result, skin) VALUES(?, ?, ?)''',
                ('player', 0, 'skin1.png'))
con.commit()

username = [elem[-1] for elem in cur.execute('''SELECT name From user''')]
pause_flag = False


def determine_side(rect1, rect2, shape_size1, shape_size2, shape_size3):
    """
    Определение стороны пересечения спрайтов
    """
    avg_cross = 80 - sprite_speed
    cross = rect2.y - rect1.y
    if avg_cross - 3 <= cross <= avg_cross + 3:
        return TOP
    else:
        if shape_size1 < (rect1.x - rect2.x) < shape_size2:
            return LEFT
        elif rect1.x - rect2.x >= shape_size3:
            return RIGHT


def load_image(name, colorkey=None):
    """
    Загрузка изображений
    """
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    """
    Выход из программы
    """
    con.close()
    pygame.quit()
    sys.exit()


class Wall(pygame.sprite.Sprite):
    """
    Класс спрайтов синих блоков
    """

    def __init__(self, coeff):
        super().__init__(wall_sprites)
        self.image = pygame.transform.scale(load_image('wall.png'), (5, 80))
        self.rect = self.image.get_rect()
        self.rect.x = random.sample([76, 157, 238, 319], 1)[0]
        self.rect.y = -70 + coeff
        attempt = 0
        while attempt <= 5 and len(
                pygame.sprite.spritecollide(self, square_sprites, False)) > 1:
            attempt += 1
            self.rect.x = random.sample([76, 157, 238, 319], 1)[0]
            if attempt == 5:
                square_sprites.remove(self)

    def update(self):
        """
        Перемещение спрайтов
        """
        global safe
        if self.rect.y > height:
            wall_sprites.remove(self)
        else:
            if safe:
                self.rect = self.rect.move(0, sprite_speed)


class Square(pygame.sprite.Sprite):
    """
    Класс спрайтов квадратов
    """

    def __init__(self):
        super().__init__(square_sprites)
        self.image = pygame.Surface([76, 80])
        self.rect = self.image.get_rect()
        self.rect.x = random.sample([0, 81, 162, 243, 324], 1)[0]
        self.rand_num = random.randint(1, 50)
        self.rect.y = -70
        points[id(self)] = self.rand_num * 10
        attempt = 0
        while attempt <= 5 and len(
                pygame.sprite.spritecollide(self, square_sprites, False)) > 1:
            attempt += 1
            self.rect.x = random.sample([0, 81, 162, 243, 324], 1)[0]
            if attempt == 5:
                square_sprites.remove(self)

    def update(self):
        """
        Перемещение спрайтов
        """
        global safe
        if points[id(self)] // 10 <= 9:
            self.image.fill((253, 233, 16))
        elif points[id(self)] // 10 <= 19:
            self.image.fill(pygame.Color('green'))
        elif points[id(self)] // 10 <= 29:
            self.image.fill(pygame.Color('blue'))
        elif points[id(self)] // 10 <= 39:
            self.image.fill((255, 136, 0))
        elif points[id(self)] // 10 <= 50:
            self.image.fill(pygame.Color('red'))

        font = pygame.font.Font(None, 60)
        text = font.render(f'{points[id(self)] // 10}', True,
                           pygame.Color('white'))
        size = text.get_rect(center=(self.rect.centerx, self.rect.y + 40))
        screen.blit(text, (size))

        if self.rect.y > height:
            square_sprites.remove(self)
            del points[id(self)]
        else:
            collision_ball = pygame.sprite.spritecollideany(
                self, ball_sprites)
            if safe:
                self.rect = self.rect.move(0, sprite_speed)
            else:
                if collision_ball:
                    side = determine_side(self.rect, collision_ball.rect, 40,
                                          87, 10)
                    if side == TOP:
                        safe = False


class Points(pygame.sprite.Sprite):
    """
    Класс спрайтов красного круга
    """

    def __init__(self):
        super().__init__(point_sprites)
        self.image = pygame.transform.scale(load_image('skin1.png'), (
            CIRCLE_POINTS_SIZE, CIRCLE_POINTS_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = self.get_random_position()
        self.rect.y = -50
        self.rand_num = random.randint(1, 5)
        points[id(self)] = self.rand_num
        attempt = 0
        while attempt <= 5 and len(
                pygame.sprite.spritecollide(self, square_sprites, False)) == 1:

            attempt += 1
            self.rect.x = self.get_random_position()
            if attempt == 5:
                point_sprites.remove(self)
        if len(pygame.sprite.spritecollide(self, point_sprites, False)) > 1:
            point_sprites.remove(self)

    @staticmethod
    def get_random_position():
        return random.sample([18, 97, 178, 259, 340], 1)[0]

    def update(self):
        """
        Перемещение спрайтов
        """
        if self.rect.y > height:
            del points[id(self)]
            point_sprites.remove(self)
        else:
            font = pygame.font.Font(None, 40)
            text = font.render(f'{self.rand_num}', True, pygame.Color('white'))
            text_x = self.rect.x + 12
            text_y = self.rect.y + 6
            screen.blit(text, (text_x, text_y))
            if safe:
                self.rect = self.rect.move(0, sprite_speed)


class Worm(pygame.sprite.Sprite):
    '''
    Класс спрайта, которым мы управляем с помощью курсора мыши
    '''

    def __init__(self, username):
        super().__init__(ball_sprites)
        self.ball_interval = 0
        skin = cur.execute('''SELECT skin FROM user WHERE name = (?)''',
                           (username,)).fetchall()[0][0]
        self.image = pygame.transform.scale(
            load_image(skin, -1), (CIRCLE_SIZE, CIRCLE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.y = height // 2 + self.ball_interval
        self.count = 4
        self.coord_x = width // 2 - (CIRCLE_SIZE / 2)
        self.position = width // 2 - (CIRCLE_SIZE / 2)
        self.blocked_coord = -1
        self.flag = True
        self.l = True
        self.r = False

    def update(self, x_pos):
        """
        Перемещение спрайта
        """
        global safe, game_over, score
        if x_pos >= width - CIRCLE_SIZE + 2:
            x_pos = width - CIRCLE_SIZE + 2
        collision_wall = pygame.sprite.spritecollideany(self, wall_sprites)
        collision_square = pygame.sprite.spritecollideany(self, square_sprites)
        if collision_wall:
            side = determine_side(collision_wall.rect, self.rect, 20, 39, -100)
            if side == TOP:
                safe = False
                self.rect.x = x_pos
            else:
                if side == LEFT:
                    self.rect.x = collision_wall.rect.x - 37
                    self.l = True
                elif side == RIGHT:
                    if x_pos < collision_wall.rect.x:
                        self.rect.x = collision_wall.rect.x - 5
                    self.r = True
                self.flag = False
        else:
            if self.flag:
                self.rect.x = x_pos
            self.flag = True
            self.l = False
            self.r = False

        if pygame.sprite.spritecollide(self, point_sprites, False):
            n = pygame.sprite.spritecollide(self, point_sprites, True)
            new_balls = points[id(n[0])]
            self.count += new_balls
        if collision_square:
            side = determine_side(collision_square.rect, self.rect, 40, 87, 10)
            if side == TOP:
                if not self.flag and self.l and x_pos <= self.rect.x:
                    self.rect.x = x_pos
                elif not self.flag and self.r and x_pos > self.rect.x:
                    self.rect.x = x_pos
                elif self.flag:
                    self.rect.x = x_pos
                if points[id(collision_square)] > 0:
                    safe = False
                    points[id(collision_square)] -= 1
                    if points[id(collision_square)] % 10 == 0:
                        self.count -= 1
                        score += 1
                else:
                    square_sprites.remove(
                        pygame.sprite.spritecollide(self, square_sprites,
                                                    False)[0])
            else:
                safe = True
                if side == LEFT:
                    self.rect.x = collision_square.rect.x
                else:
                    if x_pos + CIRCLE_SIZE < collision_square.rect.x:
                        self.rect.x = x_pos
                self.flag = False
        else:
            safe = True
            if self.flag:
                self.rect.x = x_pos
            self.flag = True
        if self.count == 0:
            game_over = True
        font = pygame.font.Font(None, 40)
        text = font.render(f'{self.count}', True, pygame.Color('white'))
        size = text.get_rect(center=(self.rect.centerx, self.rect.y - 12))
        screen.blit(text, (size))


def pause(username):
    """
    Пауза игры
    """
    global pause_flag
    pygame.mouse.set_visible(True)
    screen.fill(pygame.Color(246, 74, 70))
    draw_text(f'Score {score}', width // 2, height // 4, None,
              65,
              (100, 255, 100), None, True)
    image = 'resume_button.png'
    x = width / 4.5
    y = height / 1.7
    for i in range(2):
        go_sprite = pygame.sprite.Sprite()
        go_sprite.image = pygame.transform.scale(
            load_image(image), (SPRITE_SIZE3, SPRITE_SIZE3))
        go_sprite.rect = go_sprite.image.get_rect()
        go_sprite.rect.x = x
        go_sprite.rect.y = y
        x = width - x - SPRITE_SIZE3
        pause_sprites.add(go_sprite)
        image = 'house.png'
    pause_sprites.draw(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if x <= event.pos[0] <= x + SPRITE_SIZE3 and y <= event.pos[
                    1] <= y + SPRITE_SIZE3:
                    pause_flag = True
                    start_game(username)
                    break
                x = width - x - SPRITE_SIZE3
                if x <= event.pos[0] <= x + SPRITE_SIZE3 and y <= event.pos[
                    1] <= y + SPRITE_SIZE3:
                    main_menu()
                    break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause_flag = True
                    start_game(username)
                    break
        pygame.display.flip()


def gameOver(username):
    """
    Ооконание игры
    """
    global game_over
    screen.fill((246, 74, 70))
    cur.execute(
        '''UPDATE user SET result = (?) WHERE name = (?) and result < (?)''',
        (score, username, score))
    con.commit()
    font = pygame.font.Font(None, 50)
    text = font.render("GAME OVER!", True, (100, 255, 100))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 5 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)
    draw_text(f'Score {score}', width // 2, height / 2, None, 65,
              (100, 255, 100), None,
              True)
    image = 'house.png'
    rect_x = width / 4.5
    rect_y = height / 1.5
    for i in range(2):
        go_sprite = pygame.sprite.Sprite()
        go_sprite.image = pygame.transform.scale(
            load_image(image), (SPRITE_SIZE3, SPRITE_SIZE3))
        go_sprite.rect = go_sprite.image.get_rect()
        go_sprite.rect.x = rect_x
        go_sprite.rect.y = rect_y
        rect_x = width - rect_x - SPRITE_SIZE3
        game_over_sprites.add(go_sprite)
        image = 'reboot.png'
    game_over_sprites.draw(screen)
    pygame.mouse.set_visible(True)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_x <= event.pos[0] <= rect_x + SPRITE_SIZE3 and rect_y <= \
                        event.pos[1] <= rect_y + SPRITE_SIZE3:
                    game_over = False
                    main_menu()
                    break
                rect_x = width - rect_x - SPRITE_SIZE3
                if rect_x <= event.pos[0] <= rect_x + SPRITE_SIZE3 and rect_y <= \
                        event.pos[1] <= rect_y + SPRITE_SIZE3:
                    game_over = False
                    start_game(username)
                    break
        pygame.display.flip()


def start_game(username):
    """
    Начало игры
    """
    global pause_flag, sprite_speed, game_over, score, ball_sprites, point_sprites, wall_sprites, square_sprites
    if not pause_flag:
        ball_sprites = pygame.sprite.Group()
        point_sprites = pygame.sprite.Group()
        wall_sprites = pygame.sprite.Group()
        square_sprites = pygame.sprite.Group()
        sprite_speed = 5
        score = 0
        Worm(username)
    pause_flag = False
    move_distance = 0
    iteration = 0

    magic_number = 250 / sprite_speed
    new_points = magic_number * sprite_speed
    generation_distance = magic_number * sprite_speed

    x_position = width // 2 - (CIRCLE_SIZE / 2)
    rand_num = 1
    pause_sprite = pygame.sprite.Sprite()
    pause_sprite.image = pygame.transform.scale(
        load_image('pause.png', -1), (SPRITE_SIZE1, SPRITE_SIZE1))
    pause_sprite.rect = pause_sprite.image.get_rect()
    pause_sprite.rect.x = 0
    pause_sprite.rect.y = 10
    pause_spr.add(pause_sprite)
    count = 0
    while True:
        if game_over:
            gameOver(username)
            break
        else:
            if safe:
                move_distance += sprite_speed
            screen.fill(pygame.Color('black'))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEMOTION:
                    x_position = event.pos[0]
                    if event.pos[1] > 60:
                        pygame.mouse.set_visible(False)
                    else:
                        pygame.mouse.set_visible(True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_sprite.rect.x <= event.pos[
                        0] <= pause_sprite.rect.x + SPRITE_SIZE1 and pause_sprite.rect.y <= \
                            event.pos[1] <= pause_sprite.rect.y + SPRITE_SIZE1:
                        pause(username)
                        break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause(username)
                        break
            if rand_num == 1:
                if move_distance >= generation_distance:
                    for j in range(random.randint(1, 5)):
                        Square()
                    for i in range(random.randint(0, 2)):
                        Points()
            else:
                if move_distance >= generation_distance:
                    for j in range(random.randint(1, 5)):
                        Square()
                    for i in range(random.randint(0, 2)):
                        Points()
                    generation_distance = magic_number * sprite_speed
                if move_distance >= generation_distance / 2 and count == 0:
                    for i in range(random.randint(0, 2)):
                        k = (move_distance - generation_distance // 2)
                        Wall(k)
                        count = 1

            if move_distance >= new_points:
                count = 0
                iteration += 1
                for i in range(random.randint(1, 2)):
                    Points()
                move_distance = 0
                rand_num = random.randint(1, 2)
                if rand_num == 1:
                    magic_number = 250 / sprite_speed
                    new_points = magic_number * sprite_speed
                    generation_distance = magic_number * sprite_speed
                else:
                    magic_number = 340 / sprite_speed
                    new_points = magic_number * sprite_speed
                    generation_distance = magic_number * sprite_speed / 2
                if iteration == 30 and sprite_speed < 10:
                    sprite_speed += 1
                    iteration = 0
                    rand_num = 1
                    magic_number = 250 / sprite_speed
                    new_points = magic_number * sprite_speed
                    generation_distance = magic_number * sprite_speed
            ball_sprites.update(x_position)
            ball_sprites.draw(screen)
            point_sprites.draw(screen)
            point_sprites.update()
            wall_sprites.draw(screen)
            wall_sprites.update()
            square_sprites.draw(screen)
            square_sprites.update()
            font = pygame.font.Font(None, 70)
            text = font.render(f'{score}', True, (255, 136, 0))
            screen.blit(text, text.get_rect(center=(335, 40)))
            pause_spr.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def draw_text(text, x, y, font, font_cize, color, frame=None, centre=None):
    """
    Отрисовка текста
    """
    font = pygame.font.SysFont(font, font_cize)
    text = font.render(text, True, color)
    text_size = (x, y)
    if centre is not None:
        text_size = text.get_rect(center=(text_size[0], text_size[1]))
    screen.blit(text, (text_size[0], text_size[1]))
    if frame:
        text_w = text.get_width()
        text_h = text.get_height()
        pygame.draw.rect(screen, (0, 255, 0),
                         (text_size[0] - 10, text_size[1] - 10,
                          text_w + 10, text_h + 10), 1)


def rating():
    """
    Рейтинг игроков
    """
    arrow_sprite = pygame.sprite.Sprite()
    arrow_sprite.image = pygame.transform.scale(
        load_image('arrow.png'), (SPRITE_SIZE1, SPRITE_SIZE1))
    arrow_sprite.rect = arrow_sprite.image.get_rect()
    arrow_sprite.rect.x = 10
    arrow_sprite.rect.y = 15
    rating_sprites.add(arrow_sprite)
    screen.fill(pygame.Color(246, 74, 70))
    draw_text('Top players', width // 2, height // 12, None,
              55,
              (100, 255, 100), None, True)
    pygame.draw.line(screen, (0, 0, 0), (0, height // 7), (width, height // 7),
                     width=2)
    sorted_data = sorted(cur.execute('''SELECT * FROM user''').fetchall(),
                         key=lambda x: x[2], reverse=True)
    y = height // 7
    num = 1
    ln = len(sorted_data)
    if ln > 8:
        ln = 8
    for i in range(ln):
        draw_text(f'{num}. {sorted_data[i][1]}', width / 14, y + 12, None, 40,
                  (100, 255, 100), None, None)
        draw_text(f'{sorted_data[i][2]}', width / 1.5, y + 12, None, 40,
                  (100, 255, 100), None, None)
        y += 50
        num += 1
        pygame.draw.line(screen, (0, 0, 0), (0, y),
                         (width, y), width=2)
    rating_sprites.draw(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if arrow_sprite.rect.x <= event.pos[
                    0] <= arrow_sprite.rect.x + SPRITE_SIZE1 and arrow_sprite.rect.y <= \
                        event.pos[1] <= arrow_sprite.rect.y + SPRITE_SIZE1:
                    main_menu()
                    break
        pygame.display.flip()


def skins(username):
    """
    Выбор скинов
    """
    screen.fill(pygame.Color(0, 0, 0))
    draw_text('Skins', width // 2, height // 8, None,
              55,
              (100, 255, 100), None, True)
    arrow_sprite = pygame.sprite.Sprite()
    arrow_sprite.image = pygame.transform.scale(
        load_image('arrow.png', -1), (SPRITE_SIZE1, SPRITE_SIZE1))
    arrow_sprite.rect = arrow_sprite.image.get_rect()
    arrow_sprite.rect.x = 10
    arrow_sprite.rect.y = 35
    skins_sprites.add(arrow_sprite)
    x = (width // 3 - SPRITE_SIZE2) // 2
    y = 0
    distance_x = width // 3
    distance_y = width // 3
    for i in range(9):
        skins_sprite = pygame.sprite.Sprite()
        skins_sprite.image = pygame.transform.scale(
            load_image(f'skin{i + 1}.png', -1), (SPRITE_SIZE2, SPRITE_SIZE2))
        skins_sprite.rect = skins_sprite.image.get_rect()
        if i % 3 == 0:
            y += distance_y
            skins_sprite.rect.x = 0
            x = (width // 3 - SPRITE_SIZE2) // 2
        skins_sprite.rect.x += x
        skins_sprite.rect.y = y
        x += distance_x
        skins_sprites.add(skins_sprite)
    skin = cur.execute('''SELECT skin FROM user WHERE name = (?)''',
                       (username,)).fetchall()[0][0]
    skin_number = [int(i) for i in skin if i.isdigit()]
    skin_number_x = (skin_number[0] - 1) % 3
    skin_number_y = (skin_number[0] - 1) // 3
    old_coord = (skin_number_x, skin_number_y)
    pygame.draw.rect(screen, (0, 255, 0), (skin_number_x * distance_x,
                                           skin_number_y * distance_y + distance_y - distance_y / 4,
                                           distance_x,
                                           distance_y), 1)
    skins_sprites.draw(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] >= distance_y:
                    x_pos = (event.pos[0]) // distance_x
                    y_pos = (event.pos[1] + 33) // (distance_y) - 1
                    pygame.draw.rect(screen, (0, 255, 0), (x_pos * distance_x,
                                                           y_pos * distance_y + distance_y - distance_y / 4,
                                                           distance_x,
                                                           distance_y), 1)
                    if old_coord[0] != x or old_coord[1] != y:
                        pygame.draw.rect(screen, (0, 0, 0),
                                         (old_coord[0] * distance_x,
                                          old_coord[
                                              1] * distance_y + distance_y - distance_y / 4,
                                          distance_x,
                                          distance_y), 1)
                        old_coord = (x_pos, y_pos)
                    cur.execute(
                        '''UPDATE user SET skin = (?) WHERE name = (?)''',
                        (f'skin{y_pos * 3 + x_pos + 1}.png', username))
                    con.commit()
                if arrow_sprite.rect.x <= event.pos[
                    0] <= arrow_sprite.rect.x + SPRITE_SIZE1 and arrow_sprite.rect.y <= \
                        event.pos[1] <= arrow_sprite.rect.y + SPRITE_SIZE1:
                    main_menu()
                    break
        pygame.display.flip()


def main_menu():
    """
    Главное меню игры
    """
    cur.execute('''DELETE FROM USER''')
    con.commit()
    cup_sprite = pygame.sprite.Sprite()
    cup_sprite.image = pygame.transform.scale(load_image('cup.png', -1),
                                              (SPRITE_SIZE1, SPRITE_SIZE1))
    cup_sprite.rect = cup_sprite.image.get_rect()
    cup_sprite.rect.x = width // 4 + 20
    cup_sprite.rect.y = height - width // 4
    main_menu_sprites.add(cup_sprite)
    circle_radius = 30
    circle_width = 2
    ball_sprite = pygame.sprite.Sprite()
    ball_sprite.image = pygame.transform.scale(
        load_image('football_ball.png', -1), (SPRITE_SIZE2, SPRITE_SIZE2))
    ball_sprite.rect = ball_sprite.image.get_rect()
    ball_sprite.rect.x = width // 2 + 30
    ball_sprite.rect.y = height - width // 4 - 2 * circle_width
    main_menu_sprites.add(ball_sprite)
    font = pg.font.Font(None, 32)
    input_box = pg.Rect(width // 4, height // 2, 200, 32)
    color_inactive = pygame.Color(167, 252, 0)
    color = color_inactive
    color_active = pygame.Color(0, 0, 0)
    active = False
    try:
        text = username[-1]
    except IndexError:
        text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                if text != '' and username == []:
                    cur.execute(
                        '''INSERT INTO user(name, result, skin) VALUES(?, ?, ?)''',
                        (text, '0', 'skin1.png'))
                elif username != [] and text not in username:
                    cur.execute(
                        '''INSERT INTO user(name, result, skin) VALUES(?, ?, ?)''',
                        (text, 0, 'skin1.png'))
                con.commit()
                if input_box.collidepoint(event.pos):
                    active = not active
                elif cup_sprite.rect.x <= event.pos[
                    0] <= cup_sprite.rect.x + SPRITE_SIZE1 and cup_sprite.rect.y <= \
                        event.pos[1] <= cup_sprite.rect.y + SPRITE_SIZE1:
                    username.append(text)
                    rating()
                    break
                elif ball_sprite.rect.x <= event.pos[
                    0] <= ball_sprite.rect.x + SPRITE_SIZE2 and ball_sprite.rect.y <= \
                        event.pos[1] <= ball_sprite.rect.y + SPRITE_SIZE2:
                    username.append(text)
                    skins(text)
                    break
                else:
                    username.append(text)
                    start_game(text)
                    break
                color = color_active if active else color_inactive

            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        screen.fill((246, 74, 70))
        txt_surface = font.render(text, True, color)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pg.draw.rect(screen, color, input_box, 1)
        draw_text('Balls VS Blocks', width // 2, height // 4, 'Viner Hand ITC',
                  45,
                  (100, 255, 100), None, True)
        draw_text('username', width // 2, height / 2.5, None, 45,
                  (0, 0, 0), None, True)
        draw_text('Tap to start', width // 2, height - SPRITE_SIZE1 * 3, None,
                  35,
                  (0, 0, 0), None, True)
        pygame.draw.circle(screen, pygame.Color('black'),
                           (width / 3.5 + 1 + 30, 425),
                           circle_radius, circle_width)
        main_menu_sprites.draw(screen)
        pygame.display.flip()


main_menu()
