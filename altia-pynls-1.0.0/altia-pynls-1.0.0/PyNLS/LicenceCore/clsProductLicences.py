from typing import List, NamedTuple
import sys


class LicenceSeatStructure(NamedTuple):
    m_LicenceId: int
    m_Seats: int
    m_IsPerpetualLicence: bool

    @property
    def IsPerpetualLicence(self) -> bool:
        return self.m_IsPerpetualLicence

    @property
    def LicenceId(self) -> int:
        return self.m_LicenceId

    @property
    def Seats(self) -> int:
        return self.m_Seats


class ProductLicences:
    m_LicenceSeats = List[LicenceSeatStructure]

    @property
    def HasPerpetualLicence(self) -> bool:
        for ls in self.m_LicenceSeats:
            if ls.IsPerpetualLicence:
                return True
        return False

    @property
    def LicenceSeats(self) -> List[LicenceSeatStructure]:
        return self.m_LicenceSeats

    @property
    def TotalSeats(self) -> int:
        seats = 0
        for ls in self.m_LicenceSeats:
            seats = seats + ls.Seats
        return seats

    def Sort(self) -> None:
        self.m_LicenceSeats.sort(reverse=True, key=LicenceSeatStructure)


def LicenceSeatStructureComparer(x: LicenceSeatStructure) -> int:
    """
    Function to sort Licences.
    We will sort by perpetual licences, then number of seats highest to lowest...
    """
    if x.IsPerpetualLicence:
        return sys.maxsize
    return x.Seats
