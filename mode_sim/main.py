import re
from mode_sim.modes import modes_from_dict
from mode_sim.state import state_from_dict

from mode_sim.colors import bold, cyan, red, yellow
import json

def eprint(content):
    print(red(content))


def wprint(content):
    print(yellow(content))


def main_loop(vehicle):
    should_exit = False

    while not should_exit:
        command = input('> ')
        if command == 'q' or command == 'exit':
            break
        apply_command(vehicle, command)


def apply_command(vehicle, command):
    mode_match = re.search('^mode (.*)', command)
    state_match = re.search('^state (.*)', command)
    set_match = re.search('^set (.*) (ok|fail|true|false)', command)

    if command == 'state':
        vehicle.print_state()

    elif state_match:
        query = state_match.group(1)
        vehicle.print_state(query)

    elif command == 'modes':
        vehicle.print_modes()

    elif command == 'stacks':
        vehicle.print_stacks()

    elif set_match:
        query = set_match.group(1)
        value = False if (set_match.group(2) == 'fail' or  set_match.group(2) == 'false') else True
        vehicle.set_state(query, value)

    elif mode_match:
        mode = mode_match.group(1)
        vehicle.request_mode(mode)

    elif command == 's':
        vehicle.simulate()
    elif command == 'nop':
        pass
    elif not command == '':
        eprint('%s is not a command' % command)
    vehicle.print_mode_state()


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

    def _dump_json(self):
        return json.dumps(self, default=vars)

    def set_state(self, query, value):
        try:
            self._state[query].set(value, self._sim_time)
        except IndexError as err:
            eprint(str(err))

    def print_state(self, query=None):
        try:
            if query is None:
                self._state.print()
            else:
                self._state[query].print()
        except IndexError as err:
            eprint(str(err))

    def print_modes(self):
        print('Available modes:')
        for mode in self._modes:
            print('- ' + mode)

    def print_stacks(self):
        print('Available stacks:')
        for name, stack in self._stacks.items():
            print('> ' + bold(name))
            for mode in stack:
                print('  - ' + mode)

    def request_mode(self, mode):
        if mode in self._modes:
            self._user_selected_mode = self._modes[mode]
            self._mode_request_reported = False
        else:
            eprint('%s is not a valid mode' % mode)

    def print_mode_state(self):
        print(bold(cyan('Sim time: %d, user selected mode [%s], vehicle executing [%s]' %
                      (self._sim_time, self._user_selected_mode.name, self._executing_mode.name))))
        if self._fail_safe_stack:
            print(bold(red('Fail safe stack active: %s' % self._fail_safe_stack)))

    def simulate(self, step=1):
        self._sim_time += step

        # Check if the user requested mode can be respected
        if self._user_selected_mode != self._executing_mode:
            res = self._user_selected_mode.can_enter(self._state, self._sim_time) & \
                  self._user_selected_mode.can_run(self._state, self._sim_time)

            if not res.can_run:
                if not self._mode_request_reported:
                    wprint('Can not switch to mode %s. Will switch as soon as conditions allow' % self._user_selected_mode.name)
                    wprint('Reasons:')
                    for reason in res.reasons:
                        wprint(' - ' + reason)
                    self._mode_request_reported = True
            else:
                self._executing_mode = self._user_selected_mode
                self._fail_safe_stack = None
                self._mode_request_reported = True
                print('Switched to mode %s' % self._user_selected_mode.name)
                self.print_mode_state()

        # Check if currently active mode can still run
        res = self._executing_mode.can_run(self._state, self._sim_time)
        if not res.can_run:
            eprint('Can no longer execute mode %s, switching to fail safe %s stack...' %
                   (self._executing_mode.name, res.fail_stack))
            eprint('Reason:')
            for reason in res.reasons:
                eprint(' - ' + reason)

            self._fail_safe_stack = res.fail_stack

            if not self._fail_safe_stack in self._stacks:
                eprint('EMERGENCY: Fail safe stack %s does not exist.')
                eprint("This will be caught at mode register time. Giving up sim...")
                exit(1)

            success = False
            for mode in self._stacks[self._fail_safe_stack]:
                wprint('Attempting %s mode' % mode)
                if not mode in self._modes:
                    eprint('Mode %s does not exist!' % mode)
                    continue
                res = self._modes[mode].can_run(self._state, self._sim_time)
                if res.can_run:
                    wprint('Using %s mode as fail safe' % mode)
                    self._executing_mode = self._modes[mode]
                    success = True
                    self.print_mode_state()
                    break
            if not success:
                eprint('EMERGENCY: Fail safe stack %s did not have any modes that still work' % self._fail_safe_stack)
                eprint("This will be caught at mode register time. Giving up sim...")
                exit(1)

        else:
            if len(res.reasons) > 0:
                wprint('Warning:')
                for reason in res.reasons:
                    wprint(' - ' + reason)


def main():
    import yaml

    with open('../setup.yaml', 'r') as f:
        y = yaml.safe_load(f)

    modes = modes_from_dict(y['Modes'])
    state = state_from_dict(y['State'])
    stacks = y['Stacks']

    vehicle = Vehicle(modes, state, stacks)
    main_loop(vehicle)


if __name__ == '__main__':
    main()
