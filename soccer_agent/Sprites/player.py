import pathlib
import pygame
from soccer_agent.Sprites.entity import Entity
from enum import Enum

class Team(Enum):
    RED = 1
    BLUE = 2

class Player(Entity):
    def __init__(
        self,
        sprite_file: pathlib.Path,
        bb_color: pygame.Color = pygame.Color(255, 0, 0),
        has_alpha=True,
    ) -> None:
        super().__init__(sprite_file=sprite_file, is_circular=True, bb_color=bb_color, has_alpha=has_alpha)
        # Set transparency
        # self._image.set_colorkey((255, 255, 255), RLEACCEL)