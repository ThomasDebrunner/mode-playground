from termcolor import colored


class StateItem:
    def __init__(self, name):
        self.name = name
        self.value = False

    def ok(self):
        return self.value

    def print(self, level=0):
        state_str = colored('OK', 'green') if self.ok() else colored('Fail', 'red')
        print((' ' * level) + self.name + (' ' * (20-level-len(self.name))) + state_str)


class StateGroup:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children is not None else []

    def __getitem__(self, query):
        for c in self.children:
            if c.name == query:
                return c
        raise IndexError('State %s does not exist' % query)

    def ok(self):
        for c in self.children:
            if not c.ok():
                return False
        return True

    def print(self, level=0):
        state_str = colored('OK', 'green') if self.ok() else colored('Fail', 'red')
        print((' ' * level) + self.name + (' ' * (20-level-len(self.name))) + state_str)
        for c in self.children:
            c.print(level+1)


def create_initial_state():
    state = StateGroup('State', [
        StateGroup('Hardware', [
            StateGroup('Sensors', [
                StateGroup('Gyro', [
                    StateGroup('Gyro0', [
                        StateItem('Healthy'),
                        StateItem('Calibrated')
                    ]),
                    StateGroup('Gyro1', [
                        StateItem('Healthy'),
                        StateItem('Calibrated')
                    ]),
                    StateGroup('Gyro2', [
                        StateItem('Healthy'),
                        StateItem('Calibrated')
                    ])
                ]),
                StateGroup('Accelerometer', [
                    StateGroup('Accelerometer0', [
                        StateItem('Healthy'),
                        StateItem('Calibrated')
                    ]),
                    StateGroup('Accelerometer1', [
                        StateItem('Healthy'),
                        StateItem('Calibrated')
                    ]),
                    StateGroup('Accelerometer2', [
                        StateItem('Healthy'),
                        StateItem('Calibrated')
                    ]),
                ])
            ])
        ]),
        StateGroup('Estimator', [

        ]),
        StateGroup('System', [
            StateItem('Armed')
        ])
    ])
    return state
