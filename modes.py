class Mode:
    pass


class Takeoff(Mode):
    @staticmethod
    def can_run(state):
        return state['Hardware'].ok() and state['Estimator'].ok()
