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
from safe.common.tables import Table, TableRow
from safe.common.utilities import format_int, get_osm_building_usage, verify
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.impact_functions.core import get_question, get_exposure_layer, \
    get_hazard_layer

from safe.impact_functions.inundation.flood_on_buildings.\
    metadata_definitions import FloodImpactMetadata
from safe.impact_functions.base import ImpactFunction
from safe.storage.utilities import DEFAULT_ATTRIBUTE
from safe.storage.vector import Vector
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
        self.target_field = 'INUNDATED'

    @property
    def function_type(self):
        return 'old-style'

    def run(self, layers=None):
        """Flood impact to buildings (e.g. from Open Street Map).

         :param layers: List of layers expected to contain.
                * hazard_layer: Hazard layer of flood
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer
        """
        # FIXME: need to set extent in base prepare
        # self.prepare()

        threshold = self.parameters['threshold'].value  # Flood threshold [m]

        verify(isinstance(threshold, float),
               'Expected thresholds to be a float. Got %s' % str(threshold))

        # Extract data
        if layers is not None:
            hazard_layer = get_hazard_layer(layers)  # Depth
            exposure_layer = get_exposure_layer(layers)  # Building locations
        else:
            hazard_layer = self.hazard
            exposure_layer = self.exposure

        question = get_question(
            hazard_layer.get_name(),
            exposure_layer.get_name(),
            self)

        # Determine attribute name for hazard levels
        if hazard_layer.is_raster:
            mode = 'grid'
            hazard_attribute = 'depth'
        else:
            mode = 'regions'
            hazard_attribute = None

        # Interpolate hazard level to building locations
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer, attribute_name=hazard_attribute)

        # Extract relevant exposure data
        attribute_names = interpolated_layer.get_attribute_names()
        features = interpolated_layer.get_data()
        total_features = len(interpolated_layer)
        buildings = {}

        # The number of affected buildings
        affected_count = 0

        # The variable for grid mode
        inundated_count = 0
        wet_count = 0
        dry_count = 0
        inundated_buildings = {}
        wet_buildings = {}
        dry_buildings = {}

        # The variable for regions mode
        affected_buildings = {}

        if mode == 'grid':
            for i in range(total_features):
                # Get the interpolated depth
                water_depth = float(features[i]['depth'])
                if water_depth <= 0:
                    inundated_status = 0  # dry
                elif water_depth >= threshold:
                    inundated_status = 1  # inundated
                else:
                    inundated_status = 2  # wet

                # Count affected buildings by usage type if available
                usage = get_osm_building_usage(attribute_names, features[i])
                if usage is not None and usage != 0:
                    key = usage
                else:
                    key = 'unknown'

                if key not in buildings:
                    buildings[key] = 0
                    inundated_buildings[key] = 0
                    wet_buildings[key] = 0
                    dry_buildings[key] = 0

                # Count all buildings by type
                buildings[key] += 1
                if inundated_status is 0:
                    # Count dry buildings by type
                    dry_buildings[key] += 1
                    # Count total dry buildings
                    dry_count += 1
                if inundated_status is 1:
                    # Count inundated buildings by type
                    inundated_buildings[key] += 1
                    # Count total dry buildings
                    inundated_count += 1
                if inundated_status is 2:
                    # Count wet buildings by type
                    wet_buildings[key] += 1
                    # Count total wet buildings
                    wet_count += 1
                # Add calculated impact to existing attributes
                features[i][self.target_field] = inundated_status
        elif mode == 'regions':
            for i in range(total_features):
                # Use interpolated polygon attribute
                atts = features[i]

                # FIXME (Ole): Need to agree whether to use one or the
                # other as this can be very confusing!
                # For now look for 'affected' first
                if 'affected' in atts:
                    # E.g. from flood forecast
                    # Assume that building is wet if inside polygon
                    # as flagged by attribute Flooded
                    res = atts['affected']
                    if res is None:
                        inundated_status = False
                    else:
                        inundated_status = bool(res)
                elif 'FLOODPRONE' in atts:
                    res = atts['FLOODPRONE']
                    if res is None:
                        inundated_status = False
                    else:
                        inundated_status = res.lower() == 'yes'
                elif DEFAULT_ATTRIBUTE in atts:
                    # Check the default attribute assigned for points
                    # covered by a polygon
                    res = atts[DEFAULT_ATTRIBUTE]
                    if res is None:
                        inundated_status = False
                    else:
                        inundated_status = res
                else:
                    # there is no flood related attribute
                    message = (
                        'No flood related attribute found in %s. I was '
                        'looking for either "affected", "FLOODPRONE" or '
                        '"inapolygon". The latter should have been '
                        'automatically set by call to '
                        'assign_hazard_values_to_exposure_data(). Sorry I '
                        'can\'t help more.')
                    raise Exception(message)

                # Count affected buildings by usage type if available
                usage = get_osm_building_usage(attribute_names, features[i])
                if usage is not None and usage != 0:
                    key = usage
                else:
                    key = 'unknown'

                if key not in buildings:
                    buildings[key] = 0
                    affected_buildings[key] = 0

                # Count all buildings by type
                buildings[key] += 1
                if inundated_status is True:
                    # Count affected buildings by type
                    affected_buildings[key] += 1
                    # Count total affected buildings
                    affected_count += 1

                # Add calculated impact to existing attributes
                features[i][self.target_field] = int(inundated_status)
        else:
            message = (tr('Unknown hazard type %s. Must be either "depth" or '
                          '"grid"') % mode)
            raise Exception(message)

        if mode == 'grid':
            affected_count = inundated_count + wet_count

        # Lump small entries and 'unknown' into 'other' category
        for usage in buildings.keys():
            x = buildings[usage]
            if x < 25 or usage == 'unknown':
                if 'other' not in buildings:
                    buildings['other'] = 0
                    if mode == 'grid':
                        inundated_buildings['other'] = 0
                        wet_buildings['other'] = 0
                        dry_buildings['other'] = 0
                    elif mode == 'regions':
                        affected_buildings['other'] = 0

                buildings['other'] += x
                if mode == 'grid':
                    inundated_buildings['other'] += inundated_buildings[usage]
                    wet_buildings['other'] += wet_buildings[usage]
                    dry_buildings['other'] += dry_buildings[usage]
                    del buildings[usage]
                    del inundated_buildings[usage]
                    del wet_buildings[usage]
                    del dry_buildings[usage]
                elif mode == 'regions':
                    affected_buildings['other'] += affected_buildings[usage]
                    del buildings[usage]
                    del affected_buildings[usage]

        # Result
        self._tabulate(mode, question, inundated_count, wet_count, dry_count, total_features,
                       affected_count, attribute_names, buildings, inundated_buildings,
                       wet_buildings, dry_buildings, affected_buildings, threshold)
        impact_summary = Table(self._tabulated_impact).toNewlineFreeString()
        impact_table = impact_summary

        # Prepare impact layer
        map_title = tr('Buildings inundated')
        legend_title = tr('Structure inundated status')
        legend_units = ''

        self._style(mode, threshold)

        # Create vector layer and return
        vector_layer = Vector(
            data=features,
            projection=interpolated_layer.get_projection(),
            geometry=interpolated_layer.get_geometry(),
            name=tr('Estimated buildings affected'),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'target_field': self.target_field,
                'map_title': map_title,
                'legend_units': self.legend_units,
                'legend_title': legend_title,
                'buildings_total': total_features,
                'buildings_affected': affected_count},
            style_info=self.style_info)
        self._impact = vector_layer
        return vector_layer

    def prepare(self):
        """Prepare this impact function for running the analysis.

        .. seealso:: impact_functions.base.prepare_for_run()

        Calls the prepare_for_run method of the impact function base class and
        then implements any specfic checks needed by this impact function.

        :raises: GetDataError
        """
        super(ImpactFunction, self).prepare()

        affected_field = self.parameters()['affected_field']
        self.hazard_provider = self.hazard.dataProvider()
        self.affected_field_index = self.hazard_provider.fieldNameIndex(
            affected_field)
        if self.affected_field_index == -1:
            message = tr('''Parameter "Affected Field"(='%s')
                is not present in the
                attribute table of the hazard layer.''' % (affected_field, ))
            raise GetDataError(message)

    def _tabulate(self, mode, question, inundated_count, wet_count, dry_count, total_features,
                  affected_count, attribute_names, buildings, inundated_buildings, wet_buildings,
                  dry_buildings, affected_buildings, threshold):
        """Helper to perform tabulation."""
        # Generate simple impact report
        table_body = []
        if mode == 'grid':
            table_body = [
                question,
                TableRow([tr('Building type'),
                          tr('Number Inundated'),
                          tr('Number of Wet Buildings'),
                          tr('Number of Dry Buildings'),
                          tr('Total')], header=True),
                TableRow(
                    [tr('All'),
                     format_int(inundated_count),
                     format_int(wet_count),
                     format_int(dry_count),
                     format_int(total_features)])]
        elif mode == 'regions':
            table_body = [
                question,
                TableRow([tr('Building type'),
                          tr('Number flooded'),
                          tr('Total')], header=True),
                TableRow([tr('All'),
                          format_int(affected_count),
                          format_int(total_features)])]

        school_closed = 0
        hospital_closed = 0
        # Generate break down by building usage type if available
        list_type_attribute = [
            'TYPE', 'type', 'amenity', 'building_t', 'office',
            'tourism', 'leisure', 'building']
        intersect_type = set(attribute_names) & set(list_type_attribute)
        if len(intersect_type) > 0:
            # Make list of building types
            building_list = []
            for usage in buildings:
                building_type = usage.replace('_', ' ')

                # Lookup internationalised value if available
                building_type = tr(building_type)
                if mode == 'grid':
                    building_list.append([
                        building_type.capitalize(),
                        format_int(inundated_buildings[usage]),
                        format_int(wet_buildings[usage]),
                        format_int(dry_buildings[usage]),
                        format_int(buildings[usage])])
                elif mode == 'regions':
                    building_list.append([
                        building_type.capitalize(),
                        format_int(affected_buildings[usage]),
                        format_int(buildings[usage])])

                if usage.lower() == 'school':
                    school_closed = 0
                    if mode == 'grid':
                        school_closed += inundated_buildings[usage]
                        school_closed += wet_buildings[usage]
                    elif mode == 'regions':
                        school_closed = affected_buildings[usage]
                if usage.lower() == 'hospital':
                    hospital_closed = 0
                    if mode == 'grid':
                        hospital_closed += inundated_buildings[usage]
                        hospital_closed += wet_buildings[usage]
                    elif mode == 'regions':
                        hospital_closed = affected_buildings[usage]

            # Sort alphabetically
            building_list.sort()

            table_body.append(TableRow(tr('Breakdown by building type'),
                                       header=True))
            for row in building_list:
                s = TableRow(row)
                table_body.append(s)

        # Action Checklist Section
        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(
            tr('Are the critical facilities still open?')))
        table_body.append(TableRow(
            tr('Which structures have warning capacity (eg. sirens, speakers, '
               'etc.)?')))
        table_body.append(TableRow(
            tr('Which buildings will be evacuation centres?')))
        table_body.append(TableRow(
            tr('Where will we locate the operations centre?')))
        table_body.append(TableRow(
            tr('Where will we locate warehouse and/or distribution centres?')))

        if school_closed > 0:
            table_body.append(TableRow(
                tr('Where will the students from the %s closed schools go to '
                   'study?') % format_int(school_closed)))

        if hospital_closed > 0:
            table_body.append(TableRow(
                tr('Where will the patients from the %s closed hospitals go '
                   'for treatment and how will we transport them?') %
                format_int(hospital_closed)))

        # Notes Section
        table_body.append(TableRow(tr('Notes'), header=True))
        if mode == 'grid':
            table_body.append(TableRow(
                tr('Buildings are said to be inundated when flood levels '
                   'exceed %.1f m') % threshold))
            table_body.append(TableRow(
                tr('Buildings are said to be wet when flood levels '
                   'are greater than 0 m but less than %.1f m') % threshold))
            table_body.append(TableRow(
                tr('Buildings are said to be dry when flood levels '
                   'are less than 0 m')))
            table_body.append(TableRow(
                tr('Buildings are said to be closed if they are inundated or '
                   'wet')))
            table_body.append(TableRow(
                tr('Buildings are said to be open if they are dry')))
        else:
            table_body.append(TableRow(
                tr('Buildings are said to be flooded when in regions marked '
                   'as affected')))
        self._tabulated_impact = table_body

    def _style(self, mode, threshold):
        """Helper to create style."""
        style_classes = []

        if mode == 'grid':
            style_classes = [
                dict(
                    label=tr('Dry (<= 0 m)'),
                    value=0,
                    colour='#1EFC7C',
                    transparency=0,
                    size=1
                ),
                dict(
                    label=tr('Wet (0 m - %.1f m)') % threshold,
                    value=2,
                    colour='#FF9900',
                    transparency=0,
                    size=1
                ),
                dict(
                    label=tr('Inundated (>= %.1f m)') % threshold,
                    value=1,
                    colour='#F31A1C',
                    transparency=0,
                    size=1
                )]
            legend_units = tr('(inundated, wet, or dry)')
        elif mode == 'regions':
            style_classes = [
                dict(
                    label=tr('Not Inundated'),
                    value=0,
                    colour='#1EFC7C',
                    transparency=0,
                    size=1),
                dict(
                    label=tr('Inundated'),
                    value=1,
                    colour='#F31A1C',
                    ztransparency=0, size=1)]
            legend_units = tr('(inundated or not inundated)')

        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')
        self.style_info = style_info
        self.legend_units = legend_units