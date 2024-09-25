# SPDX-FileCopyrightText: 2023 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT
# pylint: disable=global-statement
from __future__ import annotations

import atexit
import contextvars
import inspect
from collections.abc import Callable, Generator
from contextlib import asynccontextmanager, contextmanager, suppress
from functools import wraps

from typing import Any, cast, overload

import svcs
from svcs._core import T1, T2, T3, T4, T5, T6, T7, T8, T9, T10

# Fancy globals
REGISTRY_VAR: contextvars.ContextVar[svcs.Registry | None] | None = None
CONTAINER_VAR: contextvars.ContextVar[svcs.Container | None] | None = None


def svcs_from() -> svcs.Container:
    """
    Get the current container from *thread*.
    """
    # With contextvar (works better with asyncio when using threads and a context manager (?))
    global CONTAINER_VAR
    if not CONTAINER_VAR:
        CONTAINER_VAR = contextvars.ContextVar("container")
    container = CONTAINER_VAR
    if not container.get(None):
        container.set(svcs.Container(get_registry()))
        container_value = container.get()
        if container_value:
            return container_value
    container_value = container.get()
    if container_value:
        return container_value
    raise RuntimeError("Container not initialized.")

    # naive implementation
    # if getattr(current_thread, "container", None) is None:
    #     container = svcs.Container(get_registry())
    #     cast(Any, current_thread()).container = container
    #     return container
    # return cast(svcs.Container, cast(Any, current_thread()).container)

    # Alternate implementation
    # import threading
    # if not threading.local.__dict__["container"]:
    #     container = svcs.Container(get_registry())
    #     threading.local.__dict__["container"] = container
    #     return container
    # return threading.local.__dict__["container"]


def get_registry() -> svcs.Registry:
    """
    Get the registry from *thread*.
    """
    global REGISTRY_VAR
    if not REGISTRY_VAR:
        REGISTRY_VAR = contextvars.ContextVar("registry")

    registry = REGISTRY_VAR
    return cast(svcs.Registry, registry.get(None))
    # return cast(svcs.Registry, cast(Any, current_threa.d()).registry)


def init_app(
    *,
    registry: svcs.Registry | None = None,
    prevent_double_init: bool = True,
) -> None:
    """
    Initialize the application.

    Args:
        registry: The registry to use. If None, a new one is created.
        prevent_double_init: If True, raise an error if the application is already initialized. This could happen in
        unit testing.
    """
    global REGISTRY_VAR
    if prevent_double_init and REGISTRY_VAR is not None:
        raise RuntimeError("Application already initialized.")
    # cast(Any, current_thread()).registry = registry or svcs.Registry()
    REGISTRY_VAR = contextvars.ContextVar("registry")
    REGISTRY_VAR.set(registry or svcs.Registry())

    # this doesn't tear down until root process is torn down.
    # Process/Thread pools will only get one teardown for everyone when process exits
    # better way: https://github.com/kuralabs/multiexit/tree/master
    atexit.register(close_registry)


async def ainit_app(
    *,
    registry: svcs.Registry | None = None,
    prevent_double_init: bool = True,
) -> None:
    """
    Initialize the application.

    Args:
        registry: The registry to use. If None, a new one is created.
        prevent_double_init: If True, raise an error if the application is already initialized. This could happen in
        unit testing.
    """
    global REGISTRY_VAR
    if prevent_double_init and REGISTRY_VAR is not None:
        raise RuntimeError("Application already initialized.")
    # cast(Any, current_thread()).registry = registry or svcs.Registry()
    # set via contextvars
    if not REGISTRY_VAR:
        REGISTRY_VAR = contextvars.ContextVar("registry")
    REGISTRY_VAR.set(registry or svcs.Registry())

    atexit.register(aclose_registry)


def register_value(
    svc_type: type,
    value: object,
    *,
    enter: bool = False,
    ping: Callable | None = None,  # type: ignore[type-arg]
    on_registry_close: Callable | None = None,  # type: ignore[type-arg]
) -> None:
    """
    Same as :meth:`svcs.Registry.register_value()`, but uses registry on
    *thread*.
    """
    get_registry().register_value(
        svc_type,
        value,
        enter=enter,
        ping=ping,
        on_registry_close=on_registry_close,
    )


def register_factory(
    svc_type: type,
    factory: Callable,  # type: ignore[type-arg]
    *,
    enter: bool = True,
    ping: Callable | None = None,  # type: ignore[type-arg]
    on_registry_close: Callable | None = None,  # type: ignore[type-arg]
) -> None:
    """
    Same as :meth:`svcs.Registry.register_factory()`, but uses registry on
    *thread*.
    """
    get_registry().register_factory(
        svc_type,
        factory,
        enter=enter,
        ping=ping,
        on_registry_close=on_registry_close,
    )


def close_registry() -> None:
    """
    Close the registry on *thread*, if present.

    You probably don't have to call this yourself, because it's registered for
    the application as an {attr}`atexit` callback.
    """
    with suppress(KeyError):
        registry = get_registry()
        if registry:
            registry.close()


async def aclose_registry() -> None:
    """
    Close the registry on *thread*, if present.

    You probably don't have to call this yourself, because it's registered for
    the application as an {attr}`atexit` callback.
    """
    with suppress(KeyError):
        await get_registry().aclose()


def get_pings() -> list[svcs.ServicePing]:
    """
    Same as :meth:`svcs.Container.get_pings`, but uses the container from
    *thread*.
    """
    return svcs_from().get_pings()


async def aget_abstract(*svc_types: type) -> Any:
    """
    Same as :meth:`svcs.Container.aget_abstract()`, but uses container from
    *request*.
    """
    return await svcs_from().aget_abstract(*svc_types)


@overload
async def aget(svc_type: type[T1], /) -> T1: ...


@overload
async def aget(svc_type1: type[T1], svc_type2: type[T2], /) -> tuple[T1, T2]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    /,
) -> tuple[T1, T2, T3]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    /,
) -> tuple[T1, T2, T3, T4]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    /,
) -> tuple[T1, T2, T3, T4, T5]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    svc_type9: type[T9],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...


@overload
async def aget(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    svc_type9: type[T9],
    svc_type10: type[T10],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...


async def aget(*svc_types: type) -> object:
    """
    Same as :meth:`svcs.Container.aget`, but uses the container from *request*.
    """
    return await svcs_from().aget(*svc_types)


@overload
def get(svc_type: type[T1], /) -> T1: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    /,
) -> tuple[T1, T2]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    /,
) -> tuple[T1, T2, T3]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    /,
) -> tuple[T1, T2, T3, T4]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    /,
) -> tuple[T1, T2, T3, T4, T5]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    svc_type9: type[T9],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...


@overload
def get(
    svc_type1: type[T1],
    svc_type2: type[T2],
    svc_type3: type[T3],
    svc_type4: type[T4],
    svc_type5: type[T5],
    svc_type6: type[T6],
    svc_type7: type[T7],
    svc_type8: type[T8],
    svc_type9: type[T9],
    svc_type10: type[T10],
    /,
) -> tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]: ...


def get(*svc_types: type) -> object:
    """
    Same as :meth:`svcs.Container.get()`, but uses thread locals to find the
    current request.
    """
    return svcs_from().get(*svc_types)


def dependency_injection(registry: svcs.Registry | None = None) -> Callable:  # type: ignore[type-arg]
    def decorator(func: Callable) -> Callable:  # type: ignore[type-arg]
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                await ainit_app(registry=registry)
                try:
                    result = await func(*args, **kwargs)
                finally:
                    await get_registry().aclose()
                return result

        else:

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                init_app(registry=registry)
                try:
                    result = func(*args, **kwargs)
                finally:
                    get_registry().close()
                return result

        return wrapper

    return decorator


def close_and_release_registry() -> None:
    get_registry().close()
    global REGISTRY_VAR
    if REGISTRY_VAR:
        REGISTRY_VAR.set(None)
    REGISTRY_VAR = None

    global CONTAINER_VAR
    if CONTAINER_VAR:
        CONTAINER_VAR.set(None)
    CONTAINER_VAR = None
    # cast(Any, current_thread()).registry = None


@contextmanager
def dependency_injection_context(registry: svcs.Registry | None = None) -> Generator[None]:
    init_app(registry=registry)
    try:
        yield
    finally:
        close_and_release_registry()


async def aclose_and_release_registry() -> None:
    await get_registry().aclose()
    global REGISTRY_VAR
    if REGISTRY_VAR:
        REGISTRY_VAR.set(None)
    REGISTRY_VAR = None
    # cast(Any, current_thread()).registry = None


@asynccontextmanager  # type: ignore
async def adependency_injection_context(  # type: ignore
    registry: svcs.Registry | None = None,
) -> Generator[None]:
    await ainit_app(registry=registry)
    try:
        yield
    finally:
        await aclose_and_release_registry()


if __name__ == "__main__":
    _ = get_registry()
    print(_)
