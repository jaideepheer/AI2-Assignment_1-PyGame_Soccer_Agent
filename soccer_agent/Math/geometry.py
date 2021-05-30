from dataclasses import dataclass
from functools import cached_property
from math import sqrt
from typing import List, Union
from numbers import Number
from ..__init__ import LOG

import pygame


@dataclass(frozen=True, eq=True, repr=True)
class Point:
    x: Number
    y: Number

    @cached_property
    def magnitude(self) -> float:
        '''
        Returns the L2 norm of this point.
        '''
        return sqrt(self.x**2 + self.y**2)

    def round(self) -> 'Point':
        '''
        Returns a new point with x and y values rounded to nearest integers.
        '''
        return Point(
            round(self.x),
            round(self.y)
        )

    def abs(self) -> 'Point':
        '''
        Returns a new point containing absolute values of x and y.
        '''
        return Point(abs(self.x), abs(self.y))

    def __getitem__(self, key):
        '''
        Defined to iterate x, y.
        '''
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError(f"Invalid key '{key}' to iterate over Point.")

    def __neg__(self,):
        return Point(-self.x, -self.y)

    def __add__(self, other: Union['Point', Number]):
        if isinstance(other, Number):
            return Point(self.x+other, self.y+other)
        elif isinstance(other, Point):
            return Point(x=self.x+other.x, y=self.y+other.y)
        else:
            raise Exception(
                f'Operator __add__ not defined for "Point" and "{type(other)}".')

    def __sub__(self, other: Union['Point', Number]):
        if isinstance(other, Number):
            return Point(self.x-other, self.y-other)
        elif isinstance(other, Point):
            return Point(x=self.x-other.x, y=self.y-other.y)
        else:
            raise Exception(
                f'Operator __sub__ not defined for "Point" and "{type(other)}".')

    def __mul__(self, other: Union['Point', Number]):
        if isinstance(other, Number):
            return Point(self.x*other, self.y*other)
        elif isinstance(other, Point):
            return Point(x=self.x*other.x, y=self.y*other.y)
        else:
            raise Exception(
                f'Operator __mul__ not defined for "Point" and "{type(other)}".')

    def __truediv__(self, other: Union['Point', Number]):
        if isinstance(other, Number):
            return Point(self.x/other, self.y/other)
        elif isinstance(other, Point):
            return Point(x=self.x/other.x, y=self.y/other.y)
        else:
            raise Exception(
                f'Operator __truediv__ not defined for "Point" and "{type(other)}".')

    def __floordiv__(self, other: Union['Point', Number]):
        if isinstance(other, Number):
            return Point(self.x//other, self.y//other)
        elif isinstance(other, Point):
            return Point(x=self.x//other.x, y=self.y//other.y)
        else:
            raise Exception(
                f'Operator __floordiv__ not defined for "Point" and "{type(other)}".')


@dataclass(frozen=True, eq=True, repr=True)
class Line:
    start: Point
    end: Point

    @cached_property
    def slope(self) -> float:
        '''
        Returns the slope of this line.
        '''
        tmp = self.end - self.start
        return tmp.y / tmp.x

    @cached_property
    def length(self) -> float:
        '''
        Returns the euclidean length of this line.
        '''
        return (self.end - self.start).magnitude

    def points_on_same_side(self, p1: Point, p2: Point) -> bool:
        '''
        Returns True if the given points are on the same side of this line.
        '''
        v1 = self.slope * p1.x - p1.y
        v2 = self.slope * p2.x - p2.y
        return (v1 > 0 and v2 > 0) or (v1 < 0 and v2 < 0)

    def dist_of_point(self, point: Point):
        d = self.end - self.start
        l = self.start - point
        return abs((d.x*l.y - l.x*d.y)/d.magnitude)


@dataclass(eq=True, repr=True)
class Rectangle:
    top_left: Point
    bottom_right: Point

    def to_pygame(self,):
        '''
        Converts to pygame rect.
        '''
        sz = self.bottom_right-self.top_left
        return pygame.Rect(*self.top_left, *sz)

    def copy(self,):
        # No need to deepcopy since points are frozen
        return Rectangle(self.top_left, self.bottom_right)
    
    @staticmethod
    def enclosing_points(points: List[Point]):
        p = points[0]
        lt = rt = p.x
        tp = bt = p.y
        for p in points:
            lt = min(p.x, lt)
            rt = max(p.x, rt)
            bt = max(p.y, bt)
            tp = min(p.y, tp)
        return Rectangle(
            Point(lt, tp),
            Point(rt, bt)
        )

    @staticmethod
    def from_pygame(rect: pygame.Rect):
        tl = Point(rect.left, rect.top)
        br = Point(rect.right, rect.bottom)
        return Rectangle(tl, br)

    @property
    def size(self) -> Point:
        '''
        Returns a point representing (width, height).
        '''
        return (self.bottom_right - self.top_left).abs()

    @property
    def area(self,):
        sz = self.size
        return sz.x * sz.y

    @property
    def center(self,):
        sz = self.bottom_right - self.top_left
        return self.top_left + (sz/2)

    @property
    def left(self):
        return self.top_left.x

    @property
    def right(self):
        return self.top_left.x+self.bottom_right.x

    @property
    def top(self):
        return self.top_left.y

    @property
    def bottom(self):
        return self.bottom_right.y

    @property
    def height(self):
        return self.size.y

    @property
    def width(self):
        return self.size.x
    
    def contains_point(self, point: Point):
        l = point - self.top_left
        q = self.bottom_right - point
        return l.x>=0 and l.y>=0 and q.x>=0 and q.y>=0

    def intersect(self, other: 'Rectangle'):
        '''
        Retruns a new rectangle that forms the intersection between these rectangles.
        If no intersection exists, returns None.
        '''
        r = Rectangle(
            Point(
                max(self.left, other.left),
                max(self.top, other.top)
            ),
            Point(
                min(self.right, other.right),
                min(self.bottom, other.bottom)
            )
        )
        return r if r.area > 0 else None

    def substract(self, other: 'Rectangle'):
        '''
        Substract another rectangle from this rectangle.
        Returns a list of ractangles.
        '''
        # Ensure other lies inside self
        other = self.intersect(other)
        if other == None:
            # No intersection
            return self.copy()
        tp = Rectangle(
            self.top_left,
            Point(other.right, other.top)
        )
        bt = Rectangle(
            Point(self.left, other.bottom),
            self.bottom_right
        )
        lt = Rectangle(
            Point(self.left, other.top),
            Point(other.left, other.bottom)
        )
        rt = Rectangle(
            Point(other.right, other.top),
            Point(self.right, other.bottom)
        )
        return [x for x in (tp, bt, lt, rt,) if x.area > 0]

    def translate(self, dist: Point):
        if not isinstance(dist, Point):
            raise Exception(
                f'Cannot traslate using translation of type \'{type(dist)}\'')
        self.top_left += dist
        self.bottom_right += dist
        return self

    def scale(self, scale: Union[Number, Point], anchor: Point = None):
        '''
        Scales the rect with respect to anchor.
        If anchor is None, will scale with respect to top_left by default.
        '''
        if anchor == None:
            anchor = self.top_left
            LOG.debug(
                f'<y>Scale</> called without anchor, using anchor: <y>{anchor}</>', tag='Rectangle')
        LOG.debug(
            f'<y>Scale</> called with anchor: <y>{anchor}</>', tag='Rectangle')
        # translate
        self.translate(-anchor)
        # scale
        self.top_left *= scale
        self.bottom_right *= scale
        # revert
        self.translate(anchor)
        return self

    def __getitem__(self, key):
        '''
        Defined to iterate top_left, bottom_right.
        '''
        if key == 0:
            return self.top_left
        elif key == 1:
            return self.bottom_right
        else:
            raise IndexError(f"Invalid key '{key}' to iterate over Rectangle.")
