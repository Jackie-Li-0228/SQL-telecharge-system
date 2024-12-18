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
