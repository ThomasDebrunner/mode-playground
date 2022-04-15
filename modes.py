class CanRunResult:
    def __init__(self, value, reasons):
        self.can_run = value
        self.reasons = reasons

    def __and__(self, other):
        return CanRunResult(self.can_run and other.can_run, self.reasons + other.reasons)

    def __or__(self, other):
        return CanRunResult(self.can_run or other.can_run, [] if (self.can_run or other.can_run) else self.reasons + other.reasons)


class Condition:
    def __init__(self, query, value):
        self._query = query
        self._value = value

    def eval(self, state):
        state_val = state[self._query].ok()
        if state_val == self._value:
            return CanRunResult(True, [])
        else:
            return CanRunResult(False, ['%s is in %s state' % (self._query, 'OK' if state_val else 'Fail')])


class Mode:
    def __init__(self, name, can_run_conditions):
        self.name = name
        self._can_run_conditions = can_run_conditions

    def can_run(self, state):
        res = CanRunResult(True, [])
        for condition in self._can_run_conditions:
            res = res & condition.eval(state)
        return res


def modes_from_dict(mode_dict):
    modes = {}
    for name, conf in mode_dict.items():
        can_run_conditions = [Condition(q, v) for q, v in conf['can_run'].items()]
        modes[name] = Mode(name, can_run_conditions)

    return modes
