
# coding: utf-8

import io
import os
import warnings
import _compression
import zstandard
from threading import RLock


_MODE_CLOSED   = 0
_MODE_READ     = 1
# Value 2 no longer used
_MODE_WRITE = 3

__ALL__ = ['ZstdFile']

class ZstdFile(_compression.BaseStream):
    def __init__(self, filename, mode="r", buffering=None, level=9):
        self._lock = RLock()
        self._fp = None
        self._closefp = False
        self._mode = _MODE_CLOSED
        self._compressor = None
        self._eof = False
        self._size = -1

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
            self._cctx = zstandard.ZstdCompressor(level=level)
        elif mode in ("x", "xb"):
            mode = "xb"
            mode_code = _MODE_WRITE
            self._cctx = zstandard.ZstdCompressor(level=level)
        elif mode in ("a", "ab"):
            mode = "ab"
            mode_code = _MODE_WRITE
            self._cctx = zstandard.ZstdCompressor(level=level)
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
            self._dctx = zstandard.ZstdDecompressor()
            self._reader = None
            self._read_pos = 0
            # raw = ZstdDecompressReader(
            #     self._fp
            # )
            # self._buffer = io.BufferedReader(raw)
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
                    if self._reader:
                        self._reader.__exit__(None, None, None)
                    # self._buffer.close()
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
                    self._compressor = None
                    self._reader = None
                    self._dctx = None

    
    def create_reader(self):
        """
        """
        if not self._reader:
            _read = self._fp.read
            def read_fp(size=-1):
                print('reader size', size)
                return _read(size)
            if self._fp.read != read_fp:
                self._fp.read = read_fp
            self._reader = self._dctx.stream_reader(self._fp)
            self._reader.__enter__()

    def read(self, size):
        with self._lock:
            if size < 0:
                return self.readall()
            if not size or self._eof:
                return None
            self.create_reader()
            data = self._reader.read(size)
            if not data:
                self._eof = True
                self._size = self._read_pos
                return None
            self._read_pos += len(data)
            return data

    def readall(self):
        with self._lock:
            if self._eof:
                return None
            data = b""
            res = self.read(io.DEFAULT_BUFFER_SIZE)
            while res:
                data += res
                res = self.read(io.DEFAULT_BUFFER_SIZE)
            return data

    def readinto(self, b):
        """Read bytes into b.
        Returns the number of bytes read (0 for EOF).
        """
        with self._lock:
            with memoryview(b) as view, view.cast("B") as byte_view:
                data = self.read(len(byte_view))
                byte_view[:len(data)] = data
            return len(data)

    def readline(self, size=-1):
        """
        Read a line of uncompressed bytes from the file.
        The terminating newline (if present) is retained. If size is
        non-negative, no more than size bytes will be read (in which
        case the line may be incomplete). Returns b'' if already at EOF.
        """
        with self._lock:
            if not isinstance(size, int):
                if not hasattr(size, "__index__"):
                    raise TypeError("Integer argument expected")
            size = size.__index__()
            offet = 1
            char = self.read(1)
            if not char:
                return char
            data = b""
            while char and char != b"\n":
                offet += 1
                char = self.read(1)
                data += char
                if offet == size:
                    break
            return data

    def readlines(self, size=-1):
        """
        Read a list of lines of uncompressed bytes from the file.
        size can be specified to control the number of lines read: no
        further lines will be read once the total size of the lines read
        so far equals or exceeds size.
        """
        with self._lock:
            if not isinstance(size, int):
                if not hasattr(size, "__index__"):
                    raise TypeError("Integer argument expected")
                size = size.__index__()
            data = []
            index = 1
            line = self.readline()
            while line:
                index += 1
                line = self.readline()
                data.append(line)
                if index == size:
                    break
            return data

    def write(self, data):
        """
        Write a byte string to the file.
        Returns the number of uncompressed bytes written, which is
        always len(data). Note that due to buffering, the file on disk
        may not reflect the data written until close() is called.
        """
        if not self._compressor:
            self._compressor = self._cctx.write_to(self._fp)
            self._compressor.__enter__()
        self._compressor.write(data)
        self._pos += len(data)
        return len(data)

    def writelines(self, seq):
        """
        Write a sequence of byte strings to the file.
        Returns the number of uncompressed bytes written.
        seq can be any iterable yielding byte strings.
        Line separators are not added between the written byte strings.
        """
        return _compression.BaseStream.writelines(self, seq)

    def _rewind(self):
        self._fp.seek(0)
        self._eof = False
        self._read_pos = 0
        if self._reader:
            self._reader.__exit__(None, None, None)
            # self._stream_reader.close()
            self._reader = None

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
        print('---seek----', offset)
        if whence == io.SEEK_SET:
            pass
        elif whence == io.SEEK_CUR:
            offset = self._read_pos + offset
        elif whence == io.SEEK_END:
            if self._size < 0:
                while self.read(io.DEFAULT_BUFFER_SIZE):
                    pass
            offset = self._size + offset
        else:
            raise ValueError("Invalid value for whence: {}".format(whence))
        if offset < self._read_pos:
            self._rewind()
        else:
            offset -= self._read_pos
        while offset > 0:
            data = self.read(min(io.DEFAULT_BUFFER_SIZE, offset))
            if not data:
                break
            offset -= len(data)
        return self._read_pos

    def tell(self):
        """
        Return the current file position.
        """

        with self._lock:
            self._check_not_closed()
            if self._mode == _MODE_READ:
                return self._read_pos
            return self._pos
