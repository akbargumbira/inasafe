"""
Basic plugin framework based on::
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
"""
from safe.impact_functions.registry import Registry
from safe.impact_functions.inundation.flood_on_buildings.impact_function \
    import FloodImpactFunction
from safe.impact_functions.inundation.flood_osm_building \
    .flood_vector_OSM_building_impact import \
    FloodVectorBuildingImpactFunction


def load_plugins():
    """Iterate through each plugin dir loading all plugins."""
    impact_function_registry = Registry()

    # Register all the Impact Functions
    impact_function_registry.register(FloodImpactFunction)
    impact_function_registry.register(FloodVectorBuildingImpactFunction)

load_plugins()


from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_plugins  # FIXME: Deprecate
from safe.impact_functions.core import get_plugin
from safe.impact_functions.core import get_admissible_plugins
from safe.impact_functions.core import compatible_layers
from safe.impact_functions.core import get_function_title
from safe.impact_functions.core import is_function_enabled
