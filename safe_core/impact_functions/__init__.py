"""
Basic plugin framework based on::
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
"""
import os


def load_plugins():
    """Iterate through each plugin dir loading all plugins."""
    dirname = os.path.dirname(__file__)
    # Import all the subdirectories
    for f in os.listdir(dirname):
        if os.path.isdir(os.path.join(dirname, f)):
            try:
                __import__('safe_core.impact_functions.%s' % f)
            except (ImportError, ValueError):
                # Ignore e.g. directories that are not Python modules
                # FIXME (Ole): Should we emit a warning to the log file?
                pass


load_plugins()


from safe_core.impact_functions.core import FunctionProvider
from safe_core.impact_functions.core import get_plugins  # FIXME: Deprecate
from safe_core.impact_functions.core import get_plugin
from safe_core.impact_functions.core import get_admissible_plugins
from safe_core.impact_functions.core import compatible_layers
from safe_core.impact_functions.core import get_function_title
from safe_core.impact_functions.core import get_metadata
from safe_core.impact_functions.core import is_function_enabled
