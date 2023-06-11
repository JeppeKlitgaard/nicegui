import os
from pathlib import Path
from typing import Awaitable, Callable, Union

import magic
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import globals
from .native import Native
from .storage import Storage


class App(FastAPI):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.native = Native()
        self.storage = Storage()

    def on_connect(self, handler: Union[Callable, Awaitable]) -> None:
        """Called every time a new client connects to NiceGUI.

        The callback has an optional parameter of `nicegui.Client`.
        """
        globals.connect_handlers.append(handler)

    def on_disconnect(self, handler: Union[Callable, Awaitable]) -> None:
        """Called every time a new client disconnects from NiceGUI.

        The callback has an optional parameter of `nicegui.Client`.
        """
        globals.disconnect_handlers.append(handler)

    def on_startup(self, handler: Union[Callable, Awaitable]) -> None:
        """Called when NiceGUI is started or restarted.

        Needs to be called before `ui.run()`.
        """
        if globals.state == globals.State.STARTED:
            raise RuntimeError('Unable to register another startup handler. NiceGUI has already been started.')
        globals.startup_handlers.append(handler)

    def on_shutdown(self, handler: Union[Callable, Awaitable]) -> None:
        """Called when NiceGUI is shut down or restarted.

        When NiceGUI is shut down or restarted, all tasks still in execution will be automatically canceled.
        """
        globals.shutdown_handlers.append(handler)

    def on_exception(self, handler: Callable) -> None:
        """Called when an exception occurs.

        The callback has an optional parameter of `Exception`.
        """
        globals.exception_handlers.append(handler)

    def shutdown(self) -> None:
        """Shut down NiceGUI.

        This will programmatically stop the server.
        Only possible when auto-reload is disabled.
        """
        if globals.reload:
            raise Exception('calling shutdown() is not supported when auto-reload is enabled')
        globals.server.should_exit = True

    def add_static_files(self, url_path: str, local_directory: str) -> None:
        """Add static files.

        `add_static_files()` makes a local directory available at the specified endpoint, e.g. `'/static'`.
        This is useful for providing local data like images to the frontend.
        Otherwise the browser would not be able to access the files.
        Do only put non-security-critical files in there, as they are accessible to everyone.

        :param url_path: string that starts with a slash "/" and identifies the path at which the files should be served
        :param local_directory: local folder with files to serve as static content
        """
        if url_path == '/':
            raise ValueError('''Path cannot be "/", because it would hide NiceGUI's internal "/_nicegui" route.''')
        globals.app.mount(url_path, StaticFiles(directory=local_directory))

    def add_media_files(self, url_path: str, local_directory: str) -> None:
        """Add media files.

        `add_media_files()` allows a local files to be streamed from a specified endpoint, e.g. `'/media'`.
        """
        @self.get(f'{url_path}/' + '{filename}')
        async def read_item(request: Request, filename: str):
            video_path = Path(local_directory) / filename
            if not video_path.is_file():
                return {"detail": "Not Found"}, 404
            file_size = video_path.stat().st_size
            start, end = 0, file_size - 1
            range_header = request.headers.get('Range', None)
            if range_header:
                byte1, byte2 = range_header.split('=')[1].split('-')
                start = int(byte1)
                if byte2:
                    end = int(byte2)
            content_length = (end - start) + 1

            def content_reader(file, start, end, chunk_size=8192):
                with open(file, 'rb') as data:
                    data.seek(start)
                    remaining_bytes = end - start + 1
                    while remaining_bytes > 0:
                        chunk = data.read(min(chunk_size, remaining_bytes))
                        if not chunk:
                            break
                        yield chunk
                        remaining_bytes -= len(chunk)

            headers = {
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Content-Length': str(content_length),
                'Accept-Ranges': 'bytes',
            }

            return StreamingResponse(
                content_reader(video_path, start, end),
                media_type=magic.from_file(str(video_path), mime=True),
                headers=headers,
                status_code=206,
            )

    def remove_route(self, path: str) -> None:
        """Remove routes with the given path."""
        self.routes[:] = [r for r in self.routes if getattr(r, 'path', None) != path]
