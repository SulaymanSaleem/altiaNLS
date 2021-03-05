from xml.etree import ElementTree
from .clsRSA import RSAVerify
import os


class LicenceReader:
    BaseExtension = ".nls"
    m_Licence1: ElementTree.Element

    @property
    def Licence1(self) -> ElementTree.Element:
        """
        Gets the associated Licence.

        :returns: The associated Licence.
        """
        return self.m_Licence1

    def Read(self, fileName: str) -> None:
        """
        Reads the licence from the specified fileName.

        :param fileName: The name of file containing the licence to read.
        """
        try:
            if os.path.isfile(os.path.join(os.getcwd(), 'Licences', fileName)) and (fileName.endswith('.nls1')):
                self.m_Licence1 = ElementTree.parse(os.path.join(os.getcwd(), 'Licences', fileName)).getroot()
        except FileNotFoundError:
            raise FileNotFoundError("Licence file: " + fileName + " not found.")

    # This function is used only when generating licences and thus is not implemented here.
    def SetLicence(self, o) -> None:
        pass

    def Verify(self, publicKey: str) -> bool:
        """
        Verifies the licence by comparing it to the signature computed
        for the licence using the specified public key.

        :param publicKey: The public key used to verify.
        :returns: Whether the licence verifies successfully.
        """
        if not publicKey:
            raise ValueError(str(publicKey))
        isValid = False
        if self.m_Licence1:
            signature = self.m_Licence1.find('Code').text
            self.m_Licence1.find('Code').text = ''
            try:
                isValid = RSAVerify().Verify(self.m_Licence1, signature, publicKey)
                self.m_Licence1.find('Code').text = signature
            except Exception as ex:
                print("Exception 22")
                print(ex)
                isValid = False
        return isValid

    # This function is used only when generating licences and thus is not implemented here.
    def Write(self, fileName: str, publicKey: str) -> None:
        pass

    @staticmethod
    def VerifyWithFile(publicKey: str, value: ElementTree.Element) -> bool:
        """
        Verifies the specified licence by comparing it to the signature
        computed for the licence using the specified public key.

        :param publicKey: The public key used to verify.
        :param value: The licence to verify.
        :returns: Whether the licence verifies successfully.
        """
        lr = LicenceReader()
        lr.m_Licence1 = value
        return lr.Verify(publicKey)
