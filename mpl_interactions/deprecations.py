# cribbing from matplotlib's approach
# by default DeprecationWarnings are ignored. Define our own class to make sure they are seen

__all__ = ["mpl_interactions_DeprecationWarning"]


class mpl_interactions_DeprecationWarning(DeprecationWarning):
    """A class for issuing deprecation warnings for mpl-interactions users."""
