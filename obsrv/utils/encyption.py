from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class EncryptionUtil:
    def __init__(self, encryption_key):
        self.algorithm = AES
        self.key = encryption_key.encode("utf-8")
        self.mode = AES.MODE_ECB
        self.block_size = AES.block_size

    def encrypt(self, value: str):
        cipher = self.algorithm.new(self.key, self.mode)
        padded_value = pad(value.encode("utf-8"), self.block_size)
        return b64encode(cipher.encrypt(padded_value)).decode("utf-8")

    def decrypt(self, value: str) -> str:
        cipher = self.algorithm.new(self.key, self.mode)
        decrypted_value64 = b64decode(value)
        decrypted_byte_value = unpad(cipher.decrypt(decrypted_value64), self.block_size)
        return decrypted_byte_value.decode("utf-8")
