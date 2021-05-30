from dataclasses import dataclass
from typing import Mapping
from soccer_agent.Sprites.player import Team
from soccer_agent.policy import Environment
from soccer_agent.Math.geometry import Point, Rectangle
from soccer_agent.GUI.window import PyGame_Window

import pygame
from .__init__ import LOG

from soccer_agent.Config.config import Context


@dataclass(repr=True)
class Simulator:
    '''
    Handles simulating the core logic of the program.
    '''
    context: Context
    # No. of players per team
    player_counts: Mapping[Team, int]
    # The kicking team
    kick_team: Team
    # Properties
    _render_bb: bool = False

    def __post_init__(self):
        self.LOG = LOG.bind(tag='Simulator')
        self.LOG.info(
            f'Initialized with player counts: {self.player_counts}')
        # Register self with window
        self.LOG.info(f'Attaching to window: {self.context.window}')
        self._unbind = self.context.window.register_tick_listener(self._render)
        self.LOG.info(f'Attaching <g>complete</>.')
        # Resize window and set background
        self.LOG.info(f'Resizing window to fit field...')
        self.context.window.window = pygame.display.set_mode(
            [self.context.field.rect.width, self.context.field.rect.height], flags=pygame.SCALED)
        self.LOG.info(f'Resize <g>complete</>.')
        # Setup render and other groups
        self.render_group = pygame.sprite.LayeredDirty(self.context.field)
        self.red_group = pygame.sprite.Group()
        self.blue_group = pygame.sprite.Group()
        # Add player sprites
        self.LOG.info(f'Setting up player sprites...')
        red_team = [None]*self.player_counts[Team.RED]
        blu_team = [None]*self.player_counts[Team.BLUE]
        for i in range(self.player_counts[Team.RED]):
            md = self.context.red_player_model.copy()
            self.render_group.add(md, layer=10)
            self.red_group.add(md)
            red_team[i] = md
        for i in range(self.player_counts[Team.BLUE]):
            md = self.context.blue_player_model.copy()
            self.render_group.add(md, layer=10)
            self.blue_group.add(md)
            blu_team[i] = md
        self.LOG.info(f'Player sprites setup <g>complete</>.')
        # Setup environment
        self.environment = Environment(
            red_players=red_team,
            blue_players=blu_team,
            kick_team=self.kick_team,
            field=self.context.field
        )
        # Store goal path
        self._goal_paths = []
        self._goal_path_dirty = False
        # Init. text labels
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.texts = {
            'no_path': self.font.render('No path found...!', True, (255, 255, 255)),
            'top_paths': self.font.render('Best paths:', True, (255, 255, 255)),
        }

    @property
    def goal_paths(self):
        return self._goal_paths

    @goal_paths.setter
    def goal_paths(self, value):
        self._goal_path_dirty = True
        self._goal_paths = value

    @property
    def render_bb(self):
        return self._render_bb

    @render_bb.setter
    def render_bb(self, value):
        self._render_bb = value
        # update values for all sprites
        for e in self.render_group:
            e.render_bb = value

    @staticmethod
    def _get_rect_random_loc(rect: Rectangle, num_points: int = 1):
        '''
        Returns multiple random points within the given rectangle.
        '''
        pass

    def relocate_players(self):
        self.LOG.info(f'Relocating players...')
        # First blue player is kicker
        self.LOG.info(f'Players <g>relocated</>.')
        pass

    def _render(self, window: PyGame_Window):
        '''
        Renders everything on screen.
        '''
        if self._goal_path_dirty == True:
            self.render_group.repaint_rect(self.context.field.rect)
            self._goal_path_dirty = False
        self.render_group.draw(window.window)
        for color, path, path_len in reversed(self.goal_paths):
            # Render goal paths
            pygame.draw.aalines(window.window, color,
                                closed=False, points=path)
        # Render path length text
        render_rect = self.context.field.bb_lower.copy()
        render_rect.top_left += Point(10,
                                      self.context.field.bb_center.height*1.3)
        if len(self.goal_paths) > 0:
            lbl_rect = Rectangle.from_pygame(
                self.texts['top_paths'].get_rect())
            lbl_rect.top_left = render_rect.top_left
            window.window.blit(self.texts['top_paths'], lbl_rect.to_pygame())
            # Render best path values
            for i, data in enumerate(self.goal_paths):
                color, _, path_len = data
                tx = self.font.render(f'{path_len:.2f}', True, color)
                rect = Rectangle.from_pygame(tx.get_rect())
                rect.top_left = Point(
                    lbl_rect.right + 10, lbl_rect.top + i*(rect.height+10))
                window.window.blit(tx, rect.to_pygame())
        else:
            rect = Rectangle.from_pygame(self.texts['no_path'].get_rect())
            rect.top_left = render_rect.top_left
            window.window.blit(self.texts['no_path'], rect.to_pygame())

    def __del__(self):
        # unbind before delete
        self.LOG.info(f'Deleting self.')
        self.LOG.info(f'Unbinding from window.')
        self._unbind()
        self.LOG.info(f'Goodbye.')
