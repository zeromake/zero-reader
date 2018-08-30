import os
from sanic.response import StreamingHTTPResponse, STATUS_CODES, file_stream
from mimetypes import guess_type


class ZeroCopyStreamingHTTPResponse(StreamingHTTPResponse):
    __slots__ = (
        'transport',
        'file_path',
        'file_name',
        'status',
        'content_type',
        'headers',
        '_cookies',
        '_chunked',
        '_file_path',
        '_file_name',
        '_chunk_size',
    )

    def __init__(
        self,
        file_path: str,
        file_name: str = None,
        chunked: bool = True,
        chunk_size: int = 4096,
        status: int = 200,
        headers: dict = None,
        content_type: str = None,
    ):
        self.content_type = content_type
        self.status = status
        self.headers = headers or {}
        self.transport = None
        self._cookies = None
        self._chunked = chunked
        self._file_name = file_name
        self._file_path = file_path
        self._chunk_size = chunk_size
    
    def sync_write(self, out_fd: int, data: bytes):
        """
        同步写入
        """
        os.write(out_fd, data)
    
    async def stream(
            self,
            version="1.1",
            keep_alive=False,
            keep_alive_timeout=None
        ):
        """
        Streams headers, runs the `streaming_fn` callback that writes
        content to the response body, then finalizes the response body.
        """
        if self._file_name:
            self.headers["Content-Disposition"] = "attachment; filename=\"%s\"" % self._file_name
        file_size = os.path.getsize(self._file_path)
        if self.content_type is None:
            self.content_type = guess_type(self._file_path)[0] or 'application/octet-stream'
        with open(self._file_path, 'rb') as input_file:
            input_fd = input_file.fileno()
            output_fd = self.transport.get_extra_info('socket').fileno()
            if self._chunked:
                headers = self.get_headers(
                    version,
                    keep_alive=keep_alive,
                    keep_alive_timeout=keep_alive_timeout
                )
                self.sync_write(output_fd, headers)
                send_size = min(file_size, self._chunk_size)
                lave_size = file_size
                offset_no = 0
                while lave_size > 0:
                    self.sync_write(
                        output_fd,
                        b"%x\r\n" % send_size
                    )
                    os.sendfile(output_fd, input_fd, offset_no, send_size)
                    self.sync_write(
                        output_fd,
                        b"\r\n"
                    )
                    offset_no += send_size
                    lave_size -= send_size
                    send_size = min(lave_size, self._chunk_size)
                self.transport.write(b'0\r\n\r\n')
            else:
                send_size = file_size
                offset_no = 0
                self.headers["Content-Length"] = str(send_size)
                headers = self.get_headers(
                    version,
                    keep_alive=keep_alive,
                    keep_alive_timeout=keep_alive_timeout
                )
                self.sync_write(output_fd, headers)
                os.sendfile(output_fd, input_fd, offset_no, send_size)

    def get_headers(
            self,
            version: str = "1.1",
            keep_alive: str = False,
            keep_alive_timeout = None,
        ):
        # This is all returned in a kind-of funky way
        # We tried to make this as fast as possible in pure python
        timeout_header = b''
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b'Keep-Alive: %d\r\n' % keep_alive_timeout
        if self._chunked:
            self.headers['Transfer-Encoding'] = 'chunked'
            self.headers.pop('Content-Length', None)
        self.headers['Accept-Ranges'] = "bytes"
        content_type = self.headers.get(
            'Content-Type',
            self.content_type
        )
        if content_type.startswith("text") or content_type.endswith("json"):
            content_type += "; charset=utf-8"
        self.headers['Content-Type'] = content_type
        headers = self._parse_headers()
        if self.status is 200:
            status = b'OK'
        else:
            status = STATUS_CODES.get(self.status)
        return (b'HTTP/%b %d %b\r\n%b%b\r\n') % (
            version.encode(),
            self.status,
            status,
            timeout_header,
            headers
        )

async def zero_copy_stream(
        file_path: str,
        file_name: str = None,
        chunked: bool = True,
        chunk_size: int = 4096,
        status=200,
        headers=None,
        mime_type=None,
    ):
    """
    Accepts an coroutine `streaming_fn`
    """
    if hasattr(os, "sendfile"):
        return ZeroCopyStreamingHTTPResponse(
            file_path,
            file_name=file_name,
            chunked=chunked,
            chunk_size=chunk_size,
            headers=headers,
            content_type=mime_type,
            status=status
        )
    return await file_stream(
        file_path,
        chunk_size=chunk_size,
        mime_type=mime_type,
        headers=headers,
        filename=file_name,
    )
