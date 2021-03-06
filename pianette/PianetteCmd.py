# coding: utf-8

import cmd
import pianette.errors
import random
import re
import time
import json

from pianette.utils import Debug

class PianetteCmdUtil:

    # Namespaces
    supported_cmd_namespaces = [ "console", "game", "piano", "pianette", "time" ]

    @staticmethod
    def is_supported_cmd_namespace(cmd_namespace):
        return cmd_namespace in PianetteCmdUtil.supported_cmd_namespaces


class PianetteCmd(cmd.Cmd):
    prompt = 'pianette: '
    doc_header = 'Available commands'

    def __init__(self, configobj=None, pianette=None, **kwargs):
        super().__init__(**kwargs)
        self.configobj = configobj
        self.pianette = pianette

    def parseline(self, line):
        # Pianette-specific command parser
        command, arg, line = super().parseline(line)

        if command and command != "EOF":
            command = command.lower()

        # Rewrite namespaced commands for cmd to properly map them
        # The default parser would interpret "namespace.do-stuff arg1 arg2" as the "namespace" command with arguments ".do-stuff", "arg1", "arg2"
        # What we want instead, is the "namespace__do_stuff" command with arguments "arg1", "arg2"
        # .. Except for the game namespace, where commands are dynamic, so we want to keep the ".do-stuff" as the first argument
        namespace = None

        if command and PianetteCmdUtil.is_supported_cmd_namespace(command):
            if arg and command != "game":
                arg_list = arg.split()
                if arg_list and len(arg_list[0]) > 1 and arg_list[0][0] == ".":
                    namespace = command
                    command += "__"
                    command += arg_list[0][1:].replace("-", "_")
                    arg_list.pop(0)
                    arg = " ".join(arg_list)

        if command == "game":
            # Let's sanitize the command name and keep arg a list of arguments
            arg_list = arg.split()
            if arg_list and len(arg_list[0]) > 1 and arg_list[0][0] == ".":
                arg_list[0] = arg_list[0][1:].replace("-", "_")
                arg = arg_list

        if namespace == "piano":
            # Assume that some arguments in piano commands include aliases for harder-to type characters
            arg = PianetteCmd.unpack_piano_args_string(arg)

        if namespace == "console":
            # Assume that some arguments in console commands include aliases for harder-to type characters
            arg = PianetteCmd.unpack_console_args_string(arg)

        # Insert safe spaces around "+" signs when arg is a string
        if (arg is not None and not isinstance(arg, list)):
            arg = re.sub('\s*\+\s*',' + ', arg)

        return command, arg, line

    # Overrides
    def emptyline(self):
        return

    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.stdout.write("%s\n"%str(header))
            if self.ruler:
                self.stdout.write("%s\n"%str(self.ruler * len(header)))
            self.columnize([name.replace("__", ".").replace("_","-") for name in cmds], maxcol-1)
            self.stdout.write("\n")

    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd".'
        if arg:
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + arg.replace(".", "__").replace("-","_")).__doc__
                    if doc:
                        self.stdout.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
                return
            func()
        else:
            super(PianetteCmd, self).do_help(arg)

    def completenames(self, text, *ignored):
        dotext = 'do_' + text.replace(".", "__").replace("-","_")
        return [a[3:].replace("__", ".").replace("_","-") for a in self.get_names() if a.startswith(dotext)]

    def cmdloop(self):
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt as e:
            print()
            Debug.println("NOTICE", "Exiting, bye bye!")
            self.pianette.stop_timer()
            return True

    @staticmethod
    def revert_direction(direction):
        return "←" if direction == "→" else "→"

    @staticmethod
    def unpack_aliases(aliases, string):
        return re.sub('|'.join(r'\b%s\b' % re.escape(s) for s in aliases),
                      lambda match: aliases[match.group(0)],
                      string)

    @staticmethod
    def unpack_console_args_string(args_string, forwarding_direction = None):
        args_string = args_string.replace('↖', '← + ↑')
        args_string = args_string.replace('↗', '↑ + →')
        args_string = args_string.replace('↘', '→ + ↓')
        args_string = args_string.replace('↙', '↓ + ←')

        args_string = args_string.upper()

        args_string = PianetteCmd.unpack_aliases(
            {
                'SQUARE': '□',
                'TRIANGLE': '△',
                'CROSS': '✕',
                'CIRCLE': '◯',
                'UP': '↑',
                'RIGHT': '→',
                'DOWN': '↓',
                'LEFT': '←',
            },
            args_string)

        if forwarding_direction is not None:
            # All combos are supposed to be noted
            # as player 1 (e.g., forwarding right)
            args_string = args_string.replace("→", "fw")
            args_string = args_string.replace("←", PianetteCmd.revert_direction(forwarding_direction))
            args_string = args_string.replace("fw", forwarding_direction)

        # print('Unpacked console args string: "%s"' % (args_string))
        return args_string

    @staticmethod
    def unpack_piano_args_string(args_string):
        args_string = args_string.replace("b", "♭")
        args_string = args_string.replace("#", "♯")

        args_string = args_string.upper()

        args_string = PianetteCmd.unpack_aliases(
            {
                'SUSTAIN': '𝆮',
                'A♯0': 'B♭0',
                'C♯1': 'D♭1',
                'D♯1': 'E♭1',
                'F♯1': 'G♭1',
                'G♯1': 'A♭1',
                'A♯1': 'B♭1',
                'C♯2': 'D♭2',
                'D♯2': 'E♭2',
                'F♯2': 'G♭2',
                'G♯2': 'A♭2',
                'A♯2': 'B♭2',
                'C♯3': 'D♭3',
                'D♯3': 'E♭3',
                'F♯3': 'G♭3',
                'G♯3': 'A♭3',
                'A♯3': 'B♭3',
                'C♯4': 'D♭4',
                'D♯4': 'E♭4',
                'F♯4': 'G♭4',
                'G♯4': 'A♭4',
                'A♯4': 'B♭4',
                'C♯5': 'D♭5',
                'D♯5': 'E♭5',
                'F♯5': 'G♭5',
                'G♯5': 'A♭5',
                'A♯5': 'B♭5',
                'C♯6': 'D♭6',
                'D♯6': 'E♭6',
                'F♯6': 'G♭6',
                'G♯6': 'A♭6',
                'A♯6': 'B♭6',
                'C♯7': 'D♭7',
                'D♯7': 'E♭7',
                'F♯7': 'G♭7',
                'G♯7': 'A♭7',
                'A♯7': 'B♭7',
            },
            args_string)

        # print('Unpacked piano args string: "%s"' % (args_string))
        return args_string

    # Commands
    def do_console__hit(self, args):
        'Play a sequence of buttons in a definite order for a single cycle'
        Debug.println("INFO", "running command: console.hit" + " " + args)
        self.pianette.push_console_controls(args, duration_cycles=1)

    def do_console__play(self, args):
        'Play a sequence of buttons in a definite order for a full Pianette cycle'
        Debug.println("INFO", "running command: console.play" + " " + args)
        self.pianette.push_console_controls(args)

    def do_game(self, args):
        'The `game` namespace contains all game-defined commands.'
        try:
            method = args[0]
        except IndexError:
            Debug.println("WARNING", "You must specify a command")
            return
        config = self.pianette.get_selected_game_config()
        player_config = self.pianette.get_selected_player_config()
        
        # Is there a command defined in the configuration for this method ?
        commands = player_config.get("Commands").get(method)
        if commands is not None:
            for command in commands.split("\n"):
                if command.strip():
                    self.onecmd(command)
            return

        # In this case, let's ask the game module
        module = self.pianette.get_selected_game_module()
        game = self.pianette.get_selected_game()
        try:
            # Call the relevant game method from the loaded module
            getattr(module, method)(args[1:], cmd=self, config=config, player_config=player_config)
        except AttributeError:
            # Method does not exist, gracefully fail
            Debug.println("WARNING", "Command %s (%s) does not exist for the game '%s'" % (method, args[1:], game))

    def do_pianette__disable_source(self, args):
        'Disable a previously enabled source'
        Debug.println("INFO", "running command: pianette.disable_source" + " " + args)
        self.pianette.disable_source(args)

    def do_pianette__enable_source(self, args):
        'Enable an input source'
        Debug.println("INFO", "running command: pianette.enable_source" + " " + args)
        self.pianette.enable_source(args)

    def do_pianette__select_game(self, args):
        'Select a game and load its configuration'
        Debug.println("INFO", "running command: pianette.select_game" + " " + args)
        self.pianette.select_game(args)

    def do_pianette__dump_state(self, args):
        'Dump a full state of the Pianette configuration'
        Debug.println("INFO", "running command: pianette.dump_state")

        # Dump general info on the pianette instance
        Debug.println("NOTICE", "Enabled sources: %s" % self.pianette.get_selected_player())

        # Dump general game configuration
        Debug.println("NOTICE", "Currently selected game: '%s'" % self.pianette.get_selected_game())
        Debug.println("NOTICE", "Current game config:")
        print(json.dumps(self.pianette.get_selected_game_config(), sort_keys=True, indent=4))
        
        # Dump player specific configuration for this game
        Debug.println("NOTICE", "Currently selected player: %s" % self.pianette.get_selected_player())
        Debug.println("NOTICE", "Current player config:")
        print(json.dumps(self.pianette.get_selected_player_config(), sort_keys=True, indent=4))

        # Dumps the buffered mappings
        Debug.println("NOTICE", "Current buffered mappings:")
        print(json.dumps(self.pianette.get_buffered_states_mappings(), sort_keys=True, indent=4))

    def do_piano__play(self, args):
        'Play a sequence of notes, chords and pedals'
        Debug.println("INFO", "running command: piano.play" + " " + args)
        self.pianette.push_piano_notes(args)

    def do_piano__hold(self, args):
        'Hold a sequence of notes, chords and pedals'
        Debug.println("INFO", "running command: piano.hold" + " " + args)
        self.pianette.hold_piano_pedals(args)

    def do_piano__release(self, args):
        'Release a sequence of notes, chords and pedals'
        Debug.println("INFO", "running command: piano.release" + " " + args)
        self.pianette.release_piano_pedals(args)

    def do_time__sleep(self, args):
        'Block the exeuction for a certain amount of Pianette cycles'
        Debug.println("INFO", "running command: time.sleep" + " " + args)
        args_list = args.split()
        sleep_time = float(args_list[0]) * self.pianette.get_cycle_period()
        if args_list:
            Debug.println("NOTICE", 'sleeping for {:.3f} seconds'.format(sleep_time))
            time.sleep(sleep_time)
            Debug.println("NOTICE", 'done sleeping for {:.3f} seconds'.format(sleep_time))
        else:
            raise pianette.errors.PianetteCmdError("No argument provided for time.sleep")
