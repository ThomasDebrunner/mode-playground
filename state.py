from colors import red, green

class StateItem:
    def __init__(self, name, initial_value):
        self.name = name
        self.value = initial_value

    def ok(self):
        return self.value

    def set(self, value):
        self.value = value

    def print(self, level=0):
        state_str = green('true (OK)') if self.ok() else red('false (Fail)')
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
        state_str = green('true (OK)') if self.ok() else red('false (Fail)')
        print((' ' * level) + self.name + (' ' * (20-level-len(self.name))) + state_str)
        for c in self.children:
            c.print(level+1)

STATE = {
    'State': {
        'Hardware': {
            'Sensors': {
                'Gyro': {
                    'Healthy': True
                }
            }
        }
    }
}


def _state_from_dict(state_dict):
    res = []
    for k, v in state_dict.items():
        if type(v) is dict:
            res.append(StateGroup(k,  _state_from_dict(v)))
        else:
            res.append(StateItem(k, v))
    return res


def state_from_dict(state_dict):
    return _state_from_dict(state_dict)[0]
