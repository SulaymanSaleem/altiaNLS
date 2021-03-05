import os
import sys
import socket
import getpass
import platform
from datetime import datetime


class Utils:
    """
    Provides static utility methods for the network licence app
    """
    @staticmethod
    def GetExecutingFilePath() -> str:
        """
        Returns the full path to the executing file folder

        :returns: The full path to the executing file folder
        """
        return os.getcwd()

    @staticmethod
    def GetIPAddress(server=None, port=None) -> str:
        """
        Returns the IP Address of the local computer, by checking which
        network card will connect to the specified server and port.

        :param server: The server to connect to.
        :param port: The port to connect on.
        :returns: The IP Address of the local computer.
        """
        if not server and not port:
            return socket.gethostbyname(socket.gethostname())
        return socket.getaddrinfo(server, port, socket.AF_INET6)[0][4][0]

    @staticmethod
    def GetHostName() -> str:
        """
        Returns the host name of the local computer.

        :returns: The host name of the local computer.
        """
        return socket.gethostname()

    @staticmethod
    def GetPlatform() -> str:
        """
        Returns the platform of the local computer.
        """
        return platform.system()

    @staticmethod
    def GetPlatformVersion() -> str:
        """
        Returns the platform version of the local computer.
        """
        if platform.system() == 'Windows':
            return platform.version()
        return platform.release()

    @staticmethod
    def GetPlatformArchitecture() -> str:
        """
        Returns the platform architecture of the local computer.
        """
        return "64-bit" if sys.maxsize > 2**32 else "32-bit"

    @staticmethod
    def GetUserName() -> str:
        """
        Returns the user name of the person who is current logged into the local computer.

        :returns: Tur user name of the person who is current logged into the local computer.
        """
        return getpass.getuser()

    @staticmethod
    def IsPortAvailable(port: int) -> bool:
        """
        Returns a value to indicate if the specified port is available

        :param port: The port to test
        :returns: True if the port is available, otherwise false
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            return sock.connect_ex(('localhost', port)) != 0

    @staticmethod
    def TicksToMilliseconds(ticks: int) -> int:
        """
        Returns the specified ticks converted as whole milliseconds.

        :param ticks: The ticks to convert to whole milliseconds.
        :returns: Ticks as whole milliseconds
        """
        TicksPerMillisecond = 10000  # There are 10,000 ticks per millisecond in TimeSpan (from .NET)
        return ticks // TicksPerMillisecond

    @staticmethod
    def UnixTimeToDate(unixTime: float) -> datetime:
        """
        Returns the specified unix time converted to date.

        :param unixTime: The unix time to convert.
        :returns: The unix time converted to a date
        """
        return datetime.fromtimestamp(unixTime)

    @staticmethod
    def DateToUnixTime(value: datetime) -> float:
        """
        Returns the specified date converted to unix time (Epoch time).

        :param value: The date to convert.
        :returns: The date converted to unix time.
        """
        return datetime.timestamp(value)

    @staticmethod
    def FixUpUri(uri: str) -> str:
        """
        Ensures the specified URI does not end in a forward slash "/"

        :param uri: The URI to fix.
        :returns: The URI without a forward slash.
        """
        if uri.endswith('/'):
            return uri[:-1]
        return uri

    @staticmethod
    def enforce_licence_newline(elem, level=0):
        """
        Formats the parsed xml to the same format as expected by the VS source code.
        This involves adding carriage returns, newlines and 2 whitespace characters per nest level.
        The default ElementTree tostring only adds newline and 1 whitespace character.
        Originally from ElementTree developer, modified to suit: http://effbot.org/zone/element-lib.html#prettyprint

        :param elem: An element of an element tree
        :param level: Depth of nesting
        """
        newline = "\r\n"
        if len(elem):
            if not elem.text or not elem.text.strip():
                # After opening parent tag
                elem.text = newline + (level + 1) * "  "
            for elem in elem:
                # For each internal tag
                Utils.enforce_licence_newline(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                # Before closing parent tag
                elem.tail = newline + (level - 1) * "  "
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                # After data tag
                elem.tail = newline + level * "  "
