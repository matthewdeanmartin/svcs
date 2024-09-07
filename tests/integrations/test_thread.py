# SPDX-FileCopyrightText: 2023 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT
import pytest
import svcs

from src.svcs.thread import dependency_injection
from tests.helpers import CloseMe
from tests.ifaces import Service


def test_basic():
    close_me = CloseMe()

    def closer():
        close_me.close()

    registry = svcs.Registry()
    registry.register_value(CloseMe, close_me, on_registry_close=closer)
    registry.register_factory(Service, Service)
    registry.register_value(int, 1)
    @dependency_injection(registry)
    def task():
        service = svcs.thread.svcs_from().get(Service)
        assert isinstance(service, Service)
        assert svcs.thread.get(int) == 1

    task()
    assert close_me.is_closed


@pytest.mark.asyncio
async def test_async():
    close_me = CloseMe()

    async def closer():
        await close_me.aclose()

    registry = svcs.Registry()
    registry.register_value(CloseMe, close_me, on_registry_close=closer)
    registry.register_factory(Service, Service)
    registry.register_value(int, 1)
    @dependency_injection(registry)
    async def task():
        print("Task is running")

        service = await svcs.thread.svcs_from().aget(Service)
        assert service
        value = await svcs.thread.aget(int)
        assert  value == 1
        print("Task is done")

    await task()
    assert close_me.is_aclosed

