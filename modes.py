class CanRunResult:
    def __init__(self, value, reason):
        self.value = value
        self.reason = reason

    def __and__(self, other):
        return CanRunResult(self.value and other.value, self.reason + other.reason)


class Mode:
    pass


class Idle(Mode):
    name = 'Idle'

    def can_run(self, state):
        return not state['System/Armed'].ok()


class Takeoff(Mode):
    name = 'Takeoff'

    def can_run(self, state):
        return state['Hardware'].ok() and state['Estimator'].ok()


class Loiter(Mode):
    name = 'Loiter'


class GoTo(Mode):
    name = 'Goto'


class RTL(Mode):
    name = 'RTL'


class MotorFailureLand(Mode):
    name = 'MotorFailureLand'


class Parachute(Mode):
    name = 'Parachute'


def create_modes():
    modes = [
        Idle(),
        Takeoff(),
        Loiter(),
        GoTo(),
        RTL(),
        MotorFailureLand(),
        Parachute()
    ]
    return {m.name: m for m in modes}
