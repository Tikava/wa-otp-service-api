class OTPVerificationError(Exception):
    """Base exception for OTP verification errors."""
    pass

class OTPExpiredError(OTPVerificationError):
    """Raised when OTP has expired."""
    pass

class OTPAlreadyUsedError(OTPVerificationError):
    """Raised when OTP has already been used."""
    pass

class InvalidOTPError(OTPVerificationError):
    """Raised when OTP is invalid or does not match."""
    pass

class ClientValidationError(OTPVerificationError):
    """Raised when client validation fails."""
    pass