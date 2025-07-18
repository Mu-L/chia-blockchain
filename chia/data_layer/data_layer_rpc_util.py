from __future__ import annotations

from typing import Any

from typing_extensions import Protocol, Self

# If accepted for general use then this should be moved to a common location
# and probably implemented by the framework instead of manual decoration.


class MarshallableProtocol(Protocol):
    @classmethod
    def unmarshal(cls, marshalled: dict[str, Any]) -> Self: ...

    def marshal(self) -> dict[str, Any]: ...


class UnboundRoute(Protocol):
    async def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        pass


class UnboundMarshalledRoute(Protocol):
    async def __call__(protocol_self, self: Any, request: MarshallableProtocol) -> MarshallableProtocol:
        pass


class RouteDecorator(Protocol):
    def __call__(self, route: UnboundMarshalledRoute) -> UnboundRoute:
        pass


def marshal() -> RouteDecorator:
    def decorator(route: UnboundMarshalledRoute) -> UnboundRoute:
        from typing import get_type_hints

        hints = get_type_hints(route)
        request_class: type[MarshallableProtocol] = hints["request"]

        async def wrapper(self: object, request: dict[str, object]) -> dict[str, object]:
            # import json
            # name = route.__name__
            # print(f"\n ==== {name} request.json\n{json.dumps(request, indent=2)}")
            unmarshalled_request = request_class.unmarshal(request)

            response = await route(self, request=unmarshalled_request)
            marshalled_response = response.marshal()
            # print(f"\n ==== {name} response.json\n{json.dumps(marshalled_response, indent=2)}")

            return marshalled_response

        # type ignoring since mypy is having issues with bound vs. unbound methods
        return wrapper  # type: ignore[return-value]

    return decorator
