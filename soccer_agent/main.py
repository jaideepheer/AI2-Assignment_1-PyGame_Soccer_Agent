# Common imports
import pathlib
from soccer_agent.policy import BasicPolicy, Policy
from soccer_agent.Sprites.player import Player, Team
from soccer_agent.simulation import Simulator
from soccer_agent.Config.config import Config, Context
from soccer_agent.Sprites.field import SoccerField
import pygame
from soccer_agent.IO.pygame_io import KeybindAction_Callable, KeybindKey
from soccer_agent.GUI.window import PyGame_Window
from .__init__ import LOG, LogTag
import asyncio


def setup_logger():
    import sys
    formats = {
        'time': '<green>{time:YYYY-MM-DD hh:mm:ss.SSS A}</green>',
        'level': '<level>{level: <8}</level>',
        'code_path': '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>'
    }
    # Remove default logger
    LOG.remove()
    # Update default logger
    default = LOG.add(
        sys.stderr,
        format=formats['time']+' | '+formats['level']+' | ' +
        formats['code_path']+' - <level>{message}</level>',
        filter=lambda record: not ("tag" in record["extra"]),
        colorize=True,
    )
    tagged = LOG.add(
        sys.stderr,
        format=formats['time']+' | '+formats['level'] +
        ' | <cyan>{extra[tag]}</cyan> - <level>{message}</level>',
        filter=lambda record: "tag" in record["extra"],
        colorize=True,
    )


def register_keybinds(context: Context, simulator: Simulator, policy: Policy):
    # Exit keybind
    def ext():
        context.window.running = False
    context.window.register_action(
        'exit', KeybindAction_Callable(callable=ext, description='Exit.'))
    context.window.register_keybind(
        KeybindKey(key_code=pygame.K_ESCAPE), 'exit')
    # Bounding box keybind

    def field_bb_toggle():
        simulator.render_bb = not simulator.render_bb
    context.window.register_action('toggle_field_bb', KeybindAction_Callable(
        callable=field_bb_toggle, description='Toggle field bounding boxes.'))
    context.window.register_keybind(KeybindKey(
        key_code=pygame.K_b), 'toggle_field_bb')
    # Policy keybind

    def relocate_players():
        simulator.environment = policy.relocate_players(
            environment=simulator.environment)
        simulator.goal_paths = policy.goal_path(
            simulator.environment, top_path_colors=context.config.top_path_colors)
    context.window.register_action('relocate_players', KeybindAction_Callable(
        callable=relocate_players, description='Relocate all players.'))
    context.window.register_keybind(KeybindKey(
        key_code=pygame.K_x), 'relocate_players')


@LOG.catch
@LogTag(tag='Main')
def main():
    '''
    This is the entry point for this module.
    It is imported as `main` in init.py
    '''
    setup_logger()
    # Create config
    config = Config(
        field_bb_color=pygame.Color(255, 0, 0),
        player_bb_color=pygame.Color(255, 0, 255),
        top_path_colors=[
            pygame.Color(255, 0, 0),
            pygame.Color(0, 255, 0),
            pygame.Color(0, 0, 255),
            pygame.Color(0, 0, 0),
        ]
    )
    LOG.info(f'Config set: <y>{config}</>')
    # crete window
    LOG.info('Creating game window...')
    window = PyGame_Window('Game Window', 300, 300)
    LOG.info(f'Game window created.')
    # Add field
    LOG.info(f'Creating field...')
    field = SoccerField(
        bb_color=config.field_bb_color,
    )
    # LOG.info(f'Attaching <r>field</> to window.')
    # field.attach_to(window)
    # LOG.info('<g>Field</> attached to window.')
    # Crete context
    context = Context(
        window=window,
        field=field,
        red_player_model=Player(pathlib.Path(
            __file__).parent / './assets/red.png').scale(0.5),
        blue_player_model=Player(pathlib.Path(
            __file__).parent / './assets/blue.png').scale(0.5),
        config=config
    )
    # Create simulator
    simulator = Simulator(
        context=context,
        player_counts={
            Team.RED: 3,
            Team.BLUE: 4,
        },
        kick_team=Team.BLUE
    )
    # Create policy
    policy = BasicPolicy()
    # Register keybinds
    register_keybinds(context, simulator, policy)
    # Await all running tasks to end
    loop = asyncio.get_event_loop()
    tasks = asyncio.all_tasks(loop)
    LOG.info('Game running, waiting for quit...')
    loop.run_until_complete(asyncio.gather(*tasks))
