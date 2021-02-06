# Sprite classes for platform game
import pygame as pg
import utils
from settings import *
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.idle_images = [utils.load_image('tiles/player/pl_idle_00.png'),
                            utils.load_image('tiles/player/pl_idle_01.png'),
                            utils.load_image('tiles/player/pl_idle_02.png'),
                            utils.load_image('tiles/player/pl_idle_03.png'),
                            utils.load_image('tiles/player/pl_idle_04.png'),
                            utils.load_image('tiles/player/pl_idle_05.png'),
                            utils.load_image('tiles/player/pl_idle_06.png'),
                            utils.load_image('tiles/player/pl_idle_07.png'),
                            utils.load_image('tiles/player/pl_idle_08.png'),
                            utils.load_image('tiles/player/pl_idle_09.png'),
                            utils.load_image('tiles/player/pl_idle_10.png')]
        self.run_images = [utils.load_image('tiles/player/player_run_00.png'),
                           utils.load_image('tiles/player/player_run_01.png'),
                           utils.load_image('tiles/player/player_run_02.png'),
                           utils.load_image('tiles/player/player_run_03.png'),
                           utils.load_image('tiles/player/player_run_04.png'),
                           utils.load_image('tiles/player/player_run_05.png'),
                           utils.load_image('tiles/player/player_run_06.png'),
                           utils.load_image('tiles/player/player_run_07.png'),
                           utils.load_image('tiles/player/player_run_08.png'),
                           utils.load_image('tiles/player/player_run_09.png'),
                           utils.load_image('tiles/player/player_run_10.png')]
        self.jump_image = utils.load_image('tiles/player/pl_jump.png')
        self.fall_image = utils.load_image('tiles/player/pl_fall.png')
        self.image = self.idle_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.onGround = False
        self.movement = [0, 0]
        self.gravity = 0
        self.coins = 0
        self.health = PLAYER_HEALTH
        self.num_frames = 0

    def get_image(self):  # TODO: in Game auslagern
        self.num_frames += 1
        if self.num_frames == FPS:
            self.num_frames = 0

        # Stehen / Gehen
        if self.movement[0] == 0:
            self.image = self.idle_images[self.num_frames // 6]
        else:
            self.image = self.run_images[self.num_frames // 6]
        # Springen
        if self.onGround is False:
            if self.movement[1] < 0:
                self.image = self.jump_image
            else:
                self.image = self.fall_image

    def jump(self):
        # jump only if standing on a platform
        if self.onGround:
            self.onGround = False
            self.gravity = -PLAYER_JUMP
            utils.play_sound('jump')

    def jump_cut(self):
        if self.onGround is False:
            if self.gravity < -3:
                self.gravity = -3
            
    def left(self):
        self.movement[0] -= PLAYER_ACC

    def right(self):
        self.movement[0] += PLAYER_ACC

    def move(self):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.rect.x += self.movement[0]
        hit_list = pg.sprite.spritecollide(self, self.game.platforms, False)
        for tile in hit_list:
            if self.movement[0] > 0:
                self.rect.right = tile.rect.left
                collision_types['right'] = True
            elif self.movement[0] < 0:
                self.rect.left = tile.rect.right
                collision_types['left'] = True
        self.rect.y += self.movement[1]
        hit_list = pg.sprite.spritecollide(self, self.game.platforms, False)
        for tile in hit_list:
            if self.movement[1] > 0:
                self.rect.bottom = tile.rect.top
                collision_types['bottom'] = True
            elif self.movement[1] < 0:
                self.rect.top = tile.rect.bottom
                collision_types['top'] = True
        return collision_types

    def check_pickups(self):
        pickup_hits = pg.sprite.spritecollide(self, self.game.collectibles, False)
        if pickup_hits:
            for pickup in pickup_hits:
                if type(pickup) == Coin:
                    utils.play_sound('coin')
                    pickup.kill()
                    self.coins += 1

    def check_enemy_hit(self):
        enemy_hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if enemy_hits:
            for enemy in enemy_hits:
                if enemy.killed is False:  # Nur für lebende Gegner
                    # Player ist über dem Enemy -> kill
                    if self.rect.bottom == enemy.rect.top or self.rect.bottom - enemy.rect.top <= 10:
                        self.gravity = -3  # Rückstoß
                        enemy.killed = True
                        utils.play_sound('kill')
                    else:  # Enemy hat uns getroffen -> Schaden
                        self.health -= enemy.damage
                        utils.play_sound('hurt')

    def update(self):
        # game over
        if self.health <= 0:
            pg.mixer.music.stop()
            utils.play_sound('death')
            self.game.playing = False
            pg.time.delay(2000)

        self.movement[1] += self.gravity
        self.gravity += PLAYER_GRAV
        if self.gravity > 10:
            self.gravity = 10

        collisions = self.move()

        if collisions['bottom']:
            self.onGround = True
            self.gravity = 0

        self.check_pickups()

        self.check_enemy_hit()

        self.get_image()
        self.movement = [0, 0]

        # wrap around the sides of the screen
        self.pos = vec(self.rect.midbottom)
        if self.pos.x > self.game.map.width:
            self.rect.x = 0
        if self.pos.x < 0:
            self.rect.x = self.game.map.width - TILESIZE


class Enemy(pg.sprite.Sprite):  # TODO: von Superklasse ableiten
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.idle_images = [utils.load_image('tiles/enemies/pinky/pink_idle_00.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_01.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_02.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_03.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_04.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_05.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_06.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_07.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_08.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_09.png'),
                            utils.load_image('tiles/enemies/pinky/pink_idle_10.png')]
        self.run_images = [utils.load_image('tiles/enemies/pinky/pink_run_00.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_01.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_02.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_03.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_04.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_05.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_06.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_07.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_08.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_09.png'),
                           utils.load_image('tiles/enemies/pinky/pink_run_10.png')]
        self.killed_image = utils.load_image('tiles/enemies/pinky/pink_hit_4.png')
        self.image = self.idle_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.initial_pos_x = self.rect.x
        self.x = x
        self.y = y
        self.solid = False
        self.game = game
        self.visibility = -200
        self.damage = 10
        self.move_direction = {'left': False, 'right': False}
        self.killed = False
        self.num_frames = 0
        self.num_dead_frames = 0

    def get_image(self):  # TODO: in Game auslagern
        # Tot
        if self.killed:
            self.num_dead_frames += 1
            self.image = self.killed_image
            if self.num_dead_frames == 10:
                self.kill()
            return

        self.num_frames += 1
        if self.num_frames == FPS:
            self.num_frames = 0

        # Gehen / Stehen
        if self.move_direction['left'] is False and self.move_direction['right'] is False:
            self.image = utils.get_image_for_frames(self.num_frames, self.idle_images)
        else:
            self.image = utils.get_image_for_frames(self.num_frames, self.run_images)

    def update(self):
        is_visible, distance_x = self.player_is_visible()
        if is_visible is True:
            can_move = self.check_collision()
            if distance_x < 0 and can_move:  # Player ist links
                self.rect.x -= ENEMY_ACC
                self.move_direction['left'] = True
                self.move_direction['right'] = False
            elif distance_x > 0 and can_move:  # Player ist rechts
                self.rect.x += ENEMY_ACC
                self.move_direction['left'] = False
                self.move_direction['right'] = True
        else:  # zurückbewegen, wenn Player nicht mehr sichtbar
            if self.rect.x > self.initial_pos_x:
                self.rect.x -= ENEMY_ACC
                self.move_direction['left'] = True
                self.move_direction['right'] = False
            elif self.rect.x < self.initial_pos_x:
                self.rect.x += ENEMY_ACC
                self.move_direction['left'] = False
                self.move_direction['right'] = True

        # Ausgangsposition, keine Bewegung mehr
        if self.rect.x == self.initial_pos_x:
            self.move_direction['left'] = False
            self.move_direction['right'] = False

        self.get_image()

    def player_is_visible(self):
        player_pos = self.game.player.rect
        # berechnen, wie weit der Player auf der x-Achse entfernt ist
        player_distance_x = player_pos.x - self.rect.x
        # gleiche Höhe und nur Pixel der visibility entfernt -> Player in Sichtweite
        if player_pos.y == self.rect.y and self.visibility <= player_distance_x <= -self.visibility:
            return True, player_distance_x
        return False, None

    def check_collision(self):
        wall_hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y += 1
        if self.move_direction['right']:
            self.rect.x += TILESIZE
        elif self.move_direction['left']:
            self.rect.x -= TILESIZE
        on_ground = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if self.move_direction['right']:
            self.rect.x -= TILESIZE
        elif self.move_direction['left']:
            self.rect.x += TILESIZE

        player_hit = self.rect.colliderect(self.game.player.rect)

        if wall_hits or not on_ground or player_hit:
            return False
        return True


class Tile(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.x = x
        self.y = y
        self.solid = False


class Brick(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = utils.load_image('tiles/brick1.png')
        self.solid = True


class Block(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = utils.load_image('tiles/block1.png')
        self.solid = True


class Ground(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = utils.load_image('tiles/ground1.png')
        self.solid = True


class Sky(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image.fill(BLUE)
        # Sky immer transparent, damit Hintergrundbild gezeigt wird
        self.image.set_colorkey(BLUE)


class Coin(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.num_frames = 0
        self.rotating_images = [utils.load_image('tiles/coin_00.png'),
                                utils.load_image('tiles/coin_01.png'),
                                utils.load_image('tiles/coin_02.png'),
                                utils.load_image('tiles/coin_03.png'),
                                utils.load_image('tiles/coin_04.png'),
                                utils.load_image('tiles/coin_05.png')]
        self.image = self.rotating_images[0]

    def get_image(self):  # TODO: in Game auslagern
        self.num_frames += 1
        if self.num_frames == FPS:
            self.num_frames = 0

        self.image = utils.get_image_for_frames(self.num_frames, self.rotating_images)

    def update(self):
        self.get_image()
