class BorschSyntaxError(Exception):
    """Raised when the .brsh markup is malformed."""
    pass

class BorschRuntimeError(Exception):
    """Raised when the code fails during execution."""
    pass

def print_borsch_error(error_type, message):
    print(f"\nBORSCH ERROR: {error_type}")
    print(f"> {message}\n")