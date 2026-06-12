from domain.game.actions import GameActionsMixin
from domain.game.core import GameCoreMixin
from domain.game.legacy import GameLegacyMixin


class Game(GameActionsMixin, GameLegacyMixin, GameCoreMixin):
    """Composed game class split into focused modules."""

    pass
