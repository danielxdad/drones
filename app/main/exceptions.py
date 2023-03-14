class AppBaseException(Exception):
    """
    Base exception for the application.
    """

    message = ''

    def __init__(self, message = '', *args: object) -> None:
        super().__init__(message, *args)
        if message:
            self.message = message
    
    def __str__(self) -> str:
        return self.message


class WeightExceededError(AppBaseException):
    """
    Exception if the weight of the medication item exceeds the maximum drone's weight.
    """

    message = "Drone weight limit exceeded, can't load the item."


class DroneInvalidStateError(AppBaseException):
    message = "The new state is invalid."


class DroneBatteryTooLowError(AppBaseException):
    message = "The dron's battery is too low to fly."
