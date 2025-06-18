# loghelpers/context/__init__.py
from .. import Configuration
from ..config import Feature
from ..context.default_provider import DefaultProvider
from ..context.registry import ContextProviders
from ..exceptions import ProviderExecutionException, DuplicateProviderKeyException

ContextProviders.register("default", DefaultProvider())


def gather_context(config: Configuration) -> dict:
    """
    Gather the current context from all registered providers.

    Returns:
        A dictionary containing the context data from all providers.
    """
    providers = ContextProviders.gather()
    context = {}
    for name, provider in providers.items():
        try:
            result = provider()
        except Exception as e:
            raise ProviderExecutionException(name, e)
        for key, value in result.items():
            if key not in context:
                context[key] = value
            else:
                if Feature.ALLOW_PROVIDER_OVERWRITE in config.features:
                    context[key] = value
                else:
                    raise DuplicateProviderKeyException(name, key)
    return context
