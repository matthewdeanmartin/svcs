# SPDX-FileCopyrightText: 2023 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import inspect


import atexit
from functools import wraps
from collections.abc import Callable
from contextlib import suppress, contextmanager, asynccontextmanager
from threading import current_thread
from typing import Any, cast, overload

import svcs

from svcs._core import (
    _KEY_CONTAINER,
    T1,
    T2,
    T3,
    T4,
    T5,
    T6,
    T7,
    T8,
    T9,
    T10,
)


def svcs_from() -> svcs.Container:
    """
    Get the current container from *thread*.
    """
    if getattr(current_thread, "container", None) is None:
        container = svcs.Container(get_registry())
        cast(Any, current_thread()).container = container
        return container
    return cast(svcs.Container, cast(Any, current_thread()).container)


def get_registry() -> svcs.Registry:
    """
    Get the registry from *thread*.
    """
    return cast(svcs.Registry, cast(Any, current_thread()).registry)



def init_app(
    *,
    registry: svcs.Registry | None = None,
) -> None:
    """
    Initialize the application.
    """
    cast(Any, current_thread()).registry = registry or svcs.Registry()
    atexit.register(close_registry)

async def ainit_app(
    *,
    registry: svcs.Registry | None = None,
) -> None:
    """
    Initialize the application.
    """
    cast(Any, current_thread()).registry = registry or svcs.Registry()
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
    ping: Callable | None = None, # type: ignore[type-arg]
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
        get_registry().close()


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
async def aget(
    svc_type1: type[T1], svc_type2: type[T2], /
) -> tuple[T1, T2]: ...


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





def dependency_injection(registry: svcs.Registry | None = None)->Callable: # type: ignore[type-arg]
    def decorator(func:Callable)->Callable: # type: ignore[type-arg]
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args:Any, **kwargs:Any)->Any:
                await ainit_app(registry=registry)
                try:
                    result = await func(*args, **kwargs)
                finally:
                    await get_registry().aclose()
                return result
        else:
            @wraps(func)
            def wrapper(*args:Any, **kwargs:Any)->Any:
                init_app(registry=registry)
                try:
                    result = func(*args, **kwargs)
                finally:
                    get_registry().close()
                return result

        return wrapper

    return decorator

@contextmanager
def dependency_injection_context(registry: svcs.Registry | None = None):
    init_app(registry=registry)
    try:
        yield
    finally:
        get_registry().close()

@asynccontextmanager
async def adependency_injection_context(registry: svcs.Registry | None = None):
    await ainit_app(registry=registry)
    try:
        yield
    finally:
        await get_registry().aclose()