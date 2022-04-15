class CanRunResult:
    def __init__(self, value, reasons):
        self.can_run = value
        self.reasons = reasons

    def __and__(self, other):
        return CanRunResult(self.can_run and other.can_run, self.reasons + other.reasons)

    def __or__(self, other):
        return CanRunResult(self.can_run or other.can_run, [] if (self.can_run or other.can_run) else self.reasons + other.reasons)


class Condition:
    def __init__(self, query, expect, fail_stack, hysteresis, overridable):
        self._query = query
        self._expect = expect
        self._fail_stack = fail_stack
        self._hysteresis = hysteresis
        self._overridable = overridable

    def eval(self, state, time):
        state_val = state[self._query].ok()
        if state_val == self._expect:
            return CanRunResult(True, [])
        else:
            time_since_toggle = time - state[self._query].toggle_time()
            if time_since_toggle < self._hysteresis:
                return CanRunResult(True, ['%s is in %s state since %d ago. Fail safe in %d' %
                                           (self._query, 'OK' if state_val else 'Fail', time_since_toggle,
                                            self._hysteresis - time_since_toggle)])
            else:
                return CanRunResult(False, ['%s is in %s state' % (self._query, 'OK' if state_val else 'Fail')])


class Mode:
    def __init__(self, name, can_run_conditions):
        self.name = name
        self._can_run_conditions = can_run_conditions

    def can_run(self, state, time):
        res = CanRunResult(True, [])
        for condition in self._can_run_conditions:
            res = res & condition.eval(state, time)
        return res


def modes_from_dict(mode_dict):
    modes = {}
    for name, conf in mode_dict.items():
        can_run_conditions = []
        for query, condition_dict in conf['can_run'].items():
            expect = condition_dict['expect']
            fail_stack = condition_dict['fail_stack']
            hysteresis = condition_dict['hysteresis'] if 'hysteresis' in condition_dict else 0
            overridable = condition_dict['overridable'] if 'overridable' in condition_dict else False
            can_run_conditions.append(Condition(query, expect, fail_stack, hysteresis, overridable))
        modes[name] = Mode(name, can_run_conditions)

    return modes
