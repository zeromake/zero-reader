import hashlib
from crypt import crypt as _crypt
import random

__all__ = [
    "crypt",
    "sha256_crypt",
    "sha512_crypt",
    "md5_crypt"
]

HASH_METHOD = {
    "1": hashlib.md5,
    "5": hashlib.sha256,
    "6": hashlib.sha512
}
rng = random.SystemRandom()

join_byte_elems = b''.join
HASH64_CHARS = [raw.encode() for raw in "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"]


def _encode_bytes_little(next_value, chunks, tail):
    """
    helper used by encode_bytes() to handle little-endian encoding
    """
    idx = 0
    while idx < chunks:
        v1 = next_value()
        v2 = next_value()
        v3 = next_value()
        yield v1 & 0x3f
        yield ((v2 & 0x0f)<<2)|(v1>>6)
        yield ((v3 & 0x03)<<4)|(v2>>4)
        yield v3>>2
        idx += 1
    if tail:
        v1 = next_value()
        if tail == 1:
            yield v1 & 0x3f
            yield v1>>6
        else:
            assert tail == 2
            v2 = next_value()
            yield v1 & 0x3f
            yield ((v2 & 0x0f)<<2)|(v1>>6)
            yield v2>>4

def encode_bytes(source):
    """
    encode bytes to base64 string.
    :arg source: byte string to encode.
    :returns: byte string containing encoded data.
    """
    chunks, tail = divmod(len(source), 3)
    next_value = iter(source).__next__
    gen = _encode_bytes_little(next_value, chunks, tail)
    data = []
    for index in gen:
        obj = HASH64_CHARS[index]
        data.append(obj)
    out = join_byte_elems(data)
    return out


def get_hash(salt):
    """
    获取hash算法
    """
    if isinstance(salt, str) and len(salt) > 1 and salt[0] == "$" and salt[1] in HASH_METHOD:
        return HASH_METHOD[salt[1]]

def crypt(word, salt):
    """
    代理原生crypt
    """
    hash_method = get_hash(salt)
    if hash_method is None:
        hash_str = _crypt(word, salt)
        hash_str = hash_str[hash_str.rindex("$")+1:]
    else:
        hash_obj = hash_method()
        hash_obj.update((salt + word + salt).encode())
        hash_str = encode_bytes(hash_obj.digest()).decode()
    if salt[-1] == "$":
        return salt + hash_str
    return "%s$%s" % (salt, hash_str)

class AbcCrypt:
    """
    Crypt抽象类
    """
    default_salt_size = 16
    hash_method = None
    @classmethod
    def _generate_salt(cls):
        """
        生成salt
        """
        count = cls.default_salt_size
        charset = HASH64_CHARS
        letters = len(charset)
        def helper():
            """
            生成器
            """
            value = rng.randrange(0, letters**count)
            i = 0
            while i < count:
                yield charset[value % letters]
                value //= letters
                i += 1
        return join_byte_elems(helper()).decode()

    @classmethod
    def hash(cls, word):
        """
        生成带盐hash
        """
        salt = "$%s$%s" % (cls.hash_method, cls._generate_salt())
        return crypt(word, salt)

    @classmethod
    def verify(cls, word, hash_string):
        """
        校验
        """
        salt = hash_string[:hash_string.rindex("$")]
        return hash_string == crypt(word, salt)
class sha256_crypt(AbcCrypt):
    """
    sha256
    """
    hash_method = "5"

class sha512_crypt(AbcCrypt):
    """
    sha512
    """
    hash_method = "6"

class md5_crypt(AbcCrypt):
    """
    md5
    """
    hash_method = "1"
