# coding=utf-8
"""Flood on buildings impact function."""
from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsRectangle,
    QgsFeatureRequest,
    QgsGeometry
)

from safe.impact_functions.inundation.flood_on_buildings.\
    metadata_definitions import FloodImpactMetadata
from safe.impact_functions.base import ImpactFunction
from safe.utilities.i18n import tr
from safe.common.exceptions import GetDataError


class FloodImpactFunction(ImpactFunction):
    """Impact function for flood on buildings."""

    _metadata = FloodImpactMetadata

    def __init__(self):
        """Constructor (calls ctor of base class)."""
        super(FloodImpactFunction, self).__init__()

        self.hazard_provider = None
        self.affected_field_index = -1

    def prepare(self):
        """Prepare this impact function for running the analysis.

        .. seealso:: impact_functions.base.prepare_for_run()

        Calls the prepare_for_run method of the impact function base class and
        then implements any specfic checks needed by this impact function.

        :raises: GetDataError
        """
        super(FloodImpactFunction, self).prepare()

        affected_field = self.parameters['affected_field']
        self.hazard_provider = self.hazard.dataProvider()
        self.affected_field_index = self.hazard.fieldNameIndex(
            affected_field.value)
        if self.affected_field_index == -1:
            message = tr('''Parameter "Affected Field"(='%s')
                is not present in the
                attribute table of the hazard layer.''' %
                         (affected_field.value, ))
            raise GetDataError(message)

    def _tabulate(self, building_count, buildings_by_type, flooded_count):
        """Helper to perform tabulation."""
        tabulated_impact = dict()
        tabulated_impact['headings'] = [
            tr('Building Type'),
            tr('Flooded'),
            tr('Total')
        ]
        tabulated_impact['totals'] = [
            tr('All'),
            int(flooded_count),
            int(building_count)]
        tabulated_impact['tabulation_title'] = tr('Breakdown by building type')
        tabulation = []
        for t, v in buildings_by_type.iteritems():
            tabulation.append([t, int(v['flooded']), int(v['total'])])
        tabulated_impact['tabulation'] = tabulation
        tabulated_impact['title'] = tr('Buildings inundated')
        self._tabulated_impact = tabulated_impact

    def _style(self, target_field):
        """Helper to create style."""
        style_classes = [
            dict(label=tr('Not Inundated'), value=0, colour='#1EFC7C',
                 transparency=0, size=0.5),
            dict(label=tr('Inundated'), value=1, colour='#F31A1C',
                 transparency=0, size=0.5)]
        style_info = dict(
            target_field=target_field,
            style_classes=style_classes,
            style_type='categorizedSymbol')
        self.style_info = style_info

    def run(self):
        """Run the impact function."""
        # First fo any generic run work defined in the ABC.
        self.prepare()

        target_field = self.parameters['flooded_target_field']
        building_type_field = self.parameters['building_type_field']
        affected_value_parameter = self.parameters['affected_value']

        crs = self.exposure.crs().toWkt()
        exposure_provider = self.exposure.dataProvider()
        fields = exposure_provider.fields()
        # If target_field does not exist, add it:
        if fields.indexFromName(target_field.value) == -1:
            exposure_provider.addAttributes(
                [QgsField(target_field.value, QVariant.Int)])
        target_field_index = exposure_provider.fieldNameIndex(target_field.value)
        fields = exposure_provider.fields()

        # Create layer for store the lines from exposure and extent
        building_layer = QgsVectorLayer(
            'Polygon?crs=' + crs, 'impact_buildings', 'memory')
        building_provider = building_layer.dataProvider()

        # Set attributes
        building_provider.addAttributes(fields.toList())
        building_layer.startEditing()
        building_layer.commitChanges()

        # Filter geometry and data using the extent
        extent = QgsRectangle(*self.extent)
        request = QgsFeatureRequest()
        request.setFilterRect(extent)

        # Split building_layer by hazard and save as result:
        #   1) Filter from hazard inundated features
        #   2) Mark buildings as inundated (1) or not inundated (0)

        affected_field_type = self.hazard_provider.fields()[
            self.affected_field_index].typeName()
        if affected_field_type in ['Real', 'Integer']:
            affected_value = float(affected_value_parameter.value)
        else:
            affected_value = affected_value_parameter.value

        hazard_data = self.hazard.getFeatures(request)
        hazard_poly = None
        for multi_polygon in hazard_data:
            attributes = multi_polygon.attributes()
            if attributes[self.affected_field_index] != affected_value:
                continue
            if hazard_poly is None:
                hazard_poly = QgsGeometry(multi_polygon.geometry())
            else:
                # Make geometry union of inundated polygons
                # But some multi_polygon.geometry() could be invalid, skip them
                tmp_geometry = hazard_poly.combine(multi_polygon.geometry())
                try:
                    if tmp_geometry.isGeosValid():
                        hazard_poly = tmp_geometry
                except AttributeError:
                    pass

        if hazard_poly is None:
            message = tr('Hazard Polygon is None')
            raise GetDataError(message)

        exposure_features = self.exposure.getFeatures(request)
        for feature in exposure_features:
            building_geometry = feature.geometry()
            attributes = feature.attributes()
            l_feat = QgsFeature()
            l_feat.setGeometry(building_geometry)
            l_feat.setAttributes(attributes)
            if hazard_poly.intersects(building_geometry):
                l_feat.setAttribute(target_field_index, 1)
            else:

                l_feat.setAttribute(target_field_index, 0)
            # Synctactic sugar to discard return values
            (_, __) = building_layer.dataProvider().addFeatures([l_feat])
        building_layer.updateExtents()

        # Generate simple impact report

        building_count = flooded_count = 0  # Count of buildings
        buildings_by_type = dict()      # Length of flooded roads by types

        buildings_data = building_layer.getFeatures()
        building_type_field_index = building_layer.fieldNameIndex(
            building_type_field.value)
        for building in buildings_data:
            building_count += 1
            attributes = building.attributes()
            building_type = attributes[building_type_field_index]
            if building_type in [None, 'NULL', 'null', 'Null']:
                building_type = 'Unknown type'
            if building_type not in buildings_by_type:
                buildings_by_type[building_type] = {'flooded': 0, 'total': 0}
            buildings_by_type[building_type]['total'] += 1

            if attributes[target_field_index] == 1:
                flooded_count += 1
                buildings_by_type[building_type]['flooded'] += 1

        self._tabulate(building_count, buildings_by_type, flooded_count)

        self._style(target_field)

        self._impact = building_layer
        # Convert QgsVectorLayer to inasafe layer and return it.
        # building_layer = Vector(
        #     data=building_layer,
        #     name=tr('Flooded buildings'),
        #     keywords={
        #         'impact_summary': impact_summary,
        #         'map_title': map_title,
        #         'target_field': target_field},
        #     style_info=style_info)
        # return building_layer
