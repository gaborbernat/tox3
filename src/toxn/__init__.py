"""toxn is a tool to help automate QA tasks"""

from pkg_resources import DistributionNotFound, get_distribution

try:
    # semantic version of the project
    __version__ = get_distribution(__name__).version
except DistributionNotFound:  # pragma: no cover
    __version__ = '0.0.0-DEV'  # pragma: no cover
