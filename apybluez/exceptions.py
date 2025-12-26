from apybluez.bluetooth import BluetoothError

class AAPError(BluetoothError):
    """Base exception for AAP related errors."""
    pass

class AAPConnectionError(AAPError):
    """Raised when an operation requires a connection but none is active."""
    pass

class AAPCommandError(AAPError):
    """Raised when a command is invalid or fails."""
    pass

class HCISpoofingError(AAPError):
    """Raised when HCI spoofing fails."""
    pass
