from functools import partial
from typing import Any

from hydra_zen import BuildsFn
from hydra_zen.typing import HydraSupportedType

from livekit.agents.types import NotGiven


class _LKBuilds(BuildsFn):
    @classmethod
    def _make_hydra_compatible(cls, value: Any, **kwargs) -> HydraSupportedType:
        if isinstance(value, NotGiven):
            return cls.builds(NotGiven)
        return super()._make_hydra_compatible(value, **kwargs)


builds = partial(_LKBuilds.builds, populate_full_signature=True, hydra_convert="all")
