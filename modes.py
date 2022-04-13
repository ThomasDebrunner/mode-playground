class CanRunResult:
    def __init__(self, value, reasons):
        self.can_run = value
        self.reasons = reasons

    def __and__(self, other):
        return CanRunResult(self.can_run and other.can_run, self.reasons + other.reasons)

    def __or__(self, other):
        return CanRunResult(self.can_run or other.can_run, [] if (self.can_run or other.can_run) else self.reasons + other.reasons)


def _expect(state, query, value):
    state_val = state[query].ok()
    if state_val == value:
        return CanRunResult(True, [])
    else:
        return CanRunResult(False, ['%s is in %s state' % (query, 'OK' if state_val else 'Fail')])


def expect_ok(state, query):
    return _expect(state, query, True)


def expect_fail(state, query):
    return _expect(state, query, False)


class Mode:
    pass


class Idle(Mode):
    name = 'Idle'

    def can_run(self, state):
        return expect_fail(state, 'System/Armed')


class Takeoff(Mode):
    name = 'Takeoff'

    def can_run(self, state):
        return expect_ok(state, 'Hardware') & \
               expect_ok(state, 'Estimator/GlobalPosition') & \
               expect_ok(state, 'System/Armed')


class Loiter(Mode):
    name = 'Loiter'

    def can_run(self, state):
        return expect_ok(state, 'Hardware') & \
               expect_ok(state, 'Estimator/GlobalPosition') & \
               expect_ok(state, 'System/Armed')


class GoTo(Mode):
    name = 'Goto'

    def can_run(self, state):
        return expect_ok(state, 'Hardware') & \
               expect_ok(state, 'Estimator/GlobalPosition') & \
               expect_ok(state, 'System/Armed')


class RTL(Mode):
    name = 'RTL'

    def can_run(self, state):
        return expect_ok(state, 'Hardware') & \
               expect_ok(state, 'Estimator/GlobalPosition') & \
               expect_ok(state, 'System/Armed')


class PositionControlled(Mode):
    name = 'PositionControl'

    def can_run(self, state):
        return expect_ok(state, 'Hardware') & \
               expect_ok(state, 'Estimator/GlobalPosition') & \
               expect_ok(state, 'System/Armed') & \
               expect_ok(state, 'System/ManualControl')


class AltitudeControlled(Mode):
    name = 'AltitudeControl'

    def can_run(self, state):
        return expect_ok(state, 'Hardware') & \
               expect_ok(state, 'Estimator/GlobalPosition/Z') & \
               expect_ok(state, 'System/Armed') & \
               expect_ok(state, 'System/ManualControl')


def create_modes():
    modes = [
        Idle(),
        Takeoff(),
        Loiter(),
        GoTo(),
        RTL(),
        PositionControlled(),
        AltitudeControlled()
    ]
    return {m.name: m for m in modes}
