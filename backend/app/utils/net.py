import socket


def random_port(start_port, end_port, host='0.0.0.0') -> int:
    """
    Finds the first usable (free) port within a given range.

    Args:
        start_port (int): The starting port of the range (inclusive).
        end_port (int): The ending port of the range (inclusive).
        host (str): The host address to bind to (default is localhost).

    Returns:
        int or None: The first usable port found, or None if no usable port is found.
    """
    for port in range(start_port, end_port + 1):
        try:
            # Create a socket object
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Try to bind the socket to the host and port
            sock.bind((host, port))
            # If binding is successful, the port is usable
            sock.close()  # Close the socket as we only needed to check availability
            return port
        except OSError:
            # If binding fails (e.g., Address already in use), the port is not usable
            continue
    return 0
