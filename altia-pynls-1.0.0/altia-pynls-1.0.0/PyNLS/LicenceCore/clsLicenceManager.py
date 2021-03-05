from .clsInvalidProductException import InvalidProductException
from .clsDatabaseSchema import Database, DatabaseSchema
from datetime import timedelta, date, datetime
from .clsLicenceReader import LicenceReader
from .clsMessage_pb2 import Message
from xml.etree import ElementTree
from .clsUtils import Utils
from typing import List
import logging
import sqlite3
import os

class LicenceManager:
    """
    Class to manage network licences.
    """
    WildCard = "*"
    FudgeFactor = 30

    m_LicenceFolder = ""
    m_DataFolder = ""
    m_HeartBeat = timedelta(seconds=300)
    m_DoubleValidation = True
    m_EncryptDatabase = False
    m_WebServerUri = ""

    @property
    def DataFile(self) -> str:
        """
        Gets the full path to the database filename.

        :returns: The full path to the database filename
        """
        return os.path.join(self.GetDataFolder(), 'Data.db3')

    @property
    def DoubleValidation(self) -> bool:
        """
        Gets a value to determine if licences are both validated
        when read from file and database or whether they are only
        validated when read from file.

        :returns: True if licences are validated both when read
        from file and database otherwise false.
        """
        return self.m_DoubleValidation

    @DoubleValidation.setter
    def DoubleValidation(self, value: bool) -> None:
        """
        Sets a value to determine if licences are both validated
        when read from file and database or whether they are only
        validated when read from file.

        :param value: A value to determine if licences are both
        validated when read from file and database or not.
        """
        self.m_DoubleValidation = value

    @property
    def EncryptDatabase(self) -> bool:
        """
        Gets a value to indicate if the datafile is encrypted.

        :returns: True if the datafile is encrypted, otherwise false
        """
        return self.m_EncryptDatabase

    @EncryptDatabase.setter
    def EncryptDatabase(self, value: bool) -> None:
        """
        Sets a value to indicate if the datafile is encrypted.

        :param value: True if the datafile is encrypted, otherwise false
        """
        self.m_EncryptDatabase = value

    @property
    def HeartBeat(self) -> timedelta:
        """
        Gets the time after which a licence is considered stale.
        The default is 300 seconds, this value should be the same as client HeartBeat value

        :returns: The time after which a licence is considered stale.
        """
        return self.m_HeartBeat

    @HeartBeat.setter
    def HeartBeat(self, value: int) -> None:
        """
        Sets the time after which a licence is considered stale.
        The default is 300 seconds, this value should be the same as client HeartBeat value

        :param value: The time after which a licence is considered stale.
        """
        self.m_HeartBeat = timedelta(seconds=value)

    @property
    def LicenceFolder(self) -> str:
        """
        Gets the full path to the folder containing the licences.

        :returns: The full path to the folder containing the licences.
        """
        return self.GetLicenceFolder()

    @property
    def ProviderVersion(self) -> str:
        """
        Returns the version of the managed components used to interact with the SQLite core library.

        :returns: The version of the managed components used to interact with the SQLite core library.
        """
        return sqlite3.version

    @property
    def SQLiteVersion(self) -> str:
        """
        Returns the version of the underlying SQLite core library.

        :returns: The version of the underlying SQLite core library.
        """
        return sqlite3.sqlite_version

    @property
    def WebServerUri(self) -> str:
        """
        Gets the port the web server is running on.

        :returns: The web server port.
        """
        return Utils.FixUpUri(self.m_WebServerUri)

    @WebServerUri.setter
    def WebServerUri(self, value: str) -> None:
        """
        Sets the port the web server is running on

        :param value: The port the web server is running on.
        """
        self.m_WebServerUri = value

    def __init__(self, licenceFolder: str, dataFolder: str, messageDelegate):
        """
        Initializes the licence manager class with the specified licence
        sub folder name, database sub folder name and error logging object.
        If the licence folder and data folder are empty then the
        executing assembly folder will be used.

        :param licenceFolder: The name of the licence sub folder
        :param dataFolder: The name of the database sub folder
        :param messageDelegate: An error logging object
        """
        self.m_LicenceFolder = licenceFolder
        self.m_DataFolder = dataFolder
        self.m_ErrorLogger = messageDelegate

        if not self.m_DataFolder:
            if not os.path.exists(self.GetDataFolder()):
                os.mkdir(self.GetDataFolder())
                logging.info('Created data folder: \'' + self.GetDataFolder() + '\'')

        if not self.m_LicenceFolder:
            if not os.path.exists(self.GetLicenceFolder()):
                os.mkdir(self.GetLicenceFolder())
                logging.info('Created licence folder: \'' + self.GetLicenceFolder() + '\'')

        self.CreateDatabase()
        self.DeleteStaleSeats()
        self.AnalyzeDatabase()
        self.VacuumDatabase()

    def DecryptDatabase(self):
        """
        Decrypts the current database
        """
        # TODO investigate decryption..? source doesnt look like it "decrypts"

    def GetConnections(self, product: str) -> List[Message.UserRecordStruct]:
        """
        Returns a list of connections for the specified product.

        :param product: The name of the product to get the connections for
        :returns: An iterator for the product connections.
        """
        if not product:
            raise ValueError
        sbSQL = ""

        # Parameter queries in python require ? instead of $ as in .net
        # It then takes an ordered list as 2nd arg in the execute call
        sbSQL += "SELECT " + Database.SqlFieldUserName + ", " + Database.SqlFieldMachineName + ", "
        sbSQL += Database.SqlFieldIpAddress + ", " + Database.SqlFieldLogonTime + ", "
        sbSQL += Database.SqlFieldUpdateTime + " "
        sbSQL += "FROM " + Database.SqlTableConnection + " "
        sbSQL += "WHERE " + Database.SqlFieldProduct + " = "
        sbSQL += "?" + " COLLATE NOCASE "
        sbSQL += "AND " + Database.SqlFieldUpdateTime + " > "
        sbSQL += "?" + ";"
        sbParameters = Database.ParameterLoggingSeparator.join([
            '0: ' + product.lower(),
            '1: ' + str(self.GetStaleTime())
        ])

        output_list = []
        try:
            # Create the connection with DataSource
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            indexOfUserName = 0
            indexOfMachineName = 1
            indexOfIpAddress = 2
            indexOfLogonTime = 3
            indexOfUpdateTime = 4
            for row in cursor.execute(sbSQL, (product.lower(), self.GetStaleTime())):
                ml = Message.UserRecordStruct()
                ml.User = row[indexOfUserName]
                ml.Host = row[indexOfMachineName]
                ml.IP = row[indexOfIpAddress]
                ml.LogonTime = row[indexOfLogonTime]
                ml.UpdateTime = row[indexOfUpdateTime]
                output_list.append(ml)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('GetConnections SQL Command: \'' + sbSQL + '\'')
            logging.critical('GetConnections SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        finally:
            logging.debug('GetConnections SQL Command: \'' + sbSQL + '\'')
            logging.debug('GetConnections SQL Parameters: \'' + sbParameters + '\'')
        return output_list

    def GetLicenceDetails(self, product: str) -> Message.LicenceStruct:
        if not product:
            raise ValueError
        messages = []
        sbSQL = ""

        # sbSQL += "SELECT * "

        sbSQL += "SELECT " + Database.SqlFieldId + ", "
        sbSQL += Database.SqlFieldCompany + ", "
        sbSQL += Database.SqlFieldProduct + ", "
        sbSQL += Database.SqlFieldCustomer + ", "
        sbSQL += Database.SqlFieldReference + ", "
        sbSQL += Database.SqlFieldReseller + ", "
        sbSQL += Database.SqlFieldNumberOfSeats + ", "
        sbSQL += Database.SqlFieldStartDate + ", "
        sbSQL += Database.SqlFieldExpiryDate + ", "
        sbSQL += Database.SqlFieldTimeStamp + ", "
        sbSQL += Database.SqlFieldCode + ", "
        sbSQL += Database.SqlFieldVersion + ", "
        sbSQL += Database.SqlFieldNotes + " "
        sbSQL += "FROM " + Database.SqlTableLicence + " "
        sbSQL += "WHERE " + Database.SqlFieldProduct + " = "
        sbSQL += "?" + "COLLATE NOCASE "
        sbSQL += "ORDER BY " + Database.SqlFieldTimeStamp + " DESC;"

        sbParameters = Database.ParameterLoggingSeparator.join([
            '0: ' + product.lower()
        ])

        ld = None
        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            indexOfLicenceID = 0
            indexOfCompany = 1
            indexOfProduct = 2
            indexOfCustomer = 3
            indexOfReference = 4
            indexOfReseller = 5
            indexOfNumberOfSeats = 6
            indexOfStartDate = 7
            indexOfExpiryDate = 8
            indexOfTimeStamp = 9
            indexOfCode = 10
            indexOfFieldVersion = 11
            indexOfFieldNotes = 12

            latestValidDate = date.min
            latestDate = date.min
            pl = ProductLicences()
            for row in cursor.execute(sbSQL, (product.lower(),)):
                # print("SQL 02")
                # print(row)
                lic = ElementTree.Element('Licence1')
                Company = ElementTree.SubElement(lic, 'Company')
                Company.text = row[indexOfCompany]
                Product = ElementTree.SubElement(lic, 'Product')
                Product.text = row[indexOfProduct]
                Customer = ElementTree.SubElement(lic, 'Customer')
                Customer.text = row[indexOfCustomer]
                Reference = ElementTree.SubElement(lic, 'Reference')
                if row[indexOfReference]:
                    Reference.text = row[indexOfReference]
                Reseller = ElementTree.SubElement(lic, 'Reseller')
                if row[indexOfReseller]:
                    Reseller.text = row[indexOfReseller]
                NumberOfSeats = ElementTree.SubElement(lic, 'NumberOfSeats')
                NumberOfSeats.text = str(row[indexOfNumberOfSeats])
                StartDate = ElementTree.SubElement(lic, 'StartDate')
                if row[indexOfStartDate]:
                    StartDate.text = row[indexOfStartDate]
                ExpiryDate = ElementTree.SubElement(lic, 'ExpiryDate')
                if row[indexOfExpiryDate]:
                    ExpiryDate.text = row[indexOfExpiryDate]
                TimeStamp = ElementTree.SubElement(lic, 'TimeStamp')
                TimeStamp.text = str(row[indexOfTimeStamp])
                ValidationCode = ElementTree.SubElement(lic, 'Code')
                ValidationCode.text = row[indexOfCode]
                Comments = ElementTree.SubElement(lic, 'Comments')
                if row[indexOfFieldNotes]:
                    Comments.text = row[indexOfFieldNotes]

                verified = True
                if self.m_DoubleValidation:
                    public_key_file = open(os.path.join(os.getcwd(), 'public_key.pem'))
                    public_key = public_key_file.read()
                    verified = LicenceReader.VerifyWithFile(public_key, lic)
                    if verified:
                        logging.debug('Licence with id: ' + str(row[indexOfLicenceID]) + ' verified.')
                    else:
                        logging.warning('Licence with id: ' + str(row[indexOfLicenceID]) + ' NOT VERIFIED.')
                if verified:
                    if ld is None:
                        ld = Message.LicenceStruct()
                        ld.Company = row[indexOfCompany]
                        ld.Product = row[indexOfProduct]
                        ld.Customer = row[indexOfCustomer]
                        if row[indexOfReference]:
                            ld.Ref = row[indexOfReference]
                        if row[indexOfReseller]:
                            ld.Reseller = row[indexOfReseller]
                    # We will persist the latest expiry date, this
                    # will only be used if all the licences expired...
                    if row[indexOfExpiryDate] and datetime.strptime(row[indexOfExpiryDate], "%d/%b/%Y").date() > latestDate:
                        latestDate = datetime.strptime(row[indexOfExpiryDate], "%d/%b/%Y").date()
                    # We will test the licence is within the current time period...
                    if not self.IsLicenceInDateWindow(lic, messages):
                        logging.info('Licence with id: ' + str(row[indexOfLicenceID]) + ' is not active.')
                    else:
                        # We will ensure only 1 perpetual licence is loaded...
                        if row[indexOfExpiryDate]:
                            pl.Add(LicenceSeatStructure(row[indexOfLicenceID], row[indexOfNumberOfSeats], False))
                            if datetime.strptime(row[indexOfExpiryDate], "%d/%b/%Y").date() > latestValidDate:
                                latestValidDate = datetime.strptime(row[indexOfExpiryDate], "%d/%b/%Y").date()
                        else:
                            if not pl.HasPerpetualLicence:
                                pl.Add(LicenceSeatStructure(row[indexOfLicenceID], row[indexOfNumberOfSeats], True))
            if ld is not None:
                if not pl.HasPerpetualLicence and latestValidDate > date.min:
                    dt = datetime.combine(latestValidDate, datetime.min.time())
                    ld.Date.FromDatetime(dt)
                ld.NumberOfSeats = pl.TotalSeats
                # We have only expired licences...
                if ld.NumberOfSeats == 0:
                    dt = datetime.combine(latestDate, datetime.min.time())
                    ld.Date.FromDatetime(dt)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('GetLicenceDetails SQL Command: \'' + sbSQL + '\'')
            logging.critical('GetLicenceDetails SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        finally:
            logging.debug('GetLicenceDetails SQL Command: \'' + sbSQL + '\'')
            logging.debug('GetLicenceDetails SQL Parameters: \'' + sbParameters + '\'')
        if ld is None:
            raise InvalidProductException('Invalid product: \'' + product + '\'')
        return ld

    def GetProducts(self) -> List[str]:
        """
        Returns a list of products in the database.

        :returns: An iterator for the products.
        """
        sbSQL = ""
        sbSQL += "SELECT " + Database.SqlFieldProduct + " "
        sbSQL += "FROM " + Database.SqlTableLicence + " "
        sbSQL += "GROUP BY " + Database.SqlFieldProduct + " "
        sbSQL += "ORDER BY " + Database.SqlFieldProduct + " ASC;"

        output_list = []
        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            indexOfProduct = 0
            for row in cursor.execute(sbSQL):
                # print("SQL 03")
                # print(row)
                output_list.append(row[indexOfProduct])
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('GetProducts SQL Command: \'' + sbSQL + '\'')
            raise
        finally:
            logging.debug('GetProducts SQL Command: \'' + sbSQL + '\'')
        return output_list

    def LoadLicences(self):
        """
        Loads the licences from the licence folder into the database.
        """
        licences = []
        timestamps = []

        for filename in os.listdir(self.GetLicenceFolder()):
            if not filename.endswith('.nls1'):
                continue
            reader = LicenceReader()
            reader.Read(filename)
            public_key_file = open(os.path.join(os.getcwd(), 'public_key.pem'))
            public_key = public_key_file.read()

            if not reader.Verify(public_key):
                logging.critical('Licence: \'' + filename + '\' NOT VERIFIED.')
            else:
                logging.debug('Licence: \'' + filename + '\' verified.')
                if reader.Licence1:
                    licences.append(reader.Licence1)
                    timestamps.append(str(reader.Licence1.find('TimeStamp').text))

        sbSQL = ""
        sbSQL += "INSERT OR IGNORE INTO " + Database.SqlTableLicence + "( "
        sbSQL += Database.SqlFieldCompany + ", "
        sbSQL += Database.SqlFieldProduct + ", "
        sbSQL += Database.SqlFieldCustomer + ", "
        sbSQL += Database.SqlFieldReference + ", "
        sbSQL += Database.SqlFieldReseller + ", "
        sbSQL += Database.SqlFieldNumberOfSeats + ", "
        sbSQL += Database.SqlFieldStartDate + ", "
        sbSQL += Database.SqlFieldExpiryDate + ", "
        sbSQL += Database.SqlFieldTimeStamp + ", "
        sbSQL += Database.SqlFieldCode + ", "
        sbSQL += Database.SqlFieldVersion + ", "
        sbSQL += Database.SqlFieldNotes + ") "

        sbSQL += "VALUES (" + "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ");"

        sbParameters = ""

        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            count = 0
            for lic in licences:
                Reference = None
                if lic.find('Reference') is not None:
                    Reference = lic.find('Reference').text
                Reseller = None
                if lic.find('Reseller') is not None:
                    Reseller = lic.find('Reseller').text
                StartDate = None
                if lic.find('StartDate') is not None:
                    StartDate = lic.find('StartDate').text
                ExpiryDate = None
                if lic.find('ExpiryDate') is not None:
                    ExpiryDate = lic.find('ExpiryDate').text
                Comments = None
                if lic.find('Comments') is not None:
                    Comments = lic.find('Comments').text
                parameters = (
                    lic.find('Company').text,
                    lic.find('Product').text,
                    lic.find('Customer').text,
                    Reference,
                    Reseller,
                    lic.find('NumberOfSeats').text,
                    StartDate,
                    ExpiryDate,
                    lic.find('TimeStamp').text,
                    lic.find('Code').text,
                    "1",
                    Comments,
                )
                sbParameters = Database.ParameterLoggingSeparator.join([
                    '0: ' + str(lic.find('Company').text),
                    '1: ' + str(lic.find('Product').text),
                    '2: ' + str(lic.find('Customer').text),
                    '3: ' + str(Reference),
                    '4: ' + str(Reseller),
                    '5: ' + str(lic.find('NumberOfSeats').text),
                    '6: ' + str(StartDate),
                    '7: ' + str(ExpiryDate),
                    '8: ' + str(lic.find('TimeStamp').text),
                    '9: ' + str(lic.find('Code').text),
                    '10: ' + "1",
                    '11: ' + str(Comments)
                ])
                cursor.execute(sbSQL, parameters)
                count += 1
                logging.debug('LoadLicences SQL Command: \'' + sbSQL + '\'')
                logging.debug('LoadLicences SQL Parameters: \'' + sbParameters + '\'')
            if count > 0:
                logging.info(str(count) + ' licence(s) loaded into database.')
            else:
                logging.debug(str(count) + ' licence(s) loaded into database.')
            sbSQL = "DELETE FROM " + Database.SqlTableLicence
            if len(timestamps) > 0:
                sbSQL += " "
                sbSQL += "WHERE " + Database.SqlFieldTimeStamp + " "
                sbSQL += "NOT IN ("
                sbSQL += ",".join(timestamps)
                sbSQL += ")"
            sbSQL += ";"
            cursor.execute(sbSQL)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('LoadLicences SQL Command: \'' + sbSQL + '\'')
            logging.critical('LoadLicences SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        logging.debug('Loaded licence(s).')

    def RefreshSeat(self, product: str, ipAddress: str, userName: str, host: str):
        """
        Sets the update time for the specified product, IP Address and
        user anme to the current time in the connection table.

        :param product: The name of the product to update the time for.
        :param ipAddress: The IP Address to update the time for.
        :param userName: The user name to update the time for.
        :param host: The host to update the time for.
        """
        if not product:
            raise ValueError
        if not ipAddress:
            raise ValueError
        if not userName:
            raise ValueError
        if not host:
            raise ValueError

        sbSQL = ""
        sbSQL += "INSERT OR IGNORE INTO " + Database.SqlTableConnection + "( "
        sbSQL += Database.SqlFieldProduct + ", "
        sbSQL += Database.SqlFieldUserName + ", "
        sbSQL += Database.SqlFieldIpAddress + ", "
        sbSQL += Database.SqlFieldMachineName + ", "
        sbSQL += Database.SqlFieldLogonTime + ", "
        sbSQL += Database.SqlFieldUpdateTime + ") "

        sbSQL += "VALUES (" + "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + "); "
        sbParameters = ""

        sbSQL_2 = ""
        sbSQL_2 += "UPDATE " + Database.SqlTableConnection + " "
        sbSQL_2 += "SET " + Database.SqlFieldUpdateTime + " = "
        sbSQL_2 += "?" + " "
        sbSQL_2 += "WHERE " + Database.SqlFieldProduct + " = "
        sbSQL_2 += "?" + " COLLATE NOCASE "
        sbSQL_2 += "AND " + Database.SqlFieldUserName + " = "
        sbSQL_2 += "?" + " "
        sbSQL_2 += "AND " + Database.SqlFieldIpAddress + " = "
        sbSQL_2 += "?" + ";"
        sbParameters_2 = ""

        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            nowTime = datetime.now()
            parameters = (
                product.lower(),
                userName,
                ipAddress,
                host,
                nowTime,
                nowTime
            )
            sbParameters = Database.ParameterLoggingSeparator.join([
                '0: ' + str(product.lower()),
                '1: ' + str(userName),
                '2: ' + str(ipAddress),
                '3: ' + str(host),
                '4: ' + str(nowTime),
                '5: ' + str(nowTime)
            ])
            parameters_2 = (
                nowTime,
                product.lower(),
                userName,
                ipAddress
            )
            sbParameters_2 = Database.ParameterLoggingSeparator.join([
                '0: ' + str(nowTime),
                '1: ' + str(product.lower()),
                '2: ' + str(userName),
                '3: ' + str(ipAddress)
            ])
            cursor.execute(sbSQL, parameters)
            cursor.execute(sbSQL_2, parameters_2)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('RefreshSeat SQL Command: \'' + sbSQL + '\'')
            logging.critical('RefreshSeat SQL Parameters: \'' + sbParameters + '\'')
            logging.critical('RefreshSeat SQL Command 2: \'' + sbSQL_2 + '\'')
            logging.critical('RefreshSeat SQL Parameters 2: \'' + sbParameters_2 + '\'')
            raise ex
        finally:
            logging.debug('RefreshSeat SQL Command: \'' + sbSQL + '\'')
            logging.debug('RefreshSeat SQL Parameters: \'' + sbParameters + '\'')
            logging.debug('RefreshSeat SQL Command 2: \'' + sbSQL_2 + '\'')
            logging.debug('RefreshSeat SQL Parameters 2: \'' + sbParameters_2 + '\'')

    def ReleaseSeat(self, product: str, ipAddress: str, userName: str) -> bool:
        """
        Deletes the line in the connection table for the specified product,
        IP Address and user name.

        :param product: The name of the product to delete the line for.
        :param ipAddress: The IP Address to delete the line for.
        :param userName: The user name to delete the line for.
        :returns: True if the line is deleted, otherwise false.
        """
        if not product:
            raise ValueError
        if not ipAddress:
            raise ValueError
        if not userName:
            raise ValueError

        sbSQL = ""

        # We will now delete any licences no longer in use...
        sbSQL += "DELETE FROM " + Database.SqlTableConnection + " "
        sbSQL += "WHERE " + Database.SqlFieldProduct + " = "
        sbSQL += "?" + " COLLATE NOCASE "
        sbSQL += "AND " + Database.SqlFieldUserName + " = "
        sbSQL += "?" + " "
        sbSQL += "AND " + Database.SqlFieldIpAddress + " = "
        sbSQL += "?" + ";"

        sbParameters = Database.ParameterLoggingSeparator.join([
            '0: ' + str(product.lower()),
            '1: ' + str(userName),
            '2: ' + str(ipAddress)
        ])

        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            parameters = (
                product.lower(),
                userName,
                ipAddress
            )
            cursor.execute(sbSQL, parameters)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('ReleaseSeat SQL Command: \'' + sbSQL + '\'')
            logging.critical('ReleaseSeat SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        finally:
            logging.debug('ReleaseSeat SQL Command: \'' + sbSQL + '\'')
            logging.debug('ReleaseSeat SQL Parameters: \'' + sbParameters + '\'')
        return True

    def TakeSeat(self, product: str, ipAddress: str, userName: str, host: str) -> bool:
        """
        Reads the number of licence seats available for the specified
        product, if a seat is available writes a line in the connection
        table for the specified product, IP Address, user njame and host.

        :param product: The name of the product to take the seat for.
        :param ipAddress: The IP Address to take the seat for.
        :param userName: The user name to take the seat for.
        :param host: The host to take the seat for.
        :returns: True if the seat is taken, otherwise false.
        """
        if not product:
            raise ValueError
        if not ipAddress:
            raise ValueError
        if not userName:
            raise ValueError
        if not host:
            raise ValueError

        messages = []
        sbSQL = ""
        takenSeat = False
        loggingCount = 1

        # This replaced a SELECT *
        sbSQL += "SELECT " + Database.SqlFieldId + ", "
        sbSQL += Database.SqlFieldCompany + ", "
        sbSQL += Database.SqlFieldProduct + ", "
        sbSQL += Database.SqlFieldCustomer + ", "
        sbSQL += Database.SqlFieldReference + ", "
        sbSQL += Database.SqlFieldReseller + ", "
        sbSQL += Database.SqlFieldNumberOfSeats + ", "
        sbSQL += Database.SqlFieldStartDate + ", "
        sbSQL += Database.SqlFieldExpiryDate + ", "
        sbSQL += Database.SqlFieldTimeStamp + ", "
        sbSQL += Database.SqlFieldCode + ", "
        sbSQL += Database.SqlFieldVersion + ", "
        sbSQL += Database.SqlFieldNotes + " "
        sbSQL += "FROM " + Database.SqlTableLicence + " "
        sbSQL += "WHERE " + Database.SqlFieldProduct + " = "
        sbSQL += "?" + " COLLATE NOCASE "
        # We will ensure that licences are read latest to earliest,
        # to ensure that only the latest perpetual licence is used...
        sbSQL += "ORDER BY " + Database.SqlFieldTimeStamp + " DESC;"

        pl = ProductLicences()
        try:
            staleTime = self.GetStaleTime()
            nowTime = datetime.now()
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            parameters = (
                product.lower(),
            )
            sbParameters = Database.ParameterLoggingSeparator.join([
                '0: ' + str(product.lower())
            ])
            logging.debug('TakeSeat SQL Command #' + str(loggingCount) + ': \'' + sbSQL + '\'')
            logging.debug('TakeSeat SQL Parameters #' + str(loggingCount) + ': \'' + sbParameters + '\'')
            indexOfLicenceID = 0
            indexOfCompany = 1
            indexOfProduct = 2
            indexOfCustomer = 3
            indexOfReference = 4
            indexOfReseller = 5
            indexOfNumberOfSeats = 6
            indexOfStartDate = 7
            indexOfExpiryDate = 8
            indexOfTimeStamp = 9
            indexOfCode = 10
            indexOfFieldVersion = 11
            indexOfFieldNotes = 12
            for row in cursor.execute(sbSQL, parameters):
                lic = ElementTree.Element('Licence1')
                Company = ElementTree.SubElement(lic, 'Company')
                Company.text = row[indexOfCompany]
                Product = ElementTree.SubElement(lic, 'Product')
                Product.text = row[indexOfProduct]
                Customer = ElementTree.SubElement(lic, 'Customer')
                Customer.text = row[indexOfCustomer]
                Reference = ElementTree.SubElement(lic, 'Reference')
                if row[indexOfReference]:
                    Reference.text = row[indexOfReference]
                Reseller = ElementTree.SubElement(lic, 'Reseller')
                if row[indexOfReseller]:
                    Reseller.text = row[indexOfReseller]
                NumberOfSeats = ElementTree.SubElement(lic, 'NumberOfSeats')
                NumberOfSeats.text = str(row[indexOfNumberOfSeats])
                StartDate = ElementTree.SubElement(lic, 'StartDate')
                if row[indexOfStartDate]:
                    StartDate.text = row[indexOfStartDate]
                ExpiryDate = ElementTree.SubElement(lic, 'ExpiryDate')
                if row[indexOfExpiryDate]:
                    ExpiryDate.text = row[indexOfExpiryDate]
                TimeStamp = ElementTree.SubElement(lic, 'TimeStamp')
                TimeStamp.text = str(row[indexOfTimeStamp])
                ValidationCode = ElementTree.SubElement(lic, 'Code')
                ValidationCode.text = row[indexOfCode]
                Comments = ElementTree.SubElement(lic, 'Comments')
                if row[indexOfFieldNotes]:
                    Comments.text = row[indexOfFieldNotes]

                verified = True
                if self.m_DoubleValidation:
                    public_key_file = open(os.path.join(os.getcwd(), 'public_key.pem'))
                    public_key = public_key_file.read()
                    verified = LicenceReader.VerifyWithFile(public_key, lic)
                    if verified:
                        logging.debug('Licence with id: ' + str(row[indexOfLicenceID]) + ' verified.')
                    else:
                        logging.warning('Licence with id: ' + str(row[indexOfLicenceID]) + ' NOT VERIFIED.')
                if verified:
                    # We will test the licence is within the current time period...
                    if not self.IsLicenceInDateWindow(lic, messages):
                        logging.info('Licence with id: ' + str(row[indexOfLicenceID]) + ' is not active.')
                    else:
                        # We will ensure only 1 perpetual licence is loaded...
                        if row[indexOfExpiryDate]:
                            pl.Add(LicenceSeatStructure(row[indexOfLicenceID], row[indexOfNumberOfSeats], False))
                        else:
                            if not pl.HasPerpetualLicence:
                                pl.Add(LicenceSeatStructure(row[indexOfLicenceID], row[indexOfNumberOfSeats], True))
            if pl is not None:
                pl.Sort()
                # * shouldn't matter since it's a count?
                sbSQL = "SELECT COUNT (*) "
                sbSQL += "FROM " + Database.SqlTableConnection + " "
                sbSQL += "WHERE ( " + Database.SqlFieldProduct + " = "
                sbSQL += "?" + " COLLATE NOCASE "
                sbSQL += "AND " + Database.SqlFieldUpdateTime + " > "
                sbSQL += "?" + ") "
                sbSQL += "AND NOT (" + Database.SqlFieldUserName + " = "
                sbSQL += "?" + " "
                sbSQL += "AND " + Database.SqlFieldIpAddress + " = "
                sbSQL += "?" + ");"
                parameters = (
                    product.lower(),
                    staleTime,
                    userName,
                    ipAddress
                )
                sbParameters = Database.ParameterLoggingSeparator.join([
                    '0: ' + str(product.lower()),
                    '1: ' + str(staleTime),
                    '2: ' + str(userName),
                    '3: ' + str(ipAddress)
                ])
                cursor.execute(sbSQL, parameters)
                takenSeats = cursor.fetchone()[0]

                loggingCount += 1
                logging.debug('TakeSeat SQL Command #' + str(loggingCount) + ': \'' + sbSQL + '\'')
                logging.debug('TakeSeat SQL Parameters #' + str(loggingCount) + ': \'' + sbParameters + '\'')

                if takenSeats >= pl.TotalSeats:
                    return False
                licenceId = pl.LicenceSeats[0].LicenceID
                if len(pl.LicenceSeats) > 1:
                    sbSQL = "SELECT COUNT(*) "
                    sbSQL += "FROM " + Database.SqlTableConnection + " "
                    sbSQL += "WHERE (" + Database.SqlTableLicence + Database.SqlFieldForeignKeyId + " = "
                    sbSQL += "?" + " "
                    sbSQL += "AND " + Database.SqlFieldUpdateTime + " > "
                    sbSQL += "?" + ") "
                    sbSQL += "AND NOT (" + Database.SqlFieldUserName + " = "
                    sbSQL += "?" + " "
                    sbSQL += "AND " + Database.SqlFieldIpAddress + " = "
                    sbSQL += "?" + ");"
                    for ls in pl.LicenceSeats:
                        parameters = (
                            ls.LicenceID,
                            staleTime,
                            userName,
                            ipAddress
                        )
                        sbParameters = Database.ParameterLoggingSeparator.join([
                            '0: ' + str(ls.LicenceID),
                            '1: ' + str(staleTime),
                            '2: ' + str(userName),
                            '3: ' + str(ipAddress)
                        ])
                        cursor.execute(sbSQL, parameters)
                        takenSeats = cursor.fetchone()[0]

                        loggingCount += 1
                        logging.debug('TakeSeat SQL Command #' + str(loggingCount) + ': \'' + sbSQL + '\'')
                        logging.debug('TakeSeat SQL Parameters #' + str(loggingCount) + ': \'' + sbParameters + '\'')

                        if takenSeats < ls.Seats:
                            licenceId = ls.LicenceID

                # The following 2 commands are split from 1 command in .NET version
                # Python sqlite3 does not support multiple statement in 1 execute
                sbSQL = "INSERT OR IGNORE INTO " + Database.SqlTableConnection + "( "
                sbSQL += Database.SqlFieldProduct + ", "
                sbSQL += Database.SqlFieldUserName + ", "
                sbSQL += Database.SqlFieldIpAddress + ", "
                sbSQL += Database.SqlFieldMachineName + ", "
                sbSQL += Database.SqlFieldLogonTime + ", "
                sbSQL += Database.SqlFieldUpdateTime + ", "
                sbSQL += Database.SqlTableLicence + Database.SqlFieldForeignKeyId + ") "

                sbSQL += "VALUES (" + "?" + ", "
                sbSQL += "?" + ", "
                sbSQL += "?" + ", "
                sbSQL += "?" + ", "
                sbSQL += "?" + ", "
                sbSQL += "?" + ", "
                sbSQL += "?" + "); "
                parameters = (
                    product.lower(),
                    userName,
                    ipAddress,
                    host,
                    nowTime,
                    nowTime,
                    licenceId
                )
                sbParameters = Database.ParameterLoggingSeparator.join([
                    '0: ' + str(product.lower()),
                    '1: ' + str(userName),
                    '2: ' + str(ipAddress),
                    '3: ' + str(host),
                    '4: ' + str(nowTime),
                    '5: ' + str(nowTime),
                    '6: ' + str(licenceId)
                ])

                loggingCount += 1
                logging.debug('TakeSeat SQL Command #' + str(loggingCount) + ': \'' + sbSQL + '\'')
                logging.debug('TakeSeat SQL Parameters #' + str(loggingCount) + ': \'' + sbParameters + '\'')

                cursor.execute(sbSQL, parameters)

                sbSQL = "UPDATE " + Database.SqlTableConnection + " "
                sbSQL += "SET " + Database.SqlFieldMachineName + " = "
                sbSQL += "?" + ", "
                sbSQL += Database.SqlFieldUpdateTime + " = "
                sbSQL += "?" + ", "
                sbSQL += Database.SqlTableLicence + Database.SqlFieldForeignKeyId + " = "
                sbSQL += "?" + " "
                sbSQL += "WHERE " + Database.SqlFieldProduct + " = "
                sbSQL += "?" + " COLLATE NOCASE "
                sbSQL += "AND " + Database.SqlFieldUserName + " = "
                sbSQL += "?" + " "
                sbSQL += "AND " + Database.SqlFieldIpAddress + " = "
                sbSQL += "?" + ";"

                parameters = (
                    host,
                    nowTime,
                    licenceId,
                    product.lower(),
                    userName,
                    ipAddress
                )
                sbParameters = Database.ParameterLoggingSeparator.join([
                    '0: ' + str(host),
                    '1: ' + str(nowTime),
                    '2: ' + str(licenceId),
                    '3: ' + str(product.lower()),
                    '4: ' + str(userName),
                    '5: ' + str(ipAddress)
                ])

                # Logging number is given .1 to indicate it's a split command
                logging.debug('TakeSeat SQL Command #' + str(loggingCount) + '.1: \'' + sbSQL + '\'')
                logging.debug('TakeSeat SQL Parameters #' + str(loggingCount) + '.1: \'' + sbParameters + '\'')
                cursor.execute(sbSQL, parameters)
            connection.commit()
            takenSeat = True
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('TakeSeat SQL Command: \'' + sbSQL + '\'')
            logging.critical('TakeSeat SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        if pl is None:
            raise InvalidProductException('Invalid product: \'' + product + '\'')
        return takenSeat

    def TotalSeats(self, product: str) -> int:
        """
        Returns the total number of licences for the specified product.

        :param product: the name of the product to get the total number of licences for.
        :returns: The total number of licences.
        """
        if not product:
            raise ValueError

        messages = []
        sbSQL = ""

        # This replaced a SELECT *
        sbSQL += "SELECT " + Database.SqlFieldId + ", "
        sbSQL += Database.SqlFieldCompany + ", "
        sbSQL += Database.SqlFieldProduct + ", "
        sbSQL += Database.SqlFieldCustomer + ", "
        sbSQL += Database.SqlFieldReference + ", "
        sbSQL += Database.SqlFieldReseller + ", "
        sbSQL += Database.SqlFieldNumberOfSeats + ", "
        sbSQL += Database.SqlFieldStartDate + ", "
        sbSQL += Database.SqlFieldExpiryDate + ", "
        sbSQL += Database.SqlFieldTimeStamp + ", "
        sbSQL += Database.SqlFieldCode + ", "
        sbSQL += Database.SqlFieldVersion + ", "
        sbSQL += Database.SqlFieldNotes + " "
        sbSQL += "FROM " + Database.SqlTableLicence + " "
        sbSQL += "WHERE " + Database.SqlFieldProduct + " = "
        sbSQL += "?" + " COLLATE NOCASE "
        sbSQL += "ORDER BY " + Database.SqlFieldTimeStamp + " DESC;"
        parameters = (
            product.lower(),
        )
        sbParameters = Database.ParameterLoggingSeparator.join([
            '0: ' + str(product.lower())
        ])

        pl = None
        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            indexOfLicenceID = 0
            indexOfCompany = 1
            indexOfProduct = 2
            indexOfCustomer = 3
            indexOfReference = 4
            indexOfReseller = 5
            indexOfNumberOfSeats = 6
            indexOfStartDate = 7
            indexOfExpiryDate = 8
            indexOfTimeStamp = 9
            indexOfCode = 10
            indexOfFieldVersion = 11
            indexOfFieldNotes = 12
            for row in cursor.execute(sbSQL, parameters):
                if pl is None:
                    pl = ProductLicences()
                lic = ElementTree.Element('Licence1')
                Company = ElementTree.SubElement(lic, 'Company')
                Company.text = row[indexOfCompany]
                Product = ElementTree.SubElement(lic, 'Product')
                Product.text = row[indexOfProduct]
                Customer = ElementTree.SubElement(lic, 'Customer')
                Customer.text = row[indexOfCustomer]
                Reference = ElementTree.SubElement(lic, 'Reference')
                if row[indexOfReference]:
                    Reference.text = row[indexOfReference]
                Reseller = ElementTree.SubElement(lic, 'Reseller')
                if row[indexOfReseller]:
                    Reseller.text = row[indexOfReseller]
                NumberOfSeats = ElementTree.SubElement(lic, 'NumberOfSeats')
                NumberOfSeats.text = str(row[indexOfNumberOfSeats])
                StartDate = ElementTree.SubElement(lic, 'StartDate')
                if row[indexOfStartDate]:
                    StartDate.text = row[indexOfStartDate]
                ExpiryDate = ElementTree.SubElement(lic, 'ExpiryDate')
                if row[indexOfExpiryDate]:
                    ExpiryDate.text = row[indexOfExpiryDate]
                TimeStamp = ElementTree.SubElement(lic, 'TimeStamp')
                TimeStamp.text = str(row[indexOfTimeStamp])
                ValidationCode = ElementTree.SubElement(lic, 'Code')
                ValidationCode.text = row[indexOfCode]
                Comments = ElementTree.SubElement(lic, 'Comments')
                if row[indexOfFieldNotes]:
                    Comments.text = row[indexOfFieldNotes]

                verified = True
                if self.m_DoubleValidation:
                    public_key_file = open(os.path.join(os.getcwd(), 'public_key.pem'))
                    public_key = public_key_file.read()
                    verified = LicenceReader.VerifyWithFile(public_key, lic)
                    if verified:
                        logging.debug('Licence with id: ' + str(row[indexOfLicenceID]) + ' verified.')
                    else:
                        logging.warning('Licence with id: ' + str(row[indexOfLicenceID]) + ' NOT VERIFIED.')
                if verified:
                    # We will test the licence is within the current time period...
                    if not self.IsLicenceInDateWindow(lic, messages):
                        logging.info('Licence with id: ' + str(row[indexOfLicenceID]) + ' is not active.')
                    else:
                        # We will ensure only 1 perpetual licence is loaded...
                        if row[indexOfExpiryDate]:
                            pl.Add(LicenceSeatStructure(row[indexOfLicenceID], row[indexOfNumberOfSeats], False))
                        else:
                            if not pl.HasPerpetualLicence:
                                pl.Add(LicenceSeatStructure(row[indexOfLicenceID], row[indexOfNumberOfSeats], True))
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('TotalSeats SQL Command: \'' + sbSQL + '\'')
            logging.critical('TotalSeats SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        finally:
            logging.debug('TotalSeats SQL Command: \'' + sbSQL + '\'')
            logging.debug('TotalSeats SQL Parameters: \'' + sbParameters + '\'')
        if pl is None:
            raise InvalidProductException('Invalid product: \'' + product + '\'')
        return pl.TotalSeats

    # Private Methods

    def AnalyzeDatabase(self):
        """
        Runs the ANALYZE command on the database.
        The ANALYZE command scans all indices of a database where
        there might be a choice between two or more indices and gathers
        statistics on the selectiveness of those indices. The results of
        this scan are stored in the sqlite_stat1 table. The contents
        of the sqlite_stat1 table are not updated as the database changes so after
        making significant changes it might be prudent to rerun ANALYZE.
        """
        commandText = "ANALYZE;"
        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            cursor.execute(commandText)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('AnalyzeDatabase SQL Command: \'' + commandText + '\'')
            raise ex
        finally:
            logging.debug('AnalyzeDatabase SQL Command: \'' + commandText + '\'')
        logging.debug('Analyzed database.')

    def CreateDatabase(self):
        """
        Creates the licence manager database schema.
        """
        sql_LicenceSchema = DatabaseSchema.GetLicenceSchema()
        sql_ConnectionSchema = DatabaseSchema.GetConnectionSchema()
        sql_SiteLogSchema = DatabaseSchema.GetSiteLogSchema()

        sbSQL = ""
        sbSQL += "INSERT INTO " + Database.SqlTableSiteLog + " "
        sbSQL += "(" + Database.SqlFieldInstallDate + ", "
        sbSQL += Database.SqlFieldVersion + ", "
        sbSQL += Database.SqlFieldNotes + ", "
        sbSQL += Database.SqlFieldReleaseDate + ") "
        sbSQL += "VALUES (" + "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + ", "
        sbSQL += "?" + "); "
        parameters = (
            datetime.now(),
            Database.Version,
            "Version " + str(Database.Version) + " installed",
            datetime.strptime(Database.ReleaseDate, "%d/%b/%Y %H:%M")
        )
        sbParameters = Database.ParameterLoggingSeparator.join([
            '0: ' + str(datetime.now()),
            '1: ' + str(Database.Version),
            '2: ' + "Version " + str(Database.Version) + " installed",
            '3: ' + str(datetime.strptime(Database.ReleaseDate, "%d/%b/%Y %H:%M"))
        ])

        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            try:
                cursor.executescript(sql_LicenceSchema)
            except sqlite3.OperationalError:
                logging.debug('Table \'licence\' already exists')
            try:
                cursor.executescript(sql_ConnectionSchema)
            except sqlite3.OperationalError:
                logging.debug('Table \'connection\' already exists')
            try:
                cursor.executescript(sql_SiteLogSchema)
                cursor.execute(sbSQL, parameters)
            except sqlite3.OperationalError:
                logging.debug('Table \'site_log\' already exists')
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('CreateDatabase SQL Command: \'' + sbSQL + '\'')
            logging.critical('CreateDatabase SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        finally:
            logging.debug('CreateDatabase SQL Command 1: \'' + sql_LicenceSchema + '\'')
            logging.debug('CreateDatabase SQL Command 2: \'' + sql_ConnectionSchema + '\'')
            logging.debug('CreateDatabase SQL Command 3: \'' + sql_SiteLogSchema + '\'')
            logging.debug('CreateDatabase SQL Command 4: \'' + sbSQL + '\'')
            logging.debug('CreateDatabase SQL Parameters: \'' + sbParameters + '\'')
        logging.info('Created database schema.')

    def DeleteStaleSeats(self):
        """
        Deletes all stale seats from the connection table.
        """
        sbSQL = ""
        sbSQL += "DELETE FROM " + Database.SqlTableConnection + " "
        sbSQL += "WHERE " + Database.SqlFieldUpdateTime + " < "
        sbSQL += "?" + ";"
        parameters = (
            self.GetStaleTime(),
        )
        sbParameters = Database.ParameterLoggingSeparator.join([
            '0: ' + str(self.GetStaleTime()),
        ])

        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            cursor.execute(sbSQL, parameters)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('DeleteStaleSeats SQL Command: \'' + sbSQL + '\'')
            logging.critical('DeleteStaleSeats SQL Parameters: \'' + sbParameters + '\'')
            raise ex
        finally:
            logging.debug('DeleteStaleSeats SQL Command: \'' + sbSQL + '\'')
            logging.debug('DeleteStaleSeats SQL Parameters: \'' + sbParameters + '\'')
        logging.info('Deleted stale seat(s)')

    def GetConnectionString(self) -> str:
        """
        Returns a connection string to the database.

        :returns: A connection string to the database.
        """
        connection_string = os.path.join(self.GetDataFolder(), Database.FileName)
        if self.m_EncryptDatabase:
            # TODO confirm what to do in this case
            pass
        return connection_string

    def GetDataFolder(self) -> str:
        """
        Returns the full path to the data folder.

        :returns: The full path to the data folder.
        """
        if not self.m_DataFolder:
            return Utils.GetExecutingFilePath()
        return os.path.join(Utils.GetExecutingFilePath(), self.m_DataFolder)

    def GetLicenceFolder(self) -> str:
        """
        Returns the full path to the licence folder.

        :returns: The full path to the licence folder.
        """
        if not self.m_LicenceFolder:
            return Utils.GetExecutingFilePath()
        return os.path.join(Utils.GetExecutingFilePath(), self.m_LicenceFolder)

    def GetStaleTime(self) -> datetime:
        """
        Returns a date and time that can be used to compare if seats have gone stale.

        :returns: A date and time that can be used to compare if seats have gone stale.
        """
        return datetime.now() - (self.m_HeartBeat + timedelta(seconds=self.FudgeFactor))

    def VacuumDatabase(self):
        """
        Runs the VACUUM command on the database.
        When an object (table, index or trigger) is dropped from
        the database, it leaves behind empty space. This makes the database
        file larger than it needs to be, but can speed up inserts. In time
        inserts and deletes can leave the database file structure fragmented,
        which slows down disk access to the database contents. The VACUUM
        command cleans the main database by copying its contents to a
        temporary database file and reloading the original database file
        from the copy. This eliminates free pages, aligns table data to be
        contiguous, and otherwise cleans up the database file structure.
        """
        commandText = "VACUUM;"
        try:
            connection = sqlite3.connect(self.GetConnectionString())
            cursor = connection.cursor()
            cursor.execute(commandText)
            connection.commit()
        except Exception as ex:
            logging.critical(str(ex))
            logging.critical('VacuumDatabase SQL Command: \'' + commandText + '\'')
            raise ex
        finally:
            logging.debug('VacuumDatabase SQL Command: \'' + commandText + '\'')
        logging.info('Vacuumed database.')

    def IsLicenceInDateWindow(self, value: ElementTree.Element, errorMessages: list) -> bool:
        """
        Tests the specified licence start and expiry dates to see if they are within the date window.

        :param value: The licence to test.
        :param errorMessages: List of error messages to log to.
        :returns: True if the start and expiry dates are within the date window, otherwise false.
        """
        afterStartDate = True
        beforeExpiryDate = True
        dateToday = datetime.now()
        logging.debug('Current date for testing if licence is active: \'' + dateToday.strftime("%d/%b/%Y") + '\'')
        if not value.find('StartDate').text:
            logging.debug('Licence has no start date.')
        else:
            logging.debug('Licence start date: \'' + value.find('StartDate').text + '\'')
            afterStartDate = dateToday > datetime.strptime(value.find('StartDate').text, "%d/%b/%Y")
        if not value.find('ExpiryDate').text:
            logging.debug('Licence has no expiry date.')
        else:
            logging.debug('Licence expiry date: \'' + value.find('ExpiryDate').text + '\'')
            beforeExpiryDate = dateToday < datetime.strptime(value.find('ExpiryDate').text, "%d/%b/%Y")
        if not afterStartDate:
            logging.debug('Licence is not yet active')
        if not beforeExpiryDate:
            logging.debug('Licence has expired')
        return afterStartDate and beforeExpiryDate

# Private ProductLicences (helper) class


class LicenceSeatStructure:
    m_LicenceId: int
    m_Seats: int
    m_IsPerpetualLicence: bool

    @property
    def IsPerpetualLicence(self) -> bool:
        return self.m_IsPerpetualLicence

    @property
    def LicenceID(self) -> int:
        return self.m_LicenceId

    @property
    def Seats(self) -> int:
        return self.m_Seats

    def __init__(self, licenceId: int, seats: int, isPerpetualLicence: bool):
        self.m_LicenceId = licenceId
        self.m_Seats = seats
        self.m_IsPerpetualLicence = isPerpetualLicence


class ProductLicences:
    m_LicenceSeats = []

    @property
    def HasPerpetualLicence(self) -> bool:
        for ls in self.m_LicenceSeats:
            if ls.IsPerpetualLicence:
                return True
        return False

    @property
    def LicenceSeats(self) -> list:
        return self.m_LicenceSeats

    @property
    def TotalSeats(self) -> int:
        seats = 0
        for ls in self.m_LicenceSeats:
            seats += ls.Seats
        return seats

    def Add(self, value: LicenceSeatStructure):
        self.m_LicenceSeats.append(value)

    def Sort(self):
        def LicenceSeatStructureComparer(licence_seat):
            if licence_seat.IsPerpetualLicence:
                return -1
            return licence_seat.Seats
        self.m_LicenceSeats.sort(key=LicenceSeatStructureComparer)

    def __init__(self):
        self.m_LicenceSeats = []
