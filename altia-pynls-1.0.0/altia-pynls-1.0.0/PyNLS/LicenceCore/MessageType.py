from enum import Enum


class MessageType(Enum):
    """
    Represents the type of message communicated between clients and the server.
    """

    Reply = 0
    """
    A reply message from the server to a client.
    """

    TakeSeat = 1
    """
    Take a seat message sent from a client.
    """

    ReleaseSeat = 2
    """
    Release a seat message sent from a client.
    """

    RefreshSeat = 3
    """
    Refresh a seat message sent from a client.
    """

    QueryConnections = 4
    """
    Query the number of connections message sent from a client.
    """

    NumberOfSeats = 5
    """
    The total number of seats (for a product) message sent from a client.
    """

    ServerVersion = 6
    """
    The server version message sent from a client.
    """

    QueryProducts = 7
    """
    The number of products message sent from a client.
    """

    QueryLicence = 8
    """
    Query the licence details message sent from a client.
    """

    WebServerAddress = 9
    """
    The port and url the web server is running on.
    If the web server is not enabled, this will be empty string.
    """

    Kill = -1
    """
    Used to signal to the server to shutdown the sockets.
    This should only be used from the server to signal a safe shutdown.
    """
