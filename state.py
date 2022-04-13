from colors import red, green

class StateItem:
    def __init__(self, name):
        self.name = name
        self.value = False

    def ok(self):
        return self.value

    def set(self, value):
        self.value = value

    def print(self, level=0):
        state_str = green('OK') if self.ok() else red('Fail')
        print((' ' * level) + self.name + (' ' * (20-level-len(self.name))) + state_str)

    def __getitem__(self, query):
        raise IndexError('State item %s does not have any children %s' % (self.name, query))


class StateGroup:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children is not None else []

    def __getitem__(self, query):
        next_item = query
        remaining_query = ''
        if '/' in query:
            split = query.split('/')
            next_item = split[0]
            remaining_query = '/'.join(split[1:])
        for c in self.children:
            if c.name == next_item:
                if remaining_query == '':
                    return c
                else:
                    return c[remaining_query]
        raise IndexError('State %s does not exist' % query)

    def set(self, value):
        for c in self.children:
            c.set(value)

    def ok(self):
        for c in self.children:
            if not c.ok():
                return False
        return True

    def print(self, level=0):
        state_str = green('OK') if self.ok() else red('Fail')
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
            StateGroup('GlobalPosition', [
                StateItem('X'),
                StateItem('Y'),
                StateItem('Z')
            ])
        ]),
        StateGroup('System', [
            StateItem('Armed'),
            StateItem('Datalink'),
            StateItem('ManualControl')
        ])
    ])
    return state
