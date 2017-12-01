import zstandard as zstd
import _compression
from threading import RLock
import os
import io
import warnings
import tarfile

class ZstdTar(tarfile.TarFile):
    """
    Zstd的tar支持
    """
    @classmethod
    def zstdopen(cls, name, mode="r", fileobj=None, level=9, **kwargs):
        """
        Open zstd compressed tar archive name for reading or writing.
           Appending is not allowed.
        """
        if mode not in ("r", "w", "x"):
            raise ValueError("mode must be 'r', 'w' or 'x'")

        # try:
        #     import zstd
        # except ImportError:
        #     raise CompressionError("zstd module is not available")

        fileobj = ZstdFile(
            fileobj or name,
            mode,
            level=level
        )

        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (OSError, EOFError):
            fileobj.close()
            if mode == 'r':
                raise tarfile.ReadError("not a zstd file")
            raise
        except:
            fileobj.close()
            raise
        t._extfileobj = False
        return t
    tarfile.TarFile.OPEN_METH.update({'zstd': 'zstdopen'})
    tarfile.TarFile.zstdopen = zstdopen

_MODE_CLOSED   = 0
_MODE_READ     = 1
# Value 2 no longer used
_MODE_WRITE = 3

class ZstdDecompressReader(io.RawIOBase):
    """
    Zstd
    """
    def readable(self):
        return True

    def __init__(self, fp, **decomp_args):
        self._fp = fp
        self._eof = False
        self._pos = 0
        self._size = -1
        self._decomp_args = decomp_args
        self._decompressor = zstd.ZstdDecompressor(**self._decomp_args)
        print(dir(self._decompressor))
        self._stream_reader = None

    def close(self):
        self._decompressor = None
        if self._stream_reader:
            self._stream_reader.__exit__(None, None, None)
            # self._stream_reader.close()
            self._stream_reader = None
        return super().close()

    def seekable(self):
        return self._fp.seekable()

    def readinto(self, b):
        with memoryview(b) as view, view.cast("B") as byte_view:
            data = self.read(len(byte_view))
            byte_view[:len(data)] = data
        return len(data)

    def read(self, size=-1):
        print('----read-----size:', size)
        if size < 0:
            return self.readall()
        if not size or self._eof:
            return b""
        if not self._stream_reader:
            self._stream_reader = self._decompressor.stream_reader(self._fp)
            self._stream_reader.__enter__()
        data = self._stream_reader.read(size)
        if not data:
            self._eof = True
            self._size = self._pos
            return b""
        self._pos += len(data)
        return data

    # Rewind the file to the beginning of the data stream.
    def _rewind(self):
        self._fp.seek(0)
        self._eof = False
        self._pos = 0
        if self._stream_reader:
            self._stream_reader.__exit__(None, None, None)
            # self._stream_reader.close()
            self._stream_reader = None
        self._decompressor = zstd.ZstdDecompressor(**self._decomp_args)

    def seek(self, offset, whence=io.SEEK_SET):
        # Recalculate offset as an absolute file position.
        if whence == io.SEEK_SET:
            pass
        elif whence == io.SEEK_CUR:
            offset = self._pos + offset
        elif whence == io.SEEK_END:
            if self._size < 0:
                while self.read(io.DEFAULT_BUFFER_SIZE):
                    pass
            offset = self._size + offset
        else:
            raise ValueError("Invalid value for whence: {}".format(whence))
        if offset < self._pos:
            self._rewind()
        else:
            offset -= self._pos
        while offset > 0:
            data = self.read(min(io.DEFAULT_BUFFER_SIZE, offset))
            if not data:
                break
            offset -= len(data)

        return self._pos

    def tell(self):
        """
        Return the current file position.
        """
        return self._pos


class ZstdFile(_compression.BaseStream):
    def __init__(self, filename, mode="r", buffering=None, level=9):
        self._lock = RLock()
        self._fp = None
        self._closefp = False
        self._mode = _MODE_CLOSED
        self._compressor = None

        if buffering is not None:
            warnings.warn(
                "Use of 'buffering' argument is deprecated",
                DeprecationWarning
            )

        if level < 1 or level > 22:
            raise ValueError("level must be between 1 and22")

        if mode in ("", "r", "rb"):
            mode = "rb"
            mode_code = _MODE_READ
        elif mode in ("w", "wb"):
            mode = "wb"
            mode_code = _MODE_WRITE
            self._cctx = zstd.ZstdCompressor(level=level)
        elif mode in ("x", "xb"):
            mode = "xb"
            mode_code = _MODE_WRITE
            self._cctx = zstd.ZstdCompressor(level=level)
        elif mode in ("a", "ab"):
            mode = "ab"
            mode_code = _MODE_WRITE
            self._cctx = zstd.ZstdCompressor(level=level)
        else:
            raise ValueError("Invalid mode: %r" % (mode,))

        if isinstance(filename, (str, bytes, os.PathLike)):
            self._fp = open(filename, mode)
            self._closefp = True
            self._mode = mode_code
        elif hasattr(filename, "read") or hasattr(filename, "write"):
            self._fp = filename
            self._mode = mode_code
        else:
            raise TypeError("filename must be a str, bytes, file or PathLike object")

        if self._mode == _MODE_READ:
            raw = ZstdDecompressReader(
                self._fp
            )
            self._buffer = io.BufferedReader(raw)
        else:
            self._pos = 0

    def close(self):
        """
        Flush and close the file.
        May be called more than once without error. Once the file is
        closed, any other operation on it will raise a ValueError.
        """
        with self._lock:
            if self._mode == _MODE_CLOSED:
                return
            try:
                if self._mode == _MODE_READ:
                    self._buffer.close()
                elif self._mode == _MODE_WRITE:
                    if self._compressor:
                        self._compressor.flush()
            finally:
                try:
                    if self._closefp:
                        if self._compressor:
                            self._compressor.__exit__(None, None, None)
                            # self._compressor.close()
                        self._fp.close()
                finally:
                    self._fp = None
                    self._closefp = False
                    self._mode = _MODE_CLOSED
                    self._buffer = None
                    self._compressor = None
    
    def read(self, size):
        with self._lock:
            return self._buffer.read(size)

    def readinto(self, b):
        """Read bytes into b.
        Returns the number of bytes read (0 for EOF).
        """
        with self._lock:
            return self._buffer.readinto(b)

    def readline(self, size=-1):
        """
        Read a line of uncompressed bytes from the file.
        The terminating newline (if present) is retained. If size is
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' if already at EOF.
        """
        if not isinstance(size, int):
            if not hasattr(size, "__index__"):
                raise TypeError("Integer argument expected")
            size = size.__index__()
        with self._lock:
            return self._buffer.readline(size)

    def readlines(self, size=-1):
        """
        Read a list of lines of uncompressed bytes from the file.
        size can be specified to control the number of lines read: no
        further lines will be read once the total size of the lines read
        so far equals or exceeds size.
        """
        if not isinstance(size, int):
            if not hasattr(size, "__index__"):
                raise TypeError("Integer argument expected")
            size = size.__index__()
        with self._lock:
            return self._buffer.readlines(size)

    def write(self, data):
        """
        Write a byte string to the file.
        Returns the number of uncompressed bytes written, which is
        always len(data). Note that due to buffering, the file on disk
        may not reflect the data written until close() is called.
        """
        with self._lock:
            if not self._compressor:
                self._compressor = self._cctx.write_to(self._fp)
                self._compressor.__enter__()
            self._compressor.write(data)
            # compressed = self._compressor.compress(data)
            # self._fp.write(compressed)
            self._pos += len(data)
            return len(data)

    def writelines(self, seq):
        """
        Write a sequence of byte strings to the file.
        Returns the number of uncompressed bytes written.
        seq can be any iterable yielding byte strings.
        Line separators are not added between the written byte strings.
        """
        with self._lock:
            return _compression.BaseStream.writelines(self, seq)

    def seek(self, offset, whence=io.SEEK_SET):
        """
        Change the file position.
        The new position is specified by offset, relative to the
        position indicated by whence. Values for whence are:
            0: start of stream (default); offset must not be negative
            1: current stream position
            2: end of stream; offset must not be positive
        Returns the new file position.
        Note that seeking is emulated, so depending on the parameters,
        this operation may be extremely slow.
        """
        with self._lock:
            return self._buffer.seek(offset, whence)

    def tell(self):
        """
        Return the current file position.
        """
        with self._lock:
            self._check_not_closed()
            if self._mode == _MODE_READ:
                return self._buffer.tell()
            return self._pos


# zstd.ZstdCompressor 压缩
# zstd.ZstdDecompressor 解压
def compressor(input_path, output_path, mode="zstd"):
    """
    压缩文件
    """
    cctx = zstd.ZstdCompressor()
    with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
        cctx.copy_stream(input_file, output_file)

def decompressor(input_path, output_path, mode="zstd"):
    """
    解压文件
    """
    dctx = zstd.ZstdDecompressor()
    with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
        dctx.copy_stream(input_file, output_file)

if __name__ == '__main__':
    # with open("1.tar.zstd", 'rb') as fh:
    #     dctx = zstd.ZstdDecompressor()
    #     print(dir(dctx))
    zstd_file = tarfile.open("1.tar.zstd", "r:zstd")
    with zstd_file.extractfile('682209267f55b840d75a7fb74da74e93bfb0ac4e800f96ad88370d524f160105/zoom.json') as json_file:
        data = json_file.readline()
        # while data:
        print(data)
            # data = json_file.readline()
    # compressor('1.tar', '1.tar.zstd')
    # decompressor('1.tar.zstd', '2.tar')
