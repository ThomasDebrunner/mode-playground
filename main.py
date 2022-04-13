from state import create_initial_state
import re
import sys
from termcolor import colored
from modes import Takeoff

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main_loop(state):
    should_exit = False
    while not should_exit:
        command = input('> ')

        state_match = re.search('^state (.*)$', command)
        set_match = re.search('^set (.*) (ok|fail)$', command)

        if command == 'state':
            state.print()
        elif command == 'q' or command == 'exit':
            should_exit = True
        elif state_match:
            query = state_match.group(1)
            try:
                state[query].print()
            except IndexError as err:
                eprint(str(err))
        elif set_match:
            query = set_match.group(1)
            value = False if set_match.group(2) == 'fail' else True
            try:
                state[query].set(value)
            except IndexError as err:
                eprint(str(err))
        elif not command == '':
            eprint('%s is not a command' % command)


def main():
    state = create_initial_state()
    main_loop(state)



if __name__ == '__main__':
    main()
