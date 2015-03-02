
"""Concrete implementation of metadata class for flood impacts."""
from safe.definitions import layer_raster_continuous

from safe.impact_functions.metadata.base import MetadataBase
from safe.impact_functions.metadata.layer_constraints import layer_vector_point
from safe.impact_functions.metadata.units import unit_metres_depth, unit_feet_depth, unit_building_generic
from safe.utilities.i18n import tr
from safe.impact_functions.metadata import (
    hazard_definition,
    hazard_flood,
    hazard_tsunami,
    unit_wetdry,
    exposure_definition,
    exposure_structure,
    unit_building_type_type,
    layer_vector_polygon)


class FloodBuildingImpactMetadata(MetadataBase):
    """Metadata for Flood Impact Function.

    .. versionadded:: 2.1

    We only need to re-implement get_metadata(), all other behaviours
    are inherited from the abstract base class.
    """
    @staticmethod
    def as_dict():
        """Return metadata as a dictionary.

        This is a static method. You can use it to get the metadata in
        dictionary format for an impact function.

        :returns: A dictionary representing all the metadata for the
            concrete impact function.
        :rtype: dict
        """
        dict_meta = {
                'id': 'FloodBuildingImpactFunction',
                'name': tr('Flood Building Impact Function'),
                'impact': tr('Be flooded'),
                'author': ['Ole Nielsen', 'Kristy van Putten'],
                'date_implemented': 'N/A',
                'overview': tr(
                    'To assess the impacts of (flood or tsunami) inundation '
                    'on building footprints originating from OpenStreetMap '
                    '(OSM).'),
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategories': [
                            hazard_flood,
                            hazard_tsunami
                        ],
                        'units': [
                            unit_wetdry,
                            unit_metres_depth,
                            unit_feet_depth],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_raster_continuous,
                        ]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategories': [exposure_structure],
                        'units': [
                            unit_building_type_type,
                            unit_building_generic],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point
                        ]
                    }
                }
            }
        return dict_meta

