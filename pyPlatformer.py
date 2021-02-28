from sprites import *
import os
from tilemap import *


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        init_sounds()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        # TODO: Evtl. Fullscreen?
        #self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        pg.key.set_repeat(0)
        # Fenster zentrieren
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.clock = pg.time.Clock()
        # Map laden
        self.maps = [Map(os.path.join(GAME_FOLDER, 'maps', 'map1.txt')),
                     Map(os.path.join(GAME_FOLDER, 'maps', 'map2.txt'))]
        self.map = None
        self.camera = None
        self.running = True
        # Hintergrund auf das gesamte Fenster vergrößern
        self.image = pg.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'background1.png')),
                                        (WIDTH, HEIGHT))
        self.playing = False
        self.all_sprites = None
        self.platforms = None
        self.enemies = None
        self.collectibles = None
        self.bullets = None
        self.water = None
        self.player = None
        self.font_health = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 24)
        self.img_health = self.font_health.render('Health: ', True, WHITE)
        self.font_coins = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 24)
        self.img_coins = self.font_coins.render('Coins: ', True, WHITE)
        self.font_game_over = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 144)
        self.img_game_over = self.font_game_over.render('Game Over', True, RED)
        self.paused = False
        self.font_paused = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 144)
        self.img_paused = self.font_paused.render('Pause', True, WHITE)
        self.font_quit = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 24)
        self.img_quit = self.font_quit.render('q drücken zum Beenden', True, WHITE)
        self.font_won = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 144)
        self.img_won = self.font_won.render('Sieg!', True, WHITE)
        self.coin_count = 0
        self.level_index = 0

    def new(self, level_map_index):
        self.map = self.maps[level_map_index]
        self.coin_count = 0

        pg.mixer.music.load(os.path.join(GAME_FOLDER, 'music', 'game.mp3'))
        pg.mixer.music.play(-1, 0.0)
        pg.mixer.music.set_volume(.5)
        # start a new game
        # Für weitere Spiele, müssen alle Entities hier neu initialisiert werden
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.collectibles = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.water = pg.sprite.Group()

        self.camera = Camera(self.map.width, self.map.height)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                tile_sprite = None
                if tile == ".":  # Sky
                    tile_sprite = Sky(col, row)
                elif tile == "#":  # Block
                    tile_sprite = Block(col, row)
                elif tile == "G":  # Ground
                    tile_sprite = Ground(col, row)
                elif tile == "B":  # Brick
                    tile_sprite = Brick(col, row)
                elif tile == "o":  # Coin
                    tile_sprite = Coin(col, row, self)
                    self.collectibles.add(tile_sprite)
                    self.coin_count += 1
                elif tile == "S":  # Strawberry
                    tile_sprite = Strawberry(col, row, self)
                    self.collectibles.add(tile_sprite)
                elif tile == "(":  # Banana
                    tile_sprite = Banana(col, row, self)
                    self.collectibles.add(tile_sprite)
                elif tile == "C":  # Cherry
                    tile_sprite = Cherry(col, row, self)
                    self.collectibles.add(tile_sprite)
                elif tile == "E":  # Enemy Pinky
                    tile_sprite = EnemyPinky(col, row, self)
                    self.enemies.add(tile_sprite)
                elif tile == "M":  # Enemy Masked
                    tile_sprite = EnemyMasked(col, row, self)
                    self.enemies.add(tile_sprite)
                elif tile == "V":  # Enemy Virtual
                    tile_sprite = EnemyVirtual(col, row, self)
                    self.enemies.add(tile_sprite)
                elif tile == "P":  # Player - wird nicht als Tile behandelt
                    if self.player is not None and self.player.won:  # Health übernehmen, wenn gewonnen
                        self.player = Player(col, row, self, self.player.health)
                    else:
                        self.player = Player(col, row, self)
                    self.all_sprites.add(self.player)
                elif tile == "w":  # Wasser oben
                    tile_sprite = WaterTop(col, row)
                    self.water.add(tile_sprite)
                elif tile == "W":  # Wasser unten
                    tile_sprite = WaterBottom(col, row)
                    self.water.add(tile_sprite)
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
        if self.paused:
            return
        # Game Loop - Update
        self.all_sprites.update()
        self.camera.update(self.player)

    def events(self):
        # Game Loop - events
        if not self.paused:
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
                if event.key == pg.K_ESCAPE:
                    if not self.paused:
                        self.paused = True
                    else:
                        self.paused = False
                if event.key == pg.K_q:
                    pg.event.post(pg.event.Event(pg.QUIT))
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
        if self.player.game_over:
            self.screen.blit(self.img_game_over, (100, 200))
        if self.paused:
            self.screen.blit(self.img_paused, (220, 200))
            self.screen.blit(self.img_quit, (20, 700))
        if self.player.won:
            self.screen.blit(self.img_won, (330, 200))
        # Player am Schluss, damit im Vordergrund
        self.screen.blit(self.player.image, self.camera.apply(self.player))
        # after drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self, game):
        pg.mixer.music.load(os.path.join(GAME_FOLDER, 'music', 'menu.mp3'))
        pg.mixer.music.play(-1, 0.0)
        pg.mixer.music.set_volume(.5)

        selected = {'Start': True, 'Quit': False}

        self.running = True
        while self.running:
            self.clock.tick(FPS)

            if self.player is not None and self.player.won:
                self.level_index += 1
                if self.level_index == len(self.maps):  # durchgespielt, zurück auf init
                    self.player = None
                    self.level_index = 0
                    pg.mixer.music.load(os.path.join(GAME_FOLDER, 'music', 'menu.mp3'))
                    pg.mixer.music.play(-1, 0.0)
                    pg.mixer.music.set_volume(.5)
                else:
                    game.new(self.level_index)
            elif self.player is not None and self.player.game_over:
                self.level_index = 0
                self.player = None
                pg.mixer.music.load(os.path.join(GAME_FOLDER, 'music', 'menu.mp3'))
                pg.mixer.music.play(-1, 0.0)
                pg.mixer.music.set_volume(.5)

            if selected['Start'] is True:
                font_start = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 92)
                img_start = font_start.render('Start!', True, WHITE)
                font_quit = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 72)
                img_quit = font_quit.render('Ende', True, WHITE)
            else:
                font_start = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 72)
                img_start = font_start.render('Start', True, WHITE)
                font_quit = pg.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 92)
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
                            game.new(self.level_index)  # erstes Level laden
                        else:
                            pg.mixer.music.fadeout(1000)
                            self.running = False

            self.screen.fill(BLACK)
            self.screen.blit(img_start, (250, 300))
            self.screen.blit(img_quit, (400, 400))

            pg.display.flip()


if __name__ == "__main__":
    g = Game()
    while g.running:
        g.show_start_screen(g)

    pg.quit()
    exit(0)
