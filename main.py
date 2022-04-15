from state import state_from_dict
import re
import sys
from modes import modes_from_dict
from colors import bold, blue, red, yellow


def eprint(content):
    print(red(content))

def wprint(content):
    print(yellow(content))

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
        vehicle._state.print()
    elif command == 'modes':
        print('Available modes:')
        for mode in vehicle._modes:
            print('- ' + mode)
    elif command == 'stacks':
        print('Available stacks:')
        for name, stack in vehicle._stacks.items():
            print('> ' + bold(name))
            for mode in stack:
                print('  - ' + mode)
    elif state_match:
        query = state_match.group(1)
        try:
            vehicle._state[query].print()
        except IndexError as err:
            eprint(str(err))
    elif set_match:
        query = set_match.group(1)
        value = False if set_match.group(2) == 'fail' else True
        try:
            vehicle.set_state(query, value)
        except IndexError as err:
            eprint(str(err))
    elif mode_match:
        mode = mode_match.group(1)
        if mode in vehicle._modes:
            vehicle.request_mode(mode)
        else:
            eprint('%s is not a valid mode' % mode)
    elif command == 's':
        vehicle.simulate()
    elif not command == '':
        eprint('%s is not a command' % command)


class Vehicle:
    def __init__(self, modes, initial_state, stacks):
        self._modes = modes
        self._state = initial_state
        self._stacks = stacks

        self._user_selected_mode = self._modes['Idle']
        self._executing_mode = self._modes['Idle']
        self._fail_safe_stack = None

        self._sim_time = 0
        self._mode_request_reported = True

    def set_state(self, query, value):
        self._state[query].set(value, self._sim_time)

    def request_mode(self, mode):
        self._user_selected_mode = self._modes[mode]
        self._mode_request_reported = False

    def print_mode_state(self):
        print(bold(blue('Sim time: %d, user selected mode [%s], vehicle executing [%s]' %
                      (self._sim_time, self._user_selected_mode.name, self._executing_mode.name))))
        if self._fail_safe_stack:
            print(bold(red('Fail safe stack active: %s' % self._fail_safe_stack)))

    def simulate(self):
        self._sim_time += 1

        # Check if the user requested mode can be respected
        if self._user_selected_mode != self._executing_mode:
            res = self._user_selected_mode.can_enter(self._state, self._sim_time) & \
                  self._user_selected_mode.can_run(self._state, self._sim_time)

            if not res.can_run:
                if not self._mode_request_reported:
                    eprint('Can not switch to mode %s. Will switch as soon as condition allows' % self._user_selected_mode.name)
                    eprint('Reasons:')
                    for reason in res.reasons:
                        eprint(' - ' + reason)
                    self._mode_request_reported = True
            else:
                self._executing_mode = self._user_selected_mode
                self._fail_safe_stack = None
                print('Switched to mode %s' % self._user_selected_mode.name)

        # Check if currently active mode can still run
        res = self._executing_mode.can_run(self._state, self._sim_time)
        if not res.can_run:
            eprint('Can no longer execute mode %s, switching to fail safe %s stack...' %
                   (self._executing_mode.name, res.fail_stack))
            eprint('Reason:')
            for reason in res.reasons:
                eprint(' - ' + reason)

            self._fail_safe_stack = res.fail_stack
            for mode in self._stacks[self._fail_safe_stack]:
                wprint('Attempting %s mode' % mode)
                res = self._modes[mode].can_run(self._state, self._sim_time)
                if res.can_run:
                    wprint('Using %s mode as fail safe' % mode)
                    self._executing_mode = self._modes[mode]
                    break

        else:
            if len(res.reasons) > 0:
                wprint('Warning:')
                for reason in res.reasons:
                    wprint(' - ' + reason)


def main():
    import yaml

    with open('setup.yaml', 'r') as f:
        y = yaml.safe_load(f)

    modes = modes_from_dict(y['Modes'])
    state = state_from_dict(y['State'])
    stacks = y['Stacks']

    vehicle = Vehicle(modes, state, stacks)
    main_loop(vehicle)


if __name__ == '__main__':
    main()
