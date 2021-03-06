# coding: utf-8
from pianette.utils import Debug
from pianette.PianetteCmd import PianetteCmd
import random

FORWARDING_DIRECTION = None
SELECTED_CHARACTER = None

def select_character(*args, **kwargs):
    global SELECTED_CHARACTER
    global FORWARDING_DIRECTION

    cmd = kwargs['cmd']
    config = kwargs['config']
    player_config = kwargs['player_config']

    try:
        character = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a character or pass {random}")
        return

    if (character == "{random}"):
        # Select a random character in supported-characters
        character = random.choice(config.get('supported-characters'))
    elif not character in config.get('supported-characters'):
        Debug.println("WARNING", "This character is not supported")
        return

    Debug.println("NOTICE", "Choosing character %s" % character)
    # Process list of commands to obtain this character
    cmd.onecmd("console.play %s ✕" % player_config.get("Positions").get(character))

    SELECTED_CHARACTER = character
    # When selecting a character, we revert to its default forwarding direction
    FORWARDING_DIRECTION = player_config.get('default-character-forwarding')
    
    reapply_character_mappings(cmd, config, player_config)

def flip(*args, **kwargs):
    global FORWARDING_DIRECTION
    FORWARDING_DIRECTION = PianetteCmd.revert_direction(FORWARDING_DIRECTION)

    cmd = kwargs['cmd']
    config = kwargs['config']
    player_config = kwargs['player_config']

    reapply_character_mappings(cmd, config, player_config)

def reapply_character_mappings(cmd, config, player_config):
    global FORWARDING_DIRECTION
    global SELECTED_CHARACTER

    if SELECTED_CHARACTER is None:
        Debug.println("FAIL", "You must select a character first")
        return

    if FORWARDING_DIRECTION is None:
        FORWARDING_DIRECTION = player_config.get('default-character-forwarding')
        
    # Get all the config
    game_mappings = config.get("Mappings")
    player_mappings = player_config.get("Mappings")
    character_mappings = game_mappings.get(SELECTED_CHARACTER)

    Debug.println("NOTICE", "Applying forwarding direction: %s" % FORWARDING_DIRECTION)
    forwarded_character_mappings = { n: PianetteCmd.unpack_console_args_string(c, FORWARDING_DIRECTION)
                                     for n, c in character_mappings.items() }

    # Merge the three dictionaries of keys
    full_mappings = dict(game_mappings, **player_mappings)
    full_mappings.update(forwarded_character_mappings)

    # Re-init the mappings following the character change
    cmd.pianette.init_mappings(full_mappings)

def select_mode(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        mode = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a mode (Versus or Arcade)")
        return

    if mode == "Versus":
        cmd.onecmd("console.play → ✕")
    else: 
        cmd.onecmd("console.play ✕")

def select_fighting_handicap(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        handicap = args[0][0]
    except IndexError:
        Debug.println("WARNING", "You must define a handicap (between ▶ and ▶▶▶▶▶▶▶▶)")
        return
    
    cmd.onecmd("console.play ← ; ← ; ← ; ← ; ← ; ← ; ← ; ← ; " + ((max(1, min(8, len(handicap))) - 1) * "→ ; ") + "✕")

def select_fighting_style(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        style = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a style (A-ISM, X-ISM or V-ISM)")
        return

    if style == "V-ISM":
        cmd.onecmd("console.play ↓")
    elif style == "X-ISM":
        cmd.onecmd("console.play ↑")
    elif style == "A-ISM":
        pass
    else:
        Debug.println("WARNING", "%s is not an available fighting style" % style)
        return

    cmd.onecmd("console.play ✕")

def select_stage(*args, **kwargs):
    cmd = kwargs['cmd']
    config = kwargs['config']
    try:
        stage = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a stage")
        return

    if (stage == "{random}"):
        # Select a random stage in supported-stages
        stage = random.choice(config.get('supported-stages'))
    elif not stage in config.get('supported-stages'):
        Debug.println("WARNING", "This stage is not supported")
        return

    Debug.println("NOTICE", "Choosing stage '%s'" % stage)

    cmd.onecmd("console.play %s ; ✕" % config.get("Stages").get(stage))
