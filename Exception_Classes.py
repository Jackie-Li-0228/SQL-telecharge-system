class UserNotFoundError(Exception):
    """Exception raised when the user with the given ID card number is not found."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class UserTypeNotFoundError(Exception):
    """Exception raised when the user type is not found in the UserTypes table."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    """Exception raised when a database operation fails."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class PhoneNumberNotFoundError(Exception):
    """Exception raised when the phone number is not found in the database."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class PaymentProcessingError(Exception):
    """Exception raised when there's an error during the payment processing."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidDateError(Exception):
    """Exception raised when today is not the first day of the month."""
    def __init__(self, message="Date Invalid."):
        self.message = message
        super().__init__(self.message)

class UserNotAdminError(Exception):
    """Exception raised when the user is not an admin."""
    def __init__(self, message="User is not an admin."):
        self.message = message
        super().__init__(self.message)

class NoLastMonthPackagesError(Exception):
    """Exception raised when no packages for the last month are found."""
    def __init__(self, message="No packages found for the last month."):
        self.message = message
        super().__init__(self.message)

class NoValidPackageFoundError(Exception):
    """Exception raised when no valid package is found for the current month."""
    def __init__(self, message="No valid package found for the current month."):
        self.message = message
        super().__init__(self.message)

class NoValidServiceFoundError(Exception):
    """The Service ID does not exist."""
    def __init__(self, message="No valid package found for the current month."):
        self.message = message
        super().__init__(self.message)

class ValueError(Exception):
    """Exception raised when a value is invalid."""
    def __init__(self, message="Value is invalid"):
        self.message = message
        super().__init__(self.message)

class InformationNotMatchError(Exception):
    """Exception raised when the information does not match the database."""
    def __init__(self, message="Information does not match."):
        self.message = message
        super().__init__(self.message)

class PhoneSuspendedError(Exception):
    def __init__(self, message="The phone number is suspended."):
        self.message = message
        super().__init__(self.message)

class ObjectNotFoundError(Exception):
    def __init__(self, message="Object not found."):
        self.message = message
        super().__init__(self.message)

class InputCheckFailed(Exception):
    def __init__(self, message):
        super().__init__(message)