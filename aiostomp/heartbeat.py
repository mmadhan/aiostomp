import asyncio
from typing import Optional

from contextlib import suppress
from datetime import datetime


class StompHeartbeater:

    HEART_BEAT = b"\n"
    MAX_MISS_DELTA = 1_000  # ms

    def __init__(
        self,
        transport: asyncio.Transport,
        interval: int = 1000,
    ):
        self._transport = transport
        self.interval = interval / 1000.0
        self.task: Optional[asyncio.Future[None]] = None
        self.is_started = False

        self.received_heartbeat = None
        self.last_time_stamp = None

    async def start(self) -> None:
        if self.is_started:
            await self.stop()

        self.is_started = True
        self.task = asyncio.ensure_future(self.run())

    async def stop(self) -> None:
        if self.is_started and self.task:
            self.is_started = False
            # Stop task and await it stopped:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task

    def shutdown(self) -> None:
        if self.task:
            self.task.cancel()
            self.task = None

    async def run(self) -> None:
        while True:
            await self.send()
            await asyncio.sleep(self.interval)

    async def send(self) -> None:
        self._transport.write(self.HEART_BEAT)

    def beat(self):
        self.last_time_stamp = datetime.now().timestamp()
        print(
            self.last_time_stamp,
            (datetime.now().timestamp() - self.last_time_stamp),
            (datetime.now().timestamp() - self.last_time_stamp) <= self.MAX_MISS_DELTA,
        )

    @property
    def is_healthy(self):
        return (
            self.last_time_stamp
            and (datetime.now().timestamp() - self.last_time_stamp)
            <= self.MAX_MISS_DELTA
        )

    def reset_time_stamp(self):
        self.last_time_stamp = None
