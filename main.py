from state import state_from_dict
import re
import sys
from modes import modes_from_dict
from colors import bold, blue


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main_loop(vehicle):
    should_exit = False

    while not should_exit:
        vehicle.print_mode_state()
        command = input('> ')
        if command == 'q' or command == 'exit':
            break
        apply_command(vehicle, command)


def apply_command(vehicle, command):
    state_match = re.search('^state (.*)$', command)
    set_match = re.search('^set (.*) (ok|fail)$', command)
    mode_match = re.search('^mode (.*)$', command)

    if command == 'state':
        vehicle.state.print()
    elif command == 'modes':
        print('Available modes:')
        for mode in vehicle.modes:
            print('- ' + mode)
    elif command == 'stacks':
        print('Available stacks:')
        for name, stack in vehicle.stacks.items():
            print('> ' + bold(name))
            for mode in stack:
                print('  - ' + mode)
    elif state_match:
        query = state_match.group(1)
        try:
            vehicle.state[query].print()
        except IndexError as err:
            eprint(str(err))
    elif set_match:
        query = set_match.group(1)
        value = False if set_match.group(2) == 'fail' else True
        try:
            vehicle.state[query].set(value)
        except IndexError as err:
            eprint(str(err))
    elif mode_match:
        mode = mode_match.group(1)
        if mode in vehicle.modes:
            vehicle.request_mode(mode)
        else:
            eprint('%s is not a valid mode' % mode)
    elif not command == '':
        eprint('%s is not a command' % command)
    vehicle.simulate()


class Vehicle:
    def __init__(self, modes, initial_state, stacks):
        self.modes = modes
        self.state = initial_state
        self.stacks = stacks

        self._user_selected_mode = self.modes['Idle']
        self._executing_mode = self.modes['Idle']

    def request_mode(self, mode):
        self._user_selected_mode = self.modes[mode]

    def print_mode_state(self):
        print(blue('User selected mode [%s], vehicle executing [%s]' %
                      (self._user_selected_mode.name, self._executing_mode.name)))

    def simulate(self):
        res = self._user_selected_mode.can_run(self.state)
        if res.can_run:
            self._executing_mode = self._user_selected_mode
        else:
            eprint('Can not execute %s because' % self._user_selected_mode.name)
            for reason in res.reasons:
                eprint('- ' + reason)


def main():
    import yaml

    with open('modes.yaml', 'r') as f:
        modes = modes_from_dict(yaml.safe_load(f))

    with open('state.yaml', 'r') as f:
        state = state_from_dict(yaml.safe_load(f))

    with open('stacks.yaml', 'r') as f:
        stacks = yaml.safe_load(f)

    vehicle = Vehicle(modes, state, stacks)
    main_loop(vehicle)


if __name__ == '__main__':
    main()
