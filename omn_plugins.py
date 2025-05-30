"""Central plugin registry for Omniscience add-ons."""

from typing import List, Protocol, Type


class Plugin(Protocol):
    """Every plugin must expose `run() -> str` and return a summary section."""

    def run(self) -> str: ...


_PLUGINS: List[Type[Plugin]] = []


def register(plugin: Type[Plugin]) -> Type[Plugin]:
    """Decorator: `@register` adds the plugin class to the global list."""
    _PLUGINS.append(plugin)
    return plugin


def run_all_plugins() -> str:
    """Invoke each registered plugin and join their outputs (with error-guard)."""
    outputs: List[str] = []
    for plugin_cls in _PLUGINS:
        try:
            outputs.append(plugin_cls().run())
        except Exception as exc:
            outputs.append(f"[Plugin {plugin_cls.__name__} failed: {exc}]")
    return "\n\n".join(outputs)
