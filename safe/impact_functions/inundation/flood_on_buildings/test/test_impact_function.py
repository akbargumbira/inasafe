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
        function.extent = [106.7865051, -6.1842385,
                           106.9091440, -6.2206013]
        function.extent_crs = [4326]
        function_parameters = function.parameters
        for x in function_parameters.values():
            print '--', x.name, x.value
        print 'Change value of target field to FLOODED:'
        function_parameters['flooded_target_field'].value = 'FLOODED'
        print 'Change value of affected field to FLOODPRONE:'
        function_parameters['affected_field'].value = 'FLOODPRONE'
        print 'Change value of affected field to YES:'
        function_parameters['affected_value'].value = 'YES'
        for x in function_parameters.values():
            print '--', x.name, x.value

        # Calculate impact using API
        hazard_layer = clone_shp_layer(
            'Jakarta_RW_2007flood', True, HAZDATA)
        exposure_layer = clone_shp_layer(
            'OSM_building_polygons_20110905', True, TESTDATA)

        function.hazard = hazard_layer
        function.exposure = exposure_layer

        function.run()

        impact_layer = function.impact

        # Extract calculated result
        icoordinates = impact_layer.featureCount()

        # Check
        print 'Impacted building : ', icoordinates

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