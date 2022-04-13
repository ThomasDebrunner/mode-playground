from state import create_initial_state
import re
import sys
from termcolor import colored
from modes import create_modes

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main_loop(vehicle):
    should_exit = False

    while not should_exit:
        print(colored('User selected mode [%s], vehicle executing [%s]' %
                      (vehicle.user_selected_mode, vehicle.executing_mode), 'blue'))

        command = input('> ')

        state_match = re.search('^state (.*)$', command)
        set_match = re.search('^set (.*) (ok|fail)$', command)
        mode_match = re.search('^mode (.*)$', command)

        if command == 'state':
            vehicle.state.print()
        elif command == 'modes':
            print('Available modes:')
            for mode in vehicle.modes:
                print('- ' + mode)
        elif command == 'q' or command == 'exit':
            should_exit = True
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
                vehicle.user_selected_mode = vehicle.modes[mode]
            else:
                eprint('%s is not a valid mode' % mode)
        elif not command == '':
            eprint('%s is not a command' % command)


class Vehicle:
    def __init__(self):
        self.modes = create_modes()
        self.state = create_initial_state()

        self.user_selected_mode = self.modes['Idle']
        self.executing_mode = self.modes['Idle']

    def simulate(self):
        pass



def main():
    vehicle = Vehicle()
    main_loop(vehicle)



if __name__ == '__main__':
    main()
