import unittest
from obsrv.utils import EncryptionUtil


class TestEncryptionUtil(unittest.TestCase):
    def setUp(self):
        self.encryption_key = "5Gw743MySPvkcobvtVQoFJ0tUqAZ8TUw"
        self.encryption_util = EncryptionUtil(self.encryption_key)

    def test_encrypt(self):
        plaintext = "Hello, World!"
        encrypted_text = self.encryption_util.encrypt(plaintext)
        self.assertEqual(encrypted_text, "tz3mCbuoi8dfMSuIPngERg==")
        self.assertNotEqual(plaintext, encrypted_text)

    def test_decrypt(self):
        plaintext = "Hello, World!"
        encrypted_text = self.encryption_util.encrypt(plaintext)
        decrypted_text = self.encryption_util.decrypt(encrypted_text)
        self.assertEqual(plaintext, decrypted_text)

    def test_decrypt_wrong_key(self):
        plaintext = "Hello, World!"
        encrypted_text = self.encryption_util.encrypt(plaintext)
        wrong_key_encryption_util = EncryptionUtil("ozfS4yogdS8opAsIO7bhPc5jkwoJ8wUy")
        with self.assertRaises(Exception):
            wrong_key_encryption_util.decrypt(encrypted_text)
