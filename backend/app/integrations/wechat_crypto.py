import base64
import hashlib
import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class WeChatCryptoError(ValueError):
    pass


class WeChatCrypto:
    def __init__(self, token: str, encoding_aes_key: str, receive_id: str) -> None:
        if not token:
            raise WeChatCryptoError("WECHAT_TOKEN is missing.")
        if not encoding_aes_key:
            raise WeChatCryptoError("WECHAT_AES_KEY is missing.")
        if len(encoding_aes_key) != 43:
            raise WeChatCryptoError("WECHAT_AES_KEY must be 43 characters.")

        self.token = token
        self.receive_id = receive_id
        self.aes_key = base64.b64decode(encoding_aes_key + "=")
        if len(self.aes_key) != 32:
            raise WeChatCryptoError("Invalid WECHAT_AES_KEY.")

    def verify_url(
        self,
        msg_signature: str,
        timestamp: str,
        nonce: str,
        echo_str: str,
    ) -> str:
        self._verify_signature(msg_signature, timestamp, nonce, echo_str)
        message, receive_id = self._decrypt(echo_str)
        self._verify_receive_id(receive_id)
        return message

    def _verify_signature(
        self,
        msg_signature: str,
        timestamp: str,
        nonce: str,
        encrypted: str,
    ) -> None:
        raw = "".join(sorted([self.token, timestamp, nonce, encrypted]))
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
        if digest != msg_signature:
            raise WeChatCryptoError("Invalid msg_signature.")

    def _decrypt(self, encrypted: str) -> tuple[str, str]:
        cipher_text = base64.b64decode(encrypted)
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_key[:16]))
        decryptor = cipher.decryptor()
        padded = decryptor.update(cipher_text) + decryptor.finalize()
        plain = self._pkcs7_unpad(padded)

        if len(plain) < 20:
            raise WeChatCryptoError("Invalid decrypted payload.")

        message_length = struct.unpack("!I", plain[16:20])[0]
        message_start = 20
        message_end = message_start + message_length
        message = plain[message_start:message_end].decode("utf-8")
        receive_id = plain[message_end:].decode("utf-8")
        return message, receive_id

    def _pkcs7_unpad(self, data: bytes) -> bytes:
        if not data:
            raise WeChatCryptoError("Empty decrypted payload.")
        pad = data[-1]
        if pad < 1 or pad > 32:
            raise WeChatCryptoError("Invalid padding.")
        if data[-pad:] != bytes([pad]) * pad:
            raise WeChatCryptoError("Invalid padding bytes.")
        return data[:-pad]

    def _verify_receive_id(self, receive_id: str) -> None:
        if self.receive_id and receive_id and receive_id != self.receive_id:
            raise WeChatCryptoError("Invalid receive id.")
