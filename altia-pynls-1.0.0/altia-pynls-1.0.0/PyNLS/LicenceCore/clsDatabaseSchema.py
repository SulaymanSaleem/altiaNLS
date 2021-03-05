class DatabaseSchema:
    """
    Provides static methods for the database schema.
    """
    @staticmethod
    def GetConnectionSchema() -> str:
        """
        Returns an SQL statement to create the connection database table.

        :returns: An SQL statement to create the connection database table.
        """
        sql_string = "CREATE TABLE " + Database.SqlTableConnection + "("
        sql_string += Database.SqlFieldId + " INTEGER PRIMARY KEY, "
        sql_string += Database.SqlFieldIpAddress + " VARCHAR(64) NOT NULL, "
        sql_string += Database.SqlFieldMachineName + " VARCHAR(32) NOT NULL, "
        sql_string += Database.SqlFieldUserName + " VARCHAR(128) NOT NULL, "
        sql_string += Database.SqlFieldLogonTime + " DATETIME NOT NULL, "
        sql_string += Database.SqlFieldUpdateTime + " DATETIME NOT NULL, "
        sql_string += Database.SqlFieldProduct + " VARCHAR(32) NOT NULL, "
        sql_string += Database.SqlTableLicence + Database.SqlFieldForeignKeyId + " INTEGER NULL, "
        sql_string += "FOREIGN KEY(" + Database.SqlTableLicence + Database.SqlFieldForeignKeyId + ") REFERENCES "
        sql_string += Database.SqlTableLicence + "(" + Database.SqlFieldId + ") ON DELETE CASCADE"
        sql_string += "); "

        # Indexes
        sql_string += "CREATE UNIQUE INDEX idx_" + Database.SqlTableConnection + "_" + Database.SqlFieldProduct + "_"
        sql_string += Database.SqlFieldUserName + "_" + Database.SqlFieldIpAddress + " ON "
        sql_string += Database.SqlTableConnection + "("
        sql_string += Database.SqlFieldProduct + " COLLATE NOCASE, "
        sql_string += Database.SqlFieldUserName + ", "
        sql_string += Database.SqlFieldIpAddress + "); "

        sql_string += "CREATE INDEX idx_" + Database.SqlTableConnection + "_" + Database.SqlFieldProduct + "_"
        sql_string += Database.SqlFieldUpdateTime + " ON "
        sql_string += Database.SqlTableConnection + "("
        sql_string += Database.SqlFieldProduct + " COLLATE NOCASE, "
        sql_string += Database.SqlFieldUpdateTime + "); "

        sql_string += "CREATE INDEX idx_" + Database.SqlTableConnection + "_" + Database.SqlTableLicence
        sql_string += Database.SqlFieldForeignKeyId + "_" + Database.SqlFieldUpdateTime + " ON "
        sql_string += Database.SqlTableConnection + "("
        sql_string += Database.SqlTableLicence + Database.SqlFieldForeignKeyId + ", "
        sql_string += Database.SqlFieldUpdateTime + "); "
        return sql_string

    @staticmethod
    def GetLicenceSchema() -> str:
        """
        Returns an SQL statement to create the licence database table.

        :returns: An SQL statement to create the licence database table.
        """
        # Table
        sql_string = "CREATE TABLE " + Database.SqlTableLicence + "("
        sql_string += Database.SqlFieldId + " INTEGER PRIMARY KEY, "
        sql_string += Database.SqlFieldCompany + " VARCHAR(32) NOT NULL, "
        sql_string += Database.SqlFieldProduct + " VARCHAR(32) NOT NULL, "
        sql_string += Database.SqlFieldCustomer + " VARCHAR(128) NOT NULL, "
        sql_string += Database.SqlFieldReference + " VARCHAR(32) NULL, "
        sql_string += Database.SqlFieldReseller + " VARCHAR(128) NULL, "
        sql_string += Database.SqlFieldNumberOfSeats + " INTEGER NOT NULL, "
        sql_string += Database.SqlFieldStartDate + " DATETIME, "
        sql_string += Database.SqlFieldExpiryDate + " DATETIME, "
        sql_string += Database.SqlFieldTimeStamp + " INTEGER NOT NULL, "
        sql_string += Database.SqlFieldCode + " VARCHAR(256) NOT NULL, "
        sql_string += Database.SqlFieldVersion + " INTEGER NOT NULL, "
        sql_string += Database.SqlFieldNotes + " TEXT); "

        # Indexes
        sql_string += "CREATE UNIQUE INDEX idx_" + Database.SqlTableLicence + "_" + Database.SqlFieldTimeStamp + " ON "
        sql_string += Database.SqlTableLicence + "("
        sql_string += Database.SqlFieldTimeStamp + "); "

        sql_string += "CREATE INDEX idx_" + Database.SqlTableLicence + "_" + Database.SqlFieldProduct + "_"
        sql_string += Database.SqlFieldTimeStamp + " ON "
        sql_string += Database.SqlTableLicence + "("
        sql_string += Database.SqlFieldProduct + " COLLATE NOCASE, "
        sql_string += Database.SqlFieldTimeStamp + " DESC); "

        sql_string += "CREATE INDEX idx_" + Database.SqlTableLicence + "_" + Database.SqlFieldExpiryDate + " ON "
        sql_string += Database.SqlTableLicence + "("
        sql_string += Database.SqlFieldExpiryDate + "); "

        sql_string += "CREATE INDEX idx_" + Database.SqlTableLicence + "_" + Database.SqlFieldStartDate + " ON "
        sql_string += Database.SqlTableLicence + "("
        sql_string += Database.SqlFieldStartDate + "); "
        return sql_string

    @staticmethod
    def GetSiteLogSchema() -> str:
        """
        Returns an SQL statement to create the site log database table.

        :returns: An SQL statement to create the site log database table.
        """
        sql_string = "CREATE TABLE " + Database.SqlTableSiteLog + "("
        sql_string += Database.SqlFieldId + " INTEGER PRIMARY KEY, "
        sql_string += Database.SqlFieldInstallDate + " DATETIME NOT NULL, "
        sql_string += Database.SqlFieldVersion + " INTEGER NOT NULL, "
        sql_string += Database.SqlFieldNotes + " TEXT NOT NULL, "
        sql_string += Database.SqlFieldReleaseDate + " DATETIME NOT NULL"
        sql_string += "); "
        return sql_string


class Database:
    ParameterChar = "$"
    Version = 1
    ReleaseDate = "04/Sep/2014 16:44"  # TODO check
    FileName = "Data.db3"
    ParameterLoggingSeparator = ", "

    # Tables
    SqlTableLicence = "licence"
    SqlTableConnection = "connection"
    SqlTableSiteLog = "site_log"

    # Misc Fields
    SqlFieldNotes = "notes"
    SqlFieldId = "id"
    SqlFieldForeignKeyId = "_id"
    SqlFieldProduct = "product"
    SqlFieldVersion = "version"

    # Site Log Fields
    SqlFieldInstallDate = "install_date"
    SqlFieldReleaseDate = "release_date"

    # Licence Fields
    SqlFieldCompany = "company"
    SqlFieldCustomer = "customer"
    SqlFieldReference = "reference"
    SqlFieldReseller = "reseller"
    SqlFieldNumberOfSeats = "seats"
    SqlFieldStartDate = "start_date"
    SqlFieldExpiryDate = "expiry_date"
    SqlFieldTimeStamp = "timestamp"
    SqlFieldCode = "code"

    # Connection Fields
    SqlFieldIpAddress = "ip"
    SqlFieldMachineName = "host"
    SqlFieldUserName = "user"
    SqlFieldLogonTime = "logon_time"
    SqlFieldUpdateTime = "update_time"
