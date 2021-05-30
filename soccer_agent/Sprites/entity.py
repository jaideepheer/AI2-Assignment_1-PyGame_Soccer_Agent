from functools import cached_property
import pathlib

from pygame import image
from soccer_agent.Math.geometry import Point, Rectangle
import pygame
import copy
from ..__init__ import LOG


class Entity(pygame.sprite.DirtySprite):
    def __init__(
        self,
        sprite_file: pathlib.Path,
        is_circular=False,
        bb_color: pygame.Color = pygame.Color(0, 255, 255),
        has_alpha=False,
    ) -> None:
        super().__init__()
        # Set paramaters
        self.LOG = LOG.bind(tag='Entity')
        self.is_circular = is_circular
        self._render_bb = False
        self._bb_color = bb_color
        # Load sprite and set attributes
        # See: https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite
        # See image.setter below
        image = pygame.image.load(sprite_file)
        if has_alpha:
            self.image = image.convert_alpha()
        else:
            self.image = image.convert()

    def copy(self) -> 'Entity':
        # make shallow copy
        cp = copy.copy(self)
        # change independent params
        cp.rect = cp.rect.copy()
        cp._bb_color = copy.deepcopy(cp._bb_color)
        return cp
    # def __copy__(self) -> 'Entity':
    #     return self.copy()

    def scale(self, scaling: float) -> 'Entity':
        '''
        Scales the image according to scaling value.
        Retruns self
        '''
        rect = Rectangle.from_pygame(self.rect)
        self.image = pygame.transform.scale(
            self.image, (*(rect.size * scaling).round(),))
        return self

    @property
    def bb_color(self):
        return self._bb_color

    @bb_color.setter
    def bb_color(self, value):
        if (value != self._bb_color) and ('_image_bb' in self.__dict__):
            # Update bb color
            del self.__dict__['_image_bb']
        self._bb_color = value

    @property
    def render_bb(self):
        return self._render_bb

    @render_bb.setter
    def render_bb(self, value):
        self.dirty = self._render_bb != value
        self._render_bb = value

    @cached_property
    def _image_bb(self):
        '''
        Returns the image with bounding box applied.
        '''
        self.LOG.debug('Generating <r>bb</> image...')
        im = self._image.copy()
        if self.is_circular:
            pygame.draw.circle(surface=im, color=self.bb_color,
                               center=im.get_rect().center, radius=self.radius, width=1)
        else:
            pygame.draw.rect(im, self.bb_color, im.get_rect(), width=1)
        self.LOG.debug('<g>bb</> image ready.')
        return im

    @property
    def image(self):
        '''
        Returns either a clean sprite or one with bb.
        See: https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite
        '''
        if self.render_bb:
            return self._image_bb
        else:
            return self._image

    @image.setter
    def image(self, value):
        self._image = value
        if '_image_bb' in self.__dict__:
            del self.__dict__['_image_bb']
        # Resize rect
        self.rect = self._image.get_rect()
        # Set radius if circular
        if self.is_circular:
            self.radius = self.rect.width/2
            LOG.debug(f'Circular entity radius set to: <y>{self.radius}</>')
