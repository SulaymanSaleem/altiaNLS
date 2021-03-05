import os
from xml.etree import ElementTree
from datetime import datetime, timedelta


class Config:
    """
    Class containing licence server configuration settings.
    """
    FileName = "Config.xml"
    """
    Represents the default name of the licence server configuration settings file
    """
    DefaultLicenceServerPort = 3180
    """
    Represents the default port for the licence server
    """
    DefaultWebServerPort = 8080
    """
    Represents the default port for the web server
    """
    LowPort = 1024
    HighPort = 65535
    DefaultReloadTime = '02:30:00'

    m_LicenceFolder = ''
    m_DataFolder = ''
    m_LicenceServerPort = DefaultLicenceServerPort
    m_WebServerPort = DefaultWebServerPort
    m_ReloadTime = DefaultReloadTime
    m_NumberOfThreads = 5
    m_HeartBeat = 300
    m_EnableWebServer = False
    m_MaximumLogFileSize = 10000
    m_NumberOfLogs = 10
    m_Password = ''
    m_UserName = ''
    m_ePassword = ''

    @property
    def DataFolder(self) -> str:
        """
        Gets the path to the data file folder

        :returns: The path to the data file folder
        """
        return self.m_DataFolder

    @DataFolder.setter
    def DataFolder(self, value) -> None:
        """
        Sets the path to the data file folder

        :param value: The path to the data file folder
        """
        self.m_DataFolder = value

    @property
    def EnableWebServer(self) -> bool:
        """
        Gets a value to indicate if the web server is enabled

        :returns: If the web server is enabled
        """
        return self.m_EnableWebServer

    @EnableWebServer.setter
    def EnableWebServer(self, value) -> None:
        """
        Sets if the web server is enabled

        :param value: True to enable the web server, otherwise false
        """
        self.m_EnableWebServer = value

    @property
    def HeartBeat(self) -> int:
        """
        Gets the delay, in seconds, after which a licence is stale
        The default value is 300

        :returns: The delay after which a licence is stale.
        """
        return self.m_HeartBeat

    @HeartBeat.setter
    def HeartBeat(self, value) -> None:
        """
        Sets the delay, in seconds, after which a licence is stale
        The default value is 300

        :param value: The delay after which a licence is stale.
        """
        if value > 0:
            self.m_HeartBeat = value

    @property
    def LicenceFolder(self) -> str:
        """
        Gets the path to the licence folder.

        :returns: The path to the licence folder.
        """
        return self.m_LicenceFolder

    @LicenceFolder.setter
    def LicenceFolder(self, value) -> None:
        """
        Sets the path to the licence folder.

        :param value: The path to the licence folder.
        """
        self.m_LicenceFolder = value

    @property
    def MaximumLogFileSize(self) -> int:
        """
        Gets the max size of log file.

        :returns: The max size of log file
        """
        return self.m_MaximumLogFileSize

    @MaximumLogFileSize.setter
    def MaximumLogFileSize(self, value) -> None:
        """
        Sets the max size of log file

        :param value: The max size of log file
        """
        self.m_MaximumLogFileSize = value

    @property
    def NumberOfLogs(self) -> int:
        """
        Gets the number of logs to save as history

        :returns: The number of logs to save as history
        """
        return self.m_NumberOfLogs

    @NumberOfLogs.setter
    def NumberOfLogs(self, value) -> None:
        """
        Sets the number of logs to save as history

        :param value: The number of logs to save as history
        """
        self.m_NumberOfLogs = value

    @property
    def NumberOfThreads(self) -> int:
        """
        Gets the number of concurrent threads.

        :returns: The number of concurrent threads.
        """
        return self.m_NumberOfThreads

    @NumberOfThreads.setter
    def NumberOfThreads(self, value) -> None:
        """
        Sets the number of concurrent threads.

        :param value: The number of concurrent threads.
        """
        if value > 0:
            self.m_NumberOfThreads = value

    @property
    def LicenceServerPort(self) -> int:
        """
        Gets the port the licence manager runs on.

        :returns: The port the licence server runs on.
        """
        return self.m_LicenceServerPort

    @LicenceServerPort.setter
    def LicenceServerPort(self, value) -> None:
        """
        Sets the port the licence manager runs on.

        :param value: The port the licence server runs on.
        """
        self.m_LicenceServerPort = value

    @property
    def ReloadTime(self) -> str:
        """
        Gets the time to run the service daily

        :returns: The time to run the service daily.
        """
        return self.m_ReloadTime

    @ReloadTime.setter
    def ReloadTime(self, value) -> None:
        """
        Sets the time to run the service daily

        :param value: The time to run the service daily.
        """
        self.m_ReloadTime = value

    @property
    def WebServerPort(self) -> int:
        """
        Gets the port the licence manager web server runs on

        :returns: The port the licence manager web server runs on.
        """
        return self.m_WebServerPort

    @WebServerPort.setter
    def WebServerPort(self, value) -> None:
        """
        Sets the port the licence manager web server runs on

        :param value: The port the licence manager web server runs on.
        """
        if self.LowPort <= value <= self.HighPort:
            self.m_WebServerPort = value

    @property
    def ePassword(self) -> str:
        """
        Gets an encrypted password for the secure web server login
        If the encrypted password is nothing empty string is returned

        :returns: An encrypted password for the secure web server login
        """
        return self.m_ePassword

    @ePassword.setter
    def ePassword(self, value) -> None:
        """
        Sets an encrypted password for the secure web server login

        :param value: An encrypted password for the secure web server login
        """
        self.m_ePassword = value

    @property
    def Password(self) -> str:
        """
        Gets a plain text password for the secure web server login

        :returns: A plain text password for the secure web server login.
        """
        return self.m_Password

    @Password.setter
    def Password(self, value) -> None:
        """
        Sets a plain text password for the secure web server login

        :param value: A plain text password for the secure web server login.
        """
        self.m_Password = value

    @property
    def UserName(self) -> str:
        """
        Gets the username for the secure web server login.

        :returns: The username for the secure web server login.
        """
        return self.m_UserName

    @UserName.setter
    def UserName(self, value) -> None:
        """
        Sets the username for the secure web server login.

        :param value: The username for the secure web server login.
        """
        self.m_UserName = value

    def GetReloadTimeFromNow(self) -> timedelta:
        """
        Returns a timedelta representing the interval until the licences will next re-load

        :returns: A timedelta representing the interval until the licences will next re-load
        """
        dummy_time = datetime.strptime(self.m_ReloadTime, "%H:%M:%S")
        reload_time = timedelta(hours=dummy_time.hour, minutes=dummy_time.minute)
        nextCheck = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + reload_time
        dateNow = datetime.now()
        if nextCheck < dateNow:
            nextCheck += timedelta(days=1)
        return nextCheck - dateNow

    def Serialize(self, fileName) -> None:
        """
        Serializes the licence server configuration file to the specified filename.

        :param fileName: The filename for the licence server configuration.
        """
        if not (fileName and fileName.strip()):
            raise ValueError
        config_file = ElementTree.ElementTree()
        config_content = ElementTree.Element('licence_server_config')
        DataFolder = ElementTree.SubElement(config_content, 'datafolder')
        DataFolder.text = self.DataFolder
        HeartBeat = ElementTree.SubElement(config_content, 'heartbeat')
        HeartBeat.text = self.HeartBeat
        LicenceFolder = ElementTree.SubElement(config_content, 'licencefolder')
        LicenceFolder.text = self.LicenceFolder
        MaximumLogFileSize = ElementTree.SubElement(config_content, 'maximumlogfilesize')
        MaximumLogFileSize.text = self.MaximumLogFileSize
        NumberOfLogs = ElementTree.SubElement(config_content, 'numberoflogs')
        NumberOfLogs.text = self.NumberOfLogs
        NumberOfThreads = ElementTree.SubElement(config_content, 'numberofthreads')
        NumberOfThreads.text = self.NumberOfThreads
        LicenceServerPort = ElementTree.SubElement(config_content, 'port')
        LicenceServerPort.text = self.LicenceServerPort
        ReloadTime = ElementTree.SubElement(config_content, 'reloadtime')
        ReloadTime.text = self.ReloadTime
        WebServerPort = ElementTree.SubElement(config_content, 'webserverport')
        WebServerPort.text = self.WebServerPort
        EnableWebServer = ElementTree.SubElement(config_content, 'enablewebserver')
        EnableWebServer.text = self.EnableWebServer
        ePassword = ElementTree.SubElement(config_content, 'epassword')
        ePassword.text = self.ePassword
        Password = ElementTree.SubElement(config_content, 'password')
        Password.text = self.Password
        UserName = ElementTree.SubElement(config_content, 'username')
        UserName.text = self.UserName
        config_file._setroot(config_content)
        config_file.write(open(fileName, 'w'), encoding='unicode')

    def Deserialize(self, fileName) -> None:
        """
        Deserializes the licence server configuration file from the specified filename.

        :param fileName: The name of the file to deserialize the licence server configuration from.
        """
        if not (fileName and fileName.strip()):
            raise ValueError
        try:
            if os.path.isfile(os.path.join(os.getcwd(), fileName)) and (fileName.endswith('.xml')):
                config_content = ElementTree.parse(os.path.join(os.getcwd(), fileName)).getroot()
                if config_content.find('datafolder') is not None:
                    self.DataFolder = config_content.find('datafolder').text
                if config_content.find('heartbeat') is not None:
                    self.HeartBeat = int(config_content.find('heartbeat').text)
                if config_content.find('licencefolder') is not None:
                    self.LicenceFolder = config_content.find('licencefolder').text
                if config_content.find('maximumlogfilesize') is not None:
                    self.MaximumLogFileSize = int(config_content.find('maximumlogfilesize').text)
                if config_content.find('numberoflogs') is not None:
                    self.NumberOfLogs = int(config_content.find('numberoflogs').text)
                if config_content.find('numberofthreads') is not None:
                    self.NumberOfThreads = int(config_content.find('numberofthreads').text)
                if config_content.find('port') is not None:
                    self.LicenceServerPort = int(config_content.find('port').text)
                if config_content.find('reloadtime') is not None:
                    self.ReloadTime = config_content.find('reloadtime').text
                if config_content.find('webserverport') is not None:
                    self.WebServerPort = int(config_content.find('webserverport').text)
                if config_content.find('enablewebserver') is not None:
                    self.EnableWebServer = (config_content.find('enablewebserver').text == 'true')
                if config_content.find('epassword') is not None:
                    self.ePassword = config_content.find('epassword').text
                if config_content.find('password') is not None:
                    self.Password = config_content.find('password').text
                if config_content.find('username') is not None:
                    self.UserName = config_content.find('username').text
        except FileNotFoundError:
            raise FileNotFoundError("Config file: " + fileName + " not found.")

    def HasEncryptedPassword(self) -> bool:
        """
        Gets a value to indicate if the config is using an encrypted password.

        :returns: True if the config has an encrypted password, otherwise false.
        """
        return bool(self.m_ePassword and self.m_ePassword.strip())

    def IsSecureWebServer(self) -> bool:
        """
        Gets a value to indicate if the web server has been secured with a login.

        :return: True if the web server has been secured with a login, otherwise false.
        """
        if bool(self.m_ePassword and self.m_ePassword.strip()) or bool(self.m_Password and self.m_Password.strip()):
            return bool(self.m_UserName and self.m_UserName.strip())
        return False
