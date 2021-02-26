# Sprite classes for platform game
from abc import ABCMeta, abstractmethod
import pygame as pg
from settings import *
from utils import *
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.idle_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_00.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_01.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_02.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_03.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_04.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_05.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_06.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_07.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_08.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_09.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_idle_10.png'))]
        self.run_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_00.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_01.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_02.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_03.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_04.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_05.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_06.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_07.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_08.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_09.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'player_run_10.png'))]
        self.jump_image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_jump.png'))
        self.fall_image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_fall.png'))
        self.killed_image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'player', 'pl_death.png'))
        self.image = self.idle_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.pos = vec(x, y)
        self.onGround = False
        self.movement = [0, 0]
        self.gravity = 0
        self.coins = 0
        self.health = PLAYER_HEALTH
        self.num_frames = 0
        self.num_dead_frames = 0
        self.game_over = False
        self.won = False
        self.num_won_frames = 0
        self.last_movement_left = False
        self.cooldown_dive = 500
        self.last_dive_time = pg.time.get_ticks()

    def get_image(self):
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

        # Drehen für links
        if self.last_movement_left:
            self.image = pg.transform.flip(self.image, True, False)

    def jump(self):
        # jump only if standing on a platform
        if self.onGround:
            self.onGround = False
            self.gravity = -PLAYER_JUMP
            play_sound('jump')

    def jump_cut(self):
        if self.onGround is False:
            if self.gravity < -3:
                self.gravity = -3
            
    def left(self):
        self.movement[0] -= PLAYER_ACC
        self.last_movement_left = True

    def right(self):
        self.movement[0] += PLAYER_ACC
        self.last_movement_left = False

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
                pickup.on_collect()
                pickup.kill()

    def check_enemy_hit(self):
        enemy_hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        if enemy_hits:
            for enemy in enemy_hits:
                if enemy.killed is False:  # Nur für lebende Gegner
                    # Player ist über dem Enemy -> kill
                    if self.rect.bottom == enemy.rect.top or self.rect.bottom - enemy.rect.top <= 10:
                        self.gravity = -3  # Rückstoß
                        enemy.killed = True
                        play_sound('kill')
                    else:  # Enemy hat uns getroffen -> Schaden
                        self.health -= enemy.damage
                        play_sound('hurt')

        bullet_hits = pg.sprite.spritecollide(self, self.game.bullets, False)
        if bullet_hits:
            for bullet in bullet_hits:
                self.health -= bullet.damage
                bullet.kill()
                play_sound('hurt')

    def check_drowning(self):
        water_hits = pg.sprite.spritecollide(self, self.game.water, False)
        if water_hits:
            now = pg.time.get_ticks()
            if now - self.last_dive_time >= self.cooldown_dive:
                self.health -= 10
                play_sound('drown')
                self.last_dive_time = now

    def update(self):
        # game over
        if self.health <= 0:
            self.num_dead_frames += 1
            if not self.game_over:  # Damit Sound nur 1x abgespielt wird
                self.game_over = True
                pg.mixer.music.stop()
                play_sound('death')
            self.image = self.killed_image
            if self.num_dead_frames == FPS * 5:  # ca. 5 Sekunden
                self.game.playing = False
            return

        # gewonnen
        if self.coins == self.game.coin_count:
            self.num_won_frames += 1
            if not self.won:
                self.won = True
                pg.mixer.music.stop()
                play_sound('won')
            if self.num_won_frames == FPS * 5:
                self.game.playing = False
            return

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

        self.check_drowning()

        self.get_image()
        self.movement = [0, 0]

        # wrap around the sides of the screen
        self.pos = vec(self.rect.midbottom)
        if self.pos.x > self.game.map.width:
            self.rect.x = 0
        if self.pos.x < 0:
            self.rect.x = self.game.map.width - TILESIZE

        # Loch im Boden
        if self.pos.y > self.game.map.height:
            self.health = 0


class Enemy(pg.sprite.Sprite, metaclass=ABCMeta):
    def __init__(self, x, y, game):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.initial_pos_x = self.rect.x
        self.x = x
        self.y = y
        self.game = game
        self.visibility = -200
        self.damage = 10
        self.acceleration = 2
        self.move_direction = {'left': False, 'right': False}
        self.killed = False
        self.num_frames = 0
        self.num_dead_frames = 0
        self.image = None
        self.solid = False

    @abstractmethod
    def get_image(self):
        pass

    def update(self):
        is_visible, distance_x = self.player_is_visible()
        if is_visible is True:
            can_move = self.check_collision()
            if distance_x < 0 and can_move:  # Player ist links
                self.rect.x -= self.acceleration
                self.move_direction['left'] = True
                self.move_direction['right'] = False
            elif distance_x > 0 and can_move:  # Player ist rechts
                self.rect.x += self.acceleration
                self.move_direction['left'] = False
                self.move_direction['right'] = True
            else:  # Hinderniss, stehen bleiben
                self.move_direction['left'] = False
                self.move_direction['right'] = False
        else:  # zurückbewegen, wenn Player nicht mehr sichtbar
            if self.rect.x > self.initial_pos_x:
                self.rect.x -= self.acceleration
                self.move_direction['left'] = True
                self.move_direction['right'] = False
            elif self.rect.x < self.initial_pos_x:
                self.rect.x += self.acceleration
                self.move_direction['left'] = False
                self.move_direction['right'] = True

        # Ausgangsposition, keine Bewegung mehr
        if self.rect.x == self.initial_pos_x:
            self.move_direction['left'] = False
            self.move_direction['right'] = False

        self.get_image()
        self.x = self.rect.x / TILESIZE
        self.y = self.rect.y / TILESIZE

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
        if wall_hits:
            return False

        on_ground = True
        # Schauen, was 1 Tile unter Enemy ist
        self.rect.y += TILESIZE
        ground_tiles = pg.sprite.spritecollide(self, self.game.all_sprites, False)
        for tile in ground_tiles:
            if not self.game.platforms.has(tile) and tile != self and tile.solid is False:
                # Tile unten ist keine Platform, nicht self (wegen temp. Rect-Verschiebung) oder solid
                on_ground = False
                break
        # Wieder auf Ausgangsposition
        self.rect.y -= TILESIZE
        if not on_ground:
            return False

        player_hit = self.rect.colliderect(self.game.player.rect)
        if player_hit:
            return False

        return True


class EnemyPinky(Enemy):
    def __init__(self, x, y, game):
        Enemy.__init__(self, x, y, game)
        self.idle_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_00.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_01.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_02.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_03.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_04.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_05.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_06.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_07.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_08.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_09.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_idle_10.png'))]
        self.run_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_00.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_01.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_02.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_03.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_04.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_05.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_06.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_07.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_08.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_09.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_run_10.png'))]
        self.killed_image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'pinky', 'pink_death.png'))
        self.image = self.idle_images[0]

    def get_image(self):
        # Tot
        if self.killed:
            self.num_dead_frames += 1
            self.image = self.killed_image
            if self.num_dead_frames == 10:
                self.kill()
            return

        self.num_frames += 1  # TODO: in Methode der Superklasse auslagern
        if self.num_frames == FPS:
            self.num_frames = 0

        # Gehen / Stehen
        if self.move_direction['left'] is False and self.move_direction['right'] is False:
            self.image = get_image_for_frames(self.num_frames, self.idle_images)
        else:
            if self.move_direction['left'] is True:
                self.image = pg.transform.flip(get_image_for_frames(self.num_frames,
                                                                    self.run_images), True, False)
            else:
                self.image = get_image_for_frames(self.num_frames, self.run_images)


class EnemyMasked(Enemy):
    def __init__(self, x, y, game):
        Enemy.__init__(self, x, y, game)
        self.idle_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_00.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_01.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_02.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_03.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_04.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_05.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_06.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_07.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_08.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_09.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_idle_10.png'))]
        self.run_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_00.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_01.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_02.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_03.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_04.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_05.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_06.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_07.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_08.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_09.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_run_10.png'))]
        self.killed_image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'masked', 'masked_death.png'))
        self.image = self.idle_images[0]
        self.visibility = -300
        self.damage = 20
        self.acceleration = 3

    def get_image(self):
        # Tot
        if self.killed:
            self.num_dead_frames += 1
            self.image = self.killed_image
            if self.num_dead_frames == 10:
                self.kill()
            return

        self.num_frames += 1  # TODO: in Methode der Superklasse auslagern
        if self.num_frames == FPS:
            self.num_frames = 0

        # Gehen / Stehen
        if self.move_direction['left'] is False and self.move_direction['right'] is False:
            self.image = get_image_for_frames(self.num_frames, self.idle_images)
        else:
            if self.move_direction['left'] is True:
                self.image = pg.transform.flip(get_image_for_frames(self.num_frames,
                                                                    self.run_images), True, False)
            else:
                self.image = get_image_for_frames(self.num_frames, self.run_images)


class EnemyVirtual(Enemy):
    def __init__(self, x, y, game):
        Enemy.__init__(self, x, y, game)
        self.idle_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_00.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_01.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_02.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_03.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_04.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_05.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_06.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_07.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_08.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_09.png')),
                            load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_idle_10.png'))]
        self.run_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_00.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_01.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_02.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_03.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_04.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_05.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_06.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_07.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_08.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_09.png')),
                           load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_run_10.png'))]
        self.killed_image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'enemies', 'virtual', 'virtual_death.png'))
        self.image = self.idle_images[0]
        self.visibility = -400
        self.damage = 20
        self.acceleration = 5
        self.cooldown_shot = 300
        self.last_shot_time = pg.time.get_ticks()

    def update(self):
        is_visible, distance_x = self.player_is_visible()
        if is_visible is True:
            player_direction = 'left' if distance_x < 0 else 'right'
            self.shoot(player_direction)
            can_move = self.check_collision()
            if distance_x < 0 and can_move:  # Player ist links
                self.rect.x -= self.acceleration
                self.move_direction['left'] = True
                self.move_direction['right'] = False
            elif distance_x > 0 and can_move:  # Player ist rechts
                self.rect.x += self.acceleration
                self.move_direction['left'] = False
                self.move_direction['right'] = True
            else:  # Hinderniss, stehen bleiben
                self.move_direction['left'] = False
                self.move_direction['right'] = False
        else:  # zurückbewegen, wenn Player nicht mehr sichtbar
            if self.rect.x > self.initial_pos_x:
                self.rect.x -= self.acceleration
                self.move_direction['left'] = True
                self.move_direction['right'] = False
            elif self.rect.x < self.initial_pos_x:
                self.rect.x += self.acceleration
                self.move_direction['left'] = False
                self.move_direction['right'] = True

        # Ausgangsposition, keine Bewegung mehr
        if self.rect.x == self.initial_pos_x:
            self.move_direction['left'] = False
            self.move_direction['right'] = False

        self.get_image()
        self.x = self.rect.x / TILESIZE
        self.y = self.rect.y / TILESIZE

    def get_image(self):
        # Tot
        if self.killed:
            self.num_dead_frames += 1
            self.image = self.killed_image
            if self.num_dead_frames == 10:
                self.kill()
            return

        self.num_frames += 1  # TODO: in Methode der Superklasse auslagern
        if self.num_frames == FPS:
            self.num_frames = 0

        # Gehen / Stehen
        if self.move_direction['left'] is False and self.move_direction['right'] is False:
            self.image = get_image_for_frames(self.num_frames, self.idle_images)
        else:
            if self.move_direction['left'] is True:
                self.image = pg.transform.flip(get_image_for_frames(self.num_frames,
                                                                    self.run_images), True, False)
            else:
                self.image = get_image_for_frames(self.num_frames, self.run_images)

    def shoot(self, direction):
        if not self.game.player.game_over:
            # schiessen, wenn 0,3 sec seit dem letzten Schuss vergangen sind
            now = pg.time.get_ticks()
            if now - self.last_shot_time >= self.cooldown_shot:
                bullet_coord = vec(self.rect.centerx / TILESIZE, self.rect.centery / TILESIZE)
                bullet = Shot(bullet_coord.x, bullet_coord.y, direction, self.game)
                self.game.bullets.add(bullet)
                self.game.all_sprites.add(bullet)
                self.last_shot_time = now
                play_sound('shot')


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
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'brick1.png'))
        self.solid = True


class Block(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'block1.png'))
        self.solid = True


class Ground(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'ground1.png'))
        self.solid = True


class Water(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)


class WaterBottom(Water):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'water_bottom.png'))


class WaterTop(Water):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.num_frames = 0
        self.rotating_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'water_top_00.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'water_top_01.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'water_top_02.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'water_top_03.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'water_top_04.png'))]
        self.image = self.rotating_images[0]

    def get_image(self):
        self.num_frames += 1
        if self.num_frames == FPS:
                self.num_frames = 0

        self.image = get_image_for_frames(self.num_frames, self.rotating_images)

    def update(self):
        self.get_image()


class Sky(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y)
        self.image.fill(BLUE)
        # Sky immer transparent, damit Hintergrundbild gezeigt wird
        self.image.set_colorkey(BLUE)


class Collectible(Tile, metaclass=ABCMeta):
    def __init__(self, x, y, game):
        Tile.__init__(self, x, y)
        self.game = game

    @abstractmethod
    def on_collect(self):
        pass


class Coin(Collectible):
    def __init__(self, x, y, game):
        Collectible.__init__(self, x, y, game)
        self.num_frames = 0
        self.rotating_images = [load_image(os.path.join(GAME_FOLDER, 'tiles', 'coin_00.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'coin_01.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'coin_02.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'coin_03.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'coin_04.png')),
                                load_image(os.path.join(GAME_FOLDER, 'tiles', 'coin_05.png'))]
        self.image = self.rotating_images[0]

    def on_collect(self):
        play_sound('coin')
        self.game.player.coins += 1

    def get_image(self):  # TODO: in Game auslagern
        self.num_frames += 1
        if self.num_frames == FPS:
            self.num_frames = 0

        self.image = get_image_for_frames(self.num_frames, self.rotating_images)

    def update(self):
        self.get_image()


class Strawberry(Collectible):
    def __init__(self, x, y, game):
        Collectible.__init__(self, x, y, game)
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'strawberry.png'))

    def on_collect(self):
        play_sound('collect')
        self.game.player.health += 20


class Banana(Collectible):
    def __init__(self, x, y, game):
        Collectible.__init__(self, x, y, game)
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'banana.png'))

    def on_collect(self):
        play_sound('collect')
        self.game.player.health += 50


class Cherry(Collectible):
    def __init__(self, x, y, game):
        Collectible.__init__(self, x, y, game)
        self.image = load_image(os.path.join(GAME_FOLDER, 'tiles', 'cherry.png'))

    def on_collect(self):
        play_sound('collect')
        self.game.player.health += 10


class Shot(pg.sprite.Sprite):
    def __init__(self, x, y, direction, game):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        # Rect x, y muss * TILESIZE, damit Position mit dem Enemy gleich ist
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        self.direction = direction
        self.game = game
        self.damage = 20
        self.acceleration = 7

    def update(self):
        if not self.collide_with_platform():
            if self.direction == 'left':  # TODO evtl über boolean
                self.rect.x -= self.acceleration
            else:
                self.rect.x += self.acceleration

            # hat Spielfeld verlassen
            if self.rect.x > self.game.map.width or self.rect.x < 0:
                self.kill()
        else:
            self.kill()

    def collide_with_platform(self):
        # doKill = True falls Wand zerstört werden kann...
        return pg.sprite.spritecollide(self, self.game.platforms, False)
