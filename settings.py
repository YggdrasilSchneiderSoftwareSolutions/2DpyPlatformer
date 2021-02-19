# game options/settings
TITLE = "2D pyPlatformer I"
WIDTH = 1024
HEIGHT = 768
FPS = 60

TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player properties
PLAYER_ACC = 4
PLAYER_GRAV = 0.8
PLAYER_JUMP = 15
PLAYER_HEALTH = 100

# Enemy properties
GROUND_SNIFF_PIXEL = TILESIZE * 0.25

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (0, 155, 155)
BROWN = (160, 82, 45)
GRAY = (128, 128, 128)
