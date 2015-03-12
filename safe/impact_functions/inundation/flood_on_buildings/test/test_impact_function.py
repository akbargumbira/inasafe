from safe.storage.vector import Vector

__author__ = 'lucernae'

import unittest
from safe.test.utilities import HAZDATA, TESTDATA, \
    clone_shp_layer, get_qgis_app
from safe.impact_functions.registry import Registry
from safe.impact_functions.inundation.flood_on_buildings.\
    impact_function import FloodImpactFunction
from safe.definitions import unit_wetdry, layer_vector_polygon, \
    exposure_structure, unit_building_type_type, hazard_flood

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestImpactFunction(unittest.TestCase):

    def setUp(self):
        self.registry = Registry()
        self.registry.register(FloodImpactFunction)

    def test_run(self):
        function = self.registry.get('FloodImpactFunction')

        # Calculate impact using API
        hazard_layer = clone_shp_layer(
            'test_flood_building_impact_hazard', True, TESTDATA)
        exposure_layer = clone_shp_layer(
            'test_flood_building_impact_exposure', True, TESTDATA)

        hazard = Vector(data=hazard_layer)
        exposure = Vector(data=exposure_layer)

        function.hazard = hazard
        function.exposure = exposure
        function.run()

        impact_layer = function.impact

        # Extract calculated result
        keywords = impact_layer.get_keywords()
        buildings_total = keywords['buildings_total']
        buildings_affected = keywords['buildings_affected']

        self.assertEqual(buildings_total, 67)
        self.assertEqual(buildings_affected, 41)

    def test_filter(self):
        hazard_keywords = {
            'subcategory': hazard_flood,
            'units': unit_wetdry,
            'layer_constraints': layer_vector_polygon
        }

        exposure_keywords = {
            'subcategory': exposure_structure,
            'units': unit_building_type_type,
            'layer_constraints': layer_vector_polygon
        }

        print 'List of IF registered:'

        self.registry.list()

        impact_functions = self.registry.filter(
            hazard_keywords, exposure_keywords)
        print 'Number of impact functions filtered : ', len(impact_functions)
        print [x.metadata()['name'] for x in impact_functions]