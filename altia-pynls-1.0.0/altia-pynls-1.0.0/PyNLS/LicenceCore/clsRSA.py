import base64
from xml.etree import ElementTree
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from .clsUtils import Utils


class RSAVerify:
    """
    Implements a class for RSA public key (Asymmetric) encryption and decryption, data signing and verifification.
    Asymmetric cryptography uses different but mathematically related keys for
    encryption and decryption. We generate a public key and a corresponding private key.
    The way the algorithms work is that the private key can only be used to decrypt information
    that has been encrypted using its matching public key. Conversely, the public key can
    verify information signed with the private key.
    """
    m_HashAlgorithm = SHA1

    def Verify(self, data: ElementTree.Element, signature: str, publicKey: str) -> bool:
        """
        Verifies the specified signature by comparing it to the signature computed for the specified data
        using the specified public key.

        :param data: The XML imported as an Element Tree Element
        :param signature: The base64-encoded string signature to verify
        :param publicKey: The public key for the asymmetric algorithm
        :returns: True if the signature is valid, otherwise false
        :raises ValueError: data is null
        """
        if not data:
            raise ValueError("data")
        public_key = RSA.import_key(publicKey)
        decoded_signature = base64.b64decode(signature)
        data.find('Code').text = ''
        Utils.enforce_licence_newline(data)
        hashed_content = self.m_HashAlgorithm.new(
            ElementTree.tostring(data, encoding='utf-8', method='xml', xml_declaration=False)
        )
        try:
            pkcs1_15.new(public_key).verify(hashed_content, decoded_signature)
            return True
        except (ValueError, TypeError):
            pass
        return False
