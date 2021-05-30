from abc import ABC, abstractmethod
from typing import Callable, Optional
from dataclasses import dataclass, field
from ..__init__ import LOG
import pygame
import asyncio


class KeybindAction(ABC):
    '''
    This defines an action to perform when a specific keybind is pressed.
    Extend this class to implement the `run()` function which is automatically called.
    Init. args:
        - description [str]: A description of this action.
        - is_async [bool]: If True, the action is performed using asyncio.create_task.
        - event_loop [asyncio.AbstractEventLoop]: If provided, uses this loop.
    '''

    def __init__(
        self,
        is_async=False,
        event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    ):
        self.is_async = is_async
        self.loop = event_loop

    @property
    @abstractmethod
    def description(self,) -> str:
        '''
        Provides the string description for this action.
        '''
        pass

    @abstractmethod
    def run(self,):
        raise NotImplementedError()

    def _perform(self):
        if self.is_async:
            self.loop.run_in_executor(None, self.run)
        else:
            self.run()


class KeybindAction_Callable(KeybindAction):
    '''
    This defines an action to perform when a specific keybind is pressed.
    Extend this class to implement the `run()` function which is automatically called.
    Init. args:
        - description [str]: A description of this action.
        - is_async [bool]: If True, the action is performed using asyncio.create_task.
        - event_loop [asyncio.AbstractEventLoop]: If provided, uses this loop.
    '''

    def __init__(
        self,
        callable: Callable,
        description: str,
        is_async=False,
        event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    ):
        super().__init__(is_async=is_async, event_loop=event_loop)
        self.callable = callable
        self.desc = description

    def run(self,):
        self.callable()

    @property
    def description(self) -> str:
        return self.desc
    
    def __repr__(self) -> str:
        return f"KeybindAction_Callable(is_async={self.is_async}, description='{self.desc}')"


@dataclass(eq=True, frozen=True)
class KeybindKey:
    key_code: int
    on_keydown: bool = field(default=False)
    is_mouse: bool = field(default=False)

    @staticmethod
    def from_pyGame_event(event: pygame.event.Event) -> Optional['KeybindKey']:
        '''
        Converts a pygame event to a keybind key if possible.
        '''
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, pygame.KEYUP):
            # Event not a key event
            return None
        is_mouse = event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)
        on_down = event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN)
        mod = event.mod if not is_mouse else pygame.KMOD_NONE
        code = event.button if is_mouse else event.key
        return KeybindKey(key_code=code, on_keydown=on_down, is_mouse=is_mouse)

    def is_active(self, event: pygame.event.Event):
        '''
        Returns true if the keybind is active in the given event.
        '''
        bind = KeybindKey.from_pyGame_event(event=event)
        return bind != None and self == bind


class KeybindHost:
    '''
    Mixin to handle configurable keybinds and I/O.
    '''

    def __init__(self, log_name='KeybindHost'):
        super().__init__()
        self.actions = dict()
        self.bindings = dict()
        self.LOG = LOG.bind(tag=log_name)

    def handle_key_event(self, event: pygame.event.Event):
        keybind = KeybindKey.from_pyGame_event(event)
        if keybind != None and keybind in self.bindings:
            # Call binded action
            action_key = self.bindings[keybind]
            action = self.actions[action_key]
            self.LOG.debug(f'Executing keybind action <r>"{action_key}"</> for: "<y>{keybind}</>".')
            action._perform()

    def register_keybind(self, key: KeybindKey, action_key: str):
        '''
        Registers a key to an action.
        If the `action_key` is not registered with any action then this raises error.
        '''
        if not action_key in self.actions:
            raise Exception(
                f'Invalid action key `{action_key}` provided to register keybind function.')
        self.bindings[key] = action_key
        self.LOG.info(
            f'Registered keybind "<y>{key}</>" for action "<r>{action_key}</>".')

    def register_action(self, action_key: str, action: KeybindAction):
        '''
        Registers the given action under the given unique `key`.
        Replaces a previous action if the key already exits.
        '''
        self.actions[action_key] = action
        self.LOG.info(f'Registered action "<r>{action_key}</>": <g>{action.description}</>.')
