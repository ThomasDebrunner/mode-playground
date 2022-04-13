
def create_stacks():
    stacks = {
        'Idle': [
            'Idle'
        ],

        'Return': [
            'RTL',
            'Land',
            'FixedRateDescend',
            'Parachute',
            'Terminate'
        ],

        'Manual': [
            'PositionControlled',
            'AltitudeControlled',
            'Stabilized'
        ]
    }
    return stacks
