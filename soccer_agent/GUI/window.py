from asyncio.events import AbstractEventLoop
from typing import Callable

from pygame.constants import VIDEORESIZE
from soccer_agent.IO.pygame_io import KeybindHost
import pygame
import asyncio
from ..__init__ import LOG

from pygame.locals import (
    QUIT,
)


class PyGame_Dependent:
    '''
    This mixin ensures pygame is initialized and ready for use.
    '''

    def __init__(self,) -> None:
        # Init. pygame
        super().__init__()
        LOG.info(f'Initializing <r>pygame</>...')
        pygame.init()
        LOG.info("<g>pygame</> initialized.")


class PyGame_Window(PyGame_Dependent, KeybindHost):
    '''
    This mixin creates and manages a PyGame window.
    '''

    def __init__(
        self,
        title: str,
        width: int,
        height: int,
        tick_rate: int = 20,
        event_loop: AbstractEventLoop = asyncio.get_event_loop()
    ):
        super().__init__()
        # create a window
        self.title = title
        self.window = pygame.display.set_mode([width, height])
        self.tick_rate = tick_rate
        self.tick_clock = pygame.time.Clock()
        self.tick_listeners = {
            'tick_start': [],
            'tick_end': [],
        }
        pygame.display.set_caption(title)
        # init. data structures
        # run async window event loop
        event_loop.create_task(self.event_loop())

    def register_tick_listener(self, listener: Callable[['PyGame_Window'], None], stage='tick_end'):
        '''
        Register a function that recieves this class and is call at a certain stage every tick.
        Allowed stages:
            - tick_start
            - tick_end 
        
        Returns: A callback to delete this listener.
        '''
        if not (stage in ('tick_start', 'tick_end',)):
            raise Exception(f'Invalid argument `{stage}` passed for stage in register tick listener.')
        def remove(x=listener):
            del x
        self.tick_listeners[stage].append(listener)
        return remove

    async def event_loop(self, ):
        '''
        The asynchronous event loop for this window.
        '''
        with LOG.contextualize(tag=self.title):
            self.running = True
            while self.running:
                # tick listeners
                for l in self.tick_listeners['tick_start']:
                    l(self)
                # Process events
                events = pygame.event.get()
                for event in events:
                    # Handle keybinds
                    self.handle_key_event(event)
                    # Handle window events
                    if event.type == QUIT:
                        LOG.info('<r>Quit</> signal recieved, closing window.')
                        self.running = False
                    elif event.type == VIDEORESIZE:
                        LOG.info('<y>Resize</> signal recieved, resizing window.')
                        pygame.display._resize_event(event)
                # tick listeners
                for l in self.tick_listeners['tick_end']:
                    l(self)
                # Update the display
                pygame.display.flip()
                # wait for next game tick
                self.tick_clock.tick(self.tick_rate)
            pygame.display.quit()
