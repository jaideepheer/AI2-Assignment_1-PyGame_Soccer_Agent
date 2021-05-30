from functools import cached_property
from soccer_agent.Sprites.entity import Entity
from soccer_agent.Math.geometry import Point, Rectangle
from pygame.constants import RLEACCEL
from soccer_agent.GUI.window import PyGame_Window
import pygame
import pathlib
from ..__init__ import LOG


class SoccerField(Entity):
    def __init__(
        self,
        background_image=pathlib.Path(__file__).parent / '../assets/field.png',
        bb_color: pygame.Color = pygame.Color(0, 255, 255),
        # *args, **kwargs
    ) -> None:
        super().__init__(sprite_file=background_image, is_circular=False, bb_color=bb_color)
        self.LOG = LOG.bind(tag='SoccerField')
        self.LOG.info(
            f'Loading <r>field</> image file: <y>{background_image}</>')
        # self.surface = pygame.image.load(background_image).convert()
        # self._image.set_colorkey((255, 255, 255), RLEACCEL)
        self.LOG.info(f'<g>Field</> image loaded.')
        self.LOG.info(f'Splitting <r>field</> sections...')
        # List of bounding boxes
        self.bb_list = []
        self._set_bounding_boxes()
        self.LOG.info(f'<g>Field</> loaded and ready.')

    def _set_bounding_boxes(self,):
        '''
        After loading the image, this sets the bounding boxes for various places on the field.
        '''
        # A rectangular bb for the center circle
        centre_radius = 30
        center = Point(*self.rect.center)
        field_rect = Rectangle.from_pygame(self.rect)
        self.LOG.debug(f'Field centre point: <y>{center}</>')
        bb_center = Rectangle(center-centre_radius,
                              center+centre_radius).translate(Point(4.4, 0))
        self.bb_center = bb_center
        # bb for upper half
        bb_upper = field_rect.copy().scale(Point(1, 0.5))
        bb_upper = bb_upper.scale(Point(0.91, 1), anchor=bb_upper.center)
        bb_upper.top_left = bb_upper.top_left + Point(4, 34)
        self.bb_upper = bb_upper
        # bb for upper small
        bb_upper_small = bb_upper.copy().scale(
            Point(0.74, 0.44)).translate(Point(59, 0))
        self.bb_upper_small = bb_upper_small
        # bb for upper goal
        bb_upper_goal = field_rect.copy().scale(
            Point(0.17, 0.045), anchor=Point(center.x, 0)).translate(Point(5, 0))
        self.bb_upper_goal = bb_upper_goal
        # bb for lower half
        bb_lower = bb_upper.copy().translate(Point(0, center.y - 35))
        self.bb_lower = bb_lower
        # Add bb to list
        self.bb_list.extend([
            self.bb_upper,
            self.bb_upper_small,
            self.bb_center,
            self.bb_lower,
            self.bb_upper_goal,
            # self.bb_lower_small,
        ])

    @cached_property
    def _image_bb(self):
        '''
        Returns the image with bounding box applied.
        Overrides Entity._image_bb
        '''
        im = super()._image_bb
        self.LOG.debug('Generating field sections <r>bb</>...')
        # Render bb
        for bb in self.bb_list:
            pygame.draw.rect(im, self.bb_color, bb.to_pygame(), width=1)
        self.LOG.debug('Field sections <g>bb</> ready.')
        return im

    # def on_window_tick(self, window: PyGame_Window):
    #     '''
    #     Is called by the attached window on tick_start.
    #     '''
    #     if self.dirty:
    #         self.dirty = 0
    #         # Set background to white
    #         window.window.fill((255, 255, 255))
    #         # Set image to window
    #         window.window.blit(self.image, (0, 0))
    # 
    # def attach_to(self, window: PyGame_Window):
    #     '''
    #     Attaches to a given PyGameWindow.
    #     '''
    #     # Unbind from previously attached window.
    #     self.unbind()
    #     self._unbind = window.register_tick_listener(self.on_window_tick)
    #     # Rescale window
    #     window.window = pygame.display.set_mode(
    #         [self.rect.width, self.rect.height], flags=pygame.SCALED)
    # 
    # def unbind(self,):
    #     if hasattr(self, '_unbind'):
    #         self._unbind()
