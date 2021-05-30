from abc import ABC, abstractmethod
from dataclasses import dataclass

import pygame
from soccer_agent.Sprites.field import SoccerField
from typing import List
from soccer_agent.Math.geometry import Line, Point, Rectangle
from soccer_agent.Sprites.player import Player, Team
import random
from .__init__ import LOG


@dataclass
class Environment:
    '''
    Rpresents the environment that this policy works in.
    '''
    red_players: List[Player]
    blue_players: List[Player]
    kick_team: Team
    field: SoccerField
    kicker: Player = None


class Policy(ABC):
    '''
    Abstract class that must be implemented.
    Defines the behaviour of the system as a whole.
    '''
    @abstractmethod
    def relocate_players(self, environment: Environment) -> Environment:
        '''
        Given a list of current players, this should relocate every player to a new position.
        Returns the updated environment.
        '''
        pass

    @abstractmethod
    def goal_path(self, environment: Environment, top_k: int) -> List[Player]:
        '''
        Returns the top k goal paths in descending order.
        Returns a list of (color, List[(x,y)]) paths.
        '''
        pass


class BasicPolicy(Policy):
    '''
    Represents a policy that has access to everything in the environment.
    '''

    def __init__(self):
        super().__init__()

    def relocate_players(self, environment: Environment) -> Environment:
        '''
        Relocates all players based on the following conditions,
            - 'kicker' stays in the 'center_circle'
            - Exactly 1 player from each team is in 'target_goal_box'
            - Remaining players are in the 'target_field_half'
        '''
        env = environment
        red = env.red_players.copy()
        blu = env.blue_players.copy()
        # Place kicker in center circle
        kicker = red.pop() if env.kick_team == Team.RED else blu.pop()
        env.kicker = kicker
        pl_width = kicker.rect.width
        pl_height = kicker.rect.height
        center = env.field.bb_center.center
        kicker.rect.x = round(center[0]-pl_width/2)
        kicker.rect.y = center[1]
        kicker.dirty = True
        # Place players in target goal box
        small_box = env.field.bb_upper_small.to_pygame()
        x = random.sample(range(small_box.left, small_box.right-pl_width), k=2)
        y = random.sample(
            range(small_box.top, small_box.bottom-pl_height), k=2)
        for i, p in enumerate([red.pop(), blu.pop()]):
            p.rect.x = x[i]
            p.rect.y = y[i]
            p.dirty = True
        # Place the remaining players
        outter_boxes = env.field.bb_upper.substract(env.field.bb_upper_small)
        bx = outter_boxes[0].to_pygame()
        plrs = red + blu
        x = random.sample(range(bx.left, bx.right-pl_width), k=len(plrs))
        y = random.sample(range(bx.top, bx.bottom-max(pl_height,
                          round(env.field.bb_center.height/2))), k=len(plrs))
        for i, pl in enumerate(plrs):
            pl.rect.x = round(x[i]-pl_width/2)
            pl.rect.y = round(y[i]-pl_height/2)
            pl.dirty = True
        return env

    def goal_path(self,
                  environment: Environment,
                  top_path_colors: List[pygame.Color] = [
                      pygame.Color(219, 42, 54),
                      pygame.Color(232, 232, 37)
                  ]
                  ):
        '''
        Returns the top len(top_path_colors) goal paths in descending order.
        '''
        env = environment
        # Get kicker team
        team = env.red_players.copy() if env.kick_team == Team.RED else env.blue_players.copy()
        player_pos = [Point(*x.rect.center) for x in team]
        collide_pos = [Point(*x.rect.center)
                       for x in (env.red_players+env.blue_players)]
        pl_radius = env.kicker.radius
        goal = Point(*env.field.bb_upper_goal.to_pygame().center)
        paths = []
        trace = []

        def check_collide_connect(p1: Point, p2: Point):
            '''
            Checks if 2 points can be connected without collision with any other players.
            '''
            l = Line(p1, p2)
            for p in collide_pos:
                if p != p1 and p != p2:
                    d = l.dist_of_point(p)
                    ray_rect = Rectangle.enclosing_points([p1, p2])
                    ray_rect.top_left -= pl_radius
                    ray_rect.bottom_right += pl_radius
                    if d <= pl_radius and ray_rect.contains_point(p):
                        LOG.debug(f'{l} colides with {p} for distance {d}.')
                        return False
            return True

        def explore(pos):
            trace.append(pos)
            # Check if this position can goal
            if check_collide_connect(pos, goal):
                # This position can goal
                paths.append(trace+[goal])
            # get neighbours
            for p in player_pos:
                if not(p in trace) and check_collide_connect(pos, p):
                    explore(p)
            # remove from trace
            trace.pop()
            return paths
        tmp = Point(*env.kicker.rect.center)
        explore(tmp)

        # sort path lengths
        def path_length(p):
            s = p[0]
            d = 0
            for x in p[1:]:
                d += (x-s).magnitude
                s = x
            return d

        LOG.debug(f'Paths found: {len(paths)}')

        paths = [p for p in paths if len(p) > 2]
        paths = sorted(paths, key=lambda p: path_length(p))
        return [
            (top_path_colors[i], [(x.x, x.y) for x in p], path_length(p)) for i, p in enumerate(paths[:len(top_path_colors)])
        ]
