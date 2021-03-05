import os
from xml.etree import ElementTree
from PyNLS.LicenceCore.clsRSA import RSAVerify


def test_positive_verify():
    public_key_file = open(os.path.join(os.getcwd(), 'public_key.pem'))
    public_key = public_key_file.read()
    licence_folder = os.path.join(os.getcwd(), 'Licences')
    licence_files = [file for file in os.listdir(licence_folder) if (os.path.isfile(os.path.join(licence_folder, file)) and (file.endswith('.nls1')))]
    for licence_file in licence_files:
        licence_content = ElementTree.parse(os.path.join(os.getcwd(), 'Licences', licence_file)).getroot()
        encoded_signature = licence_content.find('Code').text
        valid_licence = RSAVerify().Verify(data=licence_content, signature=encoded_signature, publicKey=public_key)
        assert valid_licence, "Test licence did not correctly validate"
    public_key_file.close()


def test_negative_verify():
    public_key_file = open(os.path.join(os.getcwd(), 'public_key.pem'))
    public_key = public_key_file.read()
    licence_folder = os.path.join(os.getcwd(), 'Licences')
    licence_files = [file for file in os.listdir(licence_folder) if (os.path.isfile(os.path.join(licence_folder, file)) and (file.endswith('.nls1')))]
    for licence_file in licence_files:
        licence_content = ElementTree.parse(os.path.join(os.getcwd(), 'Licences', licence_file)).getroot()
        licence_content.find('NumberOfSeats').text = '9876543210'
        encoded_signature = licence_content.find('Code').text
        valid_licence = RSAVerify().Verify(data=licence_content, signature=encoded_signature, publicKey=public_key)
        assert not valid_licence, "Test licence incorrectly validated"
    public_key_file.close()