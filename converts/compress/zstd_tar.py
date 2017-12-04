
# coding: utf-8

import tarfile
from .zstd_utils import ZstdFile

__ALL__ = ['ZstdTar']

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
