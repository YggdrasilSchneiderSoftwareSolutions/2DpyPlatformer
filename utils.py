import pygame
import settings
import os

GAME_FOLDER = os.path.dirname(__file__)

SOUNDS = {}


def load_image(filename, color_key=None):
    # Pygame das Bild laden lassen.
    image = pygame.image.load(filename)

    # Das Pixelformat der Surface an den Bildschirm (genauer: die screen-Surface) anpassen.
    # Dabei die passende Funktion verwenden, je nach dem, ob wir ein Bild mit Alpha-Kanal haben oder nicht.
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()

    # Colorkey des Bildes setzen, falls nicht None.
    # Bei -1 den Pixel im Bild an Position (0, 0) als Colorkey verwenden.
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key, pygame.RLEACCEL)

    return image


def get_image_for_frames(num_frames, images_list):
    # Schauen, wie oft die Bildersequenz in die FPS passt (+1 wegen Array): FPS/nBilder + 1
    # Ermittlen, welches Bild zum aktuellen Frame passt: nFrames / Bilder pro FPS
    image_index = num_frames / (settings.FPS / (len(images_list) + 1))
    return images_list[int(image_index - 1)]  # -1 wegen Arrayindex


def init_sounds():
    global SOUNDS
    global GAME_FOLDER
    SOUNDS['coin'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'coin.wav'))
    SOUNDS['jump'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'jump.wav'))
    SOUNDS['kill'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'kill.wav'))
    SOUNDS['hurt'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'hurt.wav'))
    SOUNDS['death'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'death.wav'))
    SOUNDS['collect'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'collect.wav'))
    SOUNDS['won'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'won.wav'))
    SOUNDS['shot'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'shot.wav'))
    SOUNDS['drown'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'drown.wav'))


def play_sound(name):
    global SOUNDS
    sound = SOUNDS[name]
    if sound is not None:
        sound.play()
