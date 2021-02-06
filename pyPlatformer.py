from sprites import *
import os
from tilemap import *


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        utils.init_sounds()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        # TODO: Evtl. Fullscreen?
        #self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        pg.key.set_repeat(1, 30)
        # Fenster zentrieren
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.clock = pg.time.Clock()
        # Map laden
        game_folder = os.path.dirname(__file__)
        self.map = Map(os.path.join(game_folder, 'maps/map1.txt'))
        self.camera = Camera(self.map.width, self.map.height)
        self.running = True
        # Hintergrund auf das gesamte Fenster vergrößern
        self.image = pg.transform.scale(utils.load_image('tiles/background1.png'), (WIDTH, HEIGHT))
        self.playing = False
        self.all_sprites = None
        self.platforms = None
        self.enemies = None
        self.collectibles = None
        self.player = None
        self.font_health = pg.font.Font(None, 24)
        self.img_health = self.font_health.render('Health: ', True, WHITE)
        self.font_coins = pg.font.Font(None, 24)
        self.img_coins = self.font_coins.render('Coins: ', True, WHITE)

    def new(self):
        pg.mixer.music.load('music/game.mp3')
        pg.mixer.music.play(-1, 0.0)
        pg.mixer.music.set_volume(.5)
        # start a new game
        # Für weitere Spiele, müssen alle Entities hier neu initialisiert werden
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.collectibles = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == ".":  # Sky
                    tile_sprite = Sky(col, row)
                elif tile == "#":  # Block
                    tile_sprite = Block(col, row)
                elif tile == "G":  # Ground
                    tile_sprite = Ground(col, row)
                elif tile == "B":  # Brick
                    tile_sprite = Brick(col, row)
                elif tile == "o":  # Coin
                    tile_sprite = Coin(col, row)
                    self.collectibles.add(tile_sprite)
                elif tile == "E":  # Enemy
                    tile_sprite = Enemy(col, row, self)
                    self.enemies.add(tile_sprite)
                else:  # Sky
                    tile_sprite = Sky(col, row)

                if tile_sprite is not None:
                    self.all_sprites.add(tile_sprite)
                    if tile_sprite.solid is True:
                        self.platforms.add(tile_sprite)

        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

        pg.mixer.music.fadeout(1000)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        self.camera.update(self.player)

    def events(self):
        # Game Loop - events
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.player.left()
        if keys[pg.K_RIGHT]:
            self.player.right()
        # Events for keyup and keydown
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)
        self.screen.blit(self.image, (0, 0))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # Anzeigen
        self.img_health = self.font_health.render('Health: ' + str(self.player.health), True, WHITE)
        self.screen.blit(self.img_health, (10, 10))
        self.img_coins = self.font_health.render('Coins: ' + str(self.player.coins), True, WHITE)
        self.screen.blit(self.img_coins, (10, 35))
        # Player am Schluss, damit im Vordergrund
        self.screen.blit(self.player.image, self.camera.apply(self.player))
        # after drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self, game):
        pg.mixer.music.load('music/menu.mp3')
        pg.mixer.music.play(-1, 0.0)
        pg.mixer.music.set_volume(.5)

        selected = {'Start': True, 'Quit': False}

        self.running = True
        while self.running:
            self.clock.tick(FPS)

            if selected['Start'] is True:
                font_start = pg.font.Font(None, 92)
                img_start = font_start.render('Start!', True, WHITE)
                font_quit = pg.font.Font(None, 72)
                img_quit = font_quit.render('Ende', True, WHITE)
            else:
                font_start = pg.font.Font(None, 72)
                img_start = font_start.render('Start', True, WHITE)
                font_quit = pg.font.Font(None, 92)
                img_quit = font_quit.render('Ende', True, WHITE)

            # Events im Menü
            for event in pg.event.get():
                # check for closing window
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        selected['Start'] = True
                        selected['Quit'] = False
                    if event.key == pg.K_DOWN:
                        selected['Start'] = False
                        selected['Quit'] = True
                    if event.key == pg.K_RETURN:
                        if selected['Start'] is True:
                            pg.mixer.music.fadeout(1000)
                            game.new()
                            pg.mixer.music.load('music/menu.mp3')
                            pg.mixer.music.play(-1, 0.0)
                            pg.mixer.music.set_volume(.5)
                        else:
                            pg.mixer.music.fadeout(1000)
                            self.running = False

            self.screen.fill(BLACK)
            self.screen.blit(img_start, (400, 300))
            self.screen.blit(img_quit, (400, 400))

            pg.display.flip()

    def show_go_screen(self):
        # game over/continue
        pass


g = Game()
while g.running:
    g.show_start_screen(g)

pg.quit()
exit(0)
