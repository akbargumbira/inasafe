
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
            'title': tr('Be flooded'),
            # should be a list, but we can do it later.
            'author': 'Ole Nielsen and Kristy van Putten',
            'date_implemented': 'N/A',
            'overview': tr(
                'To assess the impacts of (flood or tsunami) inundation '
                'on building footprints originating from OpenStreetMap '
                '(OSM).'),
            'detailed_description': tr(
                'The inundation status is calculated for each building '
                '(using the centroid if it is a polygon) based on the '
                'hazard levels provided. if the hazard is given as a '
                'raster a threshold of 1 meter is used. This is '
                'configurable through the InaSAFE interface. If the '
                'hazard is given as a vector polygon layer buildings are '
                'considered to be impacted depending on the value of '
                'hazard attributes (in order) affected" or "FLOODPRONE": '
                'If a building is in a region that has attribute '
                '"affected" set to True (or 1) it is impacted. If '
                'attribute "affected" does not exist but "FLOODPRONE" '
                'does, then the building is considered impacted if '
                '"FLOODPRONE" is "yes". If neither affected" nor '
                '"FLOODPRONE" is available, a building will be impacted '
                'if it belongs to any polygon. The latter behaviour is '
                'implemented through the attribute "inapolygon" which is '
                'automatically assigned.'),
            'hazard_input': tr(
                'A hazard raster layer where each cell represents flood '
                'depth (in meters), or a vector polygon layer where each '
                'polygon represents an inundated area. In the latter '
                'case, the following attributes are recognised '
                '(in order): "affected" (True or False) or "FLOODPRONE" '
                '(Yes or No). (True may be represented as 1, False as 0'),
            'exposure_input': tr(
                'Vector polygon or point layer extracted from OSM where '
                'each feature represents the footprint of a building.'),
            'output': tr(
                'Vector layer contains building is estimated to be '
                'flooded and the breakdown of the building by type.'),
            'actions': tr(
                'Provide details about where critical infrastructure '
                'might be flooded'),
            'limitations': [
                tr('This function only flags buildings as impacted or not '
                   'either based on a fixed threshold in case of raster '
                   'hazard or the the attributes mentioned under input '
                   'in case of vector hazard.')
            ],
            'citations': [],
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

