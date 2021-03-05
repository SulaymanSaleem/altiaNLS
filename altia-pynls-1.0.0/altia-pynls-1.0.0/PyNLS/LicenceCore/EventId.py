from enum import Enum


class EventId(Enum):
    ServiceStart = 1000
    ServiceStartMessage = 1001
    ServiceStartError = 1002
    ServiceShutdown = 1005
    ServiceShutdownError = 1006

    SeatRefreshed = 1010
    SeatReleased = 1011
    SeatNotReleased = 1012
    SeatTaken = 1013
    SeatNotTaken = 1014
    TakeSeatError = 1015
    ConnectionInfoError = 1016

    NumberOfSeatsError = 1020
    SeatRefreshedError = 1021
    SeatReleasedError = 1022

    LicenceLoad = 1030
    LicenceDelete = 1031
    LicenceInfoError = 1032
    LicenceDailyReload = 1033
    LicenceVerificationError = 1034
    LicenceNotActiveMessage = 1035
    LicenceUploadError = 1036

    InvalidProduct = 1040

    DataFolderCreated = 1050
    LicenceFolderCreated = 1051
    DatabaseSchemaCreated = 1052

    GetConnectionsSQLError = 1060
    GetLicenceDetailsSQLError = 1061
    GetProductsSQLError = 1062
    LoadLicenceSQLError = 1063
    RefreshSeatSQLError = 1064
    ReleaseSeatSQLError = 1065
    TakeSeatSQLError = 1066
    TotalSeatSQLError = 1067
    AnalyseSQLError = 1068
    VacuumSQLError = 1069
    CreateDatabaseSQLError = 1070
    DeleteStaleSeatSQLError = 1071
    ZeroMQError = 1072

    ServerVersion = 1090
    WebServerAddress = 1091
