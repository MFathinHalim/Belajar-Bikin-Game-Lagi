from os import listdir
from os.path import isfile, join

import pygame

pygame.init()

pygame.display.set_caption("Game Fathin")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
MAX_JUMP_X = 180
MIN_GAP_X = 40


window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        if obj.rect.right > offset_x and obj.rect.left < offset_x + WIDTH:
            obj.draw(window, offset_x)

    player.draw(window, offset_x)
    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            overlap = player.rect.clip(obj.rect)

            # ❌ kalau overlap lebih tinggi daripada lebar
            # ini SIDE collision, BUKAN vertical
            if overlap.height > overlap.width:
                continue

            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()

            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()


def show_end_screen(text, color):
    screen = pygame.display.set_mode((500, 300))
    font = pygame.font.SysFont("arial", 48, bold=True)
    label = font.render(text, True, color)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                run = False

        screen.fill((0, 0, 0))
        screen.blit(
            label,
            (
                screen.get_width() // 2 - label.get_width() // 2,
                screen.get_height() // 2 - label.get_height() // 2,
            ),
        )
        pygame.display.update()

    pygame.quit()
    quit()


def handle_move(player, objects, offset_x):
    visible_objects = [
        obj
        for obj in objects
        if obj.rect.right > offset_x - 50 and obj.rect.left < offset_x + WIDTH + 50
    ]

    keys = pygame.key.get_pressed()
    player.on_wall = False
    if not player.wall_stick:
        player.wall_dir = None
    # ======================
    # HORIZONTAL MOVE FIRST
    # ======================
    player.x_vel = 0

    if not player.wall_stick:
        if keys[pygame.K_a]:
            player.x_vel = -PLAYER_VEL
            player.direction = "left"
        elif keys[pygame.K_d]:
            player.x_vel = PLAYER_VEL
            player.direction = "right"
    else:
        player.x_vel = 0  # 🔒 freeze horizontal

    player.rect.x += player.x_vel
    player.update()

    for obj in visible_objects:
        if obj.name == "flag":
            continue

        if player.rect.colliderect(obj.rect):
            overlap = player.rect.clip(obj.rect)
            if overlap.width < overlap.height:
                if not player.wall_stick:
                    if player.x_vel > 0:
                        player.rect.right = obj.rect.left
                        player.wall_dir = "right"
                    elif player.x_vel < 0:
                        player.rect.left = obj.rect.right
                        player.wall_dir = "left"
                player.on_wall = True
                player.x_vel = 0
                break

    # ======================
    # WALL STICK
    # ======================
    player.wallStick(keys)

    # ======================
    # VERTICAL MOVE SECOND
    # ======================
    player.rect.y += player.y_vel
    player.update()

    for obj in visible_objects:
        if obj.name == "flag":
            continue
        if player.rect.colliderect(obj.rect):
            overlap = player.rect.clip(obj.rect)

            # landing
            if overlap.width > overlap.height and player.y_vel > 0:
                player.rect.bottom = obj.rect.top
                player.landed()

            # ceiling
            elif overlap.width > overlap.height and player.y_vel < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_flag(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(272, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3
    WALL_JUMP_X = 8
    WALL_JUMP_Y = 10

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.on_wall = False
        self.wall_stick = False
        self.wall_dir = None
        self.sprite = None
        self.current_sprite_name = None

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def wall_jump(self):
        if not self.wall_stick or not self.wall_dir:
            return
        # lompat menjauh dari wall
        if self.wall_dir == "left" and self.on_wall:
            self.x_vel = self.WALL_JUMP_X
            self.direction = "right"
        elif self.wall_dir == "right" and self.on_wall:
            self.x_vel = -self.WALL_JUMP_X
            self.direction = "left"

        self.y_vel = -self.WALL_JUMP_Y
        self.wall_stick = False
        self.fall_count = 0
        self.jump_count = 1

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        self.prev_direction = self.direction
        self.direction = "left"
        if self.prev_direction != self.direction:
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        self.prev_direction = self.direction
        self.direction = "right"
        if self.prev_direction != self.direction:
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.fall_count += 1

        if self.wall_stick:
            self.y_vel = min(self.y_vel, 2)

        self.update_sprite()

    def wallStick(self, keys):
        self.wall_stick = False

        if not self.on_wall:
            return

        if self.y_vel <= 0:
            return

        if self.wall_dir == "left" and keys[pygame.K_a]:
            self.wall_stick = True
            self.direction = "left"
        elif self.wall_dir == "right" and keys[pygame.K_d]:
            self.wall_stick = True
            self.direction = "right"

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.sprite_rect.x - offset_x, self.sprite_rect.y))

    def update_sprite(self):
        # WALL HAS PRIORITY
        sprite_sheet_name = "wall_jump_" + self.direction
        if self.wall_stick and self.wall_dir:
            sprite_sheet_name = "wall_jump_" + self.wall_dir

        else:
            if (not self.wall_stick) and not self.wall_dir:
                sprite_sheet = "idle"

                if self.y_vel < 0:
                    if self.jump_count == 1:
                        sprite_sheet = "jump"
                    elif self.jump_count == 2:
                        sprite_sheet = "double_jump"

                elif (
                    self.y_vel > self.GRAVITY * 2
                    and (not self.wall_stick)
                    and not self.wall_dir
                ):
                    sprite_sheet = "fall"

                elif self.x_vel != 0:
                    sprite_sheet = "run"

                sprite_sheet_name = sprite_sheet + "_" + self.direction

        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.sprite_rect = self.sprite.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.sprite)

        for x in range(self.mask.get_size()[0]):
            self.mask.set_at((x, 0), 0)
            self.mask.set_at((x, 1), 0)


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Flag(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, name="flag")
        block = get_flag(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, name="block")
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def generate_floor(y, block_size):
    floor = []
    for x in range(0, WIDTH, block_size):
        floor.append(Block(x, y, block_size))
    return floor


def load_level_from_text(path, block_size):
    platforms = []
    flags = []
    player_spawn = [0, 0]

    with open(path, "r") as f:
        lines = f.read().splitlines()

    for row_index, line in enumerate(lines):
        for col_index, char in enumerate(line):
            x = col_index * block_size
            y = row_index * block_size
            if char == "M":
                platforms.append(Block(x, y, block_size))
            elif char == "P":
                player_spawn = [x, y]
            elif char == "F":
                flags.append(Flag(x, y, block_size))

    return platforms, player_spawn, flags, len(lines) * block_size


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    objects = []

    level_platforms, player_spawn, flags, level_height = load_level_from_text(
        "levels/level1.txt", block_size
    )
    player = Player(player_spawn[0], player_spawn[1] - 50, 50, 50)

    objects.extend(level_platforms)
    objects.extend(flags)

    offset_x = 0

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.wall_stick:
                        player.wall_jump()
                    elif player.jump_count < 2:
                        player.jump()

        player.loop(FPS)
        # ===== KALAH JIKA JATUH =====
        if player.rect.top > level_height + 200:
            show_end_screen("YOU LOSE", (255, 80, 80))

        # ===== MENANG =====
        for flag in flags:
            if player.rect.colliderect(flag.rect):
                show_end_screen("YOU WIN", (80, 255, 80))

        handle_move(player, objects, offset_x)
        draw(window, background, bg_image, player, objects, offset_x)
        target_offset_x = player.rect.centerx - WIDTH // 2
        offset_x = int(offset_x + (target_offset_x - offset_x) * 0.1)

    return


if __name__ == "__main__":
    main(window)
