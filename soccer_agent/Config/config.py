from dataclasses import dataclass
from typing import List
from soccer_agent.Sprites.entity import Entity

import pygame
from soccer_agent.Sprites.field import SoccerField
from soccer_agent.GUI.window import PyGame_Window

@dataclass(eq=True, repr=True)
class Config:
    field_bb_color: pygame.Color
    player_bb_color: pygame.Color
    # Simulation config
    top_path_colors: List[pygame.Color]

@dataclass(frozen=True)
class Context:
    '''
    Stores the game context.
    '''
    window: PyGame_Window
    config: Config
    field: SoccerField
    # Sprites for players of different teams
    red_player_model: Entity
    blue_player_model: Entity