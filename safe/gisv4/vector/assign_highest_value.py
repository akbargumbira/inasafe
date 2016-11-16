# coding=utf-8

"""
Assign the highest value to an exposure according to a hazard layer.

Issue https://github.com/inasafe/inasafe/issues/3192
"""

import logging
from PyQt4.QtCore import QPyNullVariant
from qgis.core import (
    QGis,
    QgsFeatureRequest,
    QgsWKBTypes,
    QgsFeature,
)

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.fields import hazard_class_field
from safe.definitionsv4.hazard_classifications import hazard_classification
from safe.definitionsv4.processing_steps import assign_highest_value_steps
from safe.gisv4.vector.tools import create_memory_layer, create_spatial_index
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def assign_highest_value(exposure_layer, hazard_layer, callback=None):
    """For indivisible polygon exposure layers such as buildings, we need to
    assigned the greatest hazard that each polygon touches and use that as the
     effective hazard class.

    We follow the concept here that any part of the exposure dataset that
    touches the hazard is affected, and the greatest hazard is the effective
    hazard.

    :param exposure_layer: The building vector layer.
    :type exposure_layer: QgsVectorLayer

    :param hazard_layer: The vector layer to use for hazard.
    :type hazard_layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new impact layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = assign_highest_value_steps['output_layer_name']
    processing_step = assign_highest_value_steps['step_name']

    hazard_keywords = hazard_layer.keywords
    hazard_inasafe_fields = hazard_keywords['inasafe_fields']

    if not hazard_keywords.get('classification'):
        raise InvalidKeywordsForProcessingAlgorithm
    if not hazard_inasafe_fields.get(hazard_class_field['key']):
        raise InvalidKeywordsForProcessingAlgorithm

    # We add exposure and hazard fields to the out layer.
    fields = exposure_layer.fields()
    fields.extend(hazard_layer.fields())

    # We create the memory layer.
    writer = create_memory_layer(
        output_layer_name,
        exposure_layer.geometryType(),
        exposure_layer.crs(),
        fields
    )
    writer.startEditing()

    spatial_index = create_spatial_index(hazard_layer)

    # Todo callback
    # total = 100.0 / len(selectionA)

    hazard_field = hazard_inasafe_fields[hazard_class_field['key']]
    index = hazard_layer.fieldNameIndex(hazard_field)

    layer_classification = None
    for classification in hazard_classification['types']:
        if classification['key'] == hazard_keywords['classification']:
            layer_classification = classification
            break

    # Get a ordered list of classes like ['low', 'medium', 'high']
    levels = list(
        reversed([key['key'] for key in layer_classification['classes']]))

    out_feature = QgsFeature()

    # Let's loop over the exposure layer.
    for current, in_feature in enumerate(exposure_layer.getFeatures()):
        # progress.setPercentage(int(current * total))
        geom = in_feature.geometry()
        attributes = in_feature.attributes()

        intersects = spatial_index.intersects(geom.boundingBox())

        # List to store the highest hazard value and attributes.
        highest_hazard_value = [None, None]

        # We need to loop over each intersections exposure / aggregate hazard.
        for i in intersects:

            request = QgsFeatureRequest().setFilterFid(i)
            feature_hazard = next(hazard_layer.getFeatures(request))

            tmp_geom = feature_hazard.geometry()

            if geom.intersects(tmp_geom):

                # We get the value of the hazard.
                hazard_attributes = feature_hazard.attributes()
                hazard_value = hazard_attributes[index]

                if hazard_value:
                    value = levels.index(hazard_value)
                elif isinstance(hazard_value, QPyNullVariant):
                    value = -1
                else:
                    value = -1

                # If it's the first time in the loop, we assign the value.
                # But the hazard value can be null
                if not highest_hazard_value[0]:
                    highest_hazard_value = (
                        value,
                        hazard_attributes
                    )

                    # If it's the highest hazard value, we should skip to the
                    # other exposure feature. We can't find a higher hazard.
                    if hazard_value == levels[-1]:
                        # Need to check that one.
                        break

                else:
                    # This building has already a hazard value.

                    # We compare to a previous feature if the hazard is higher:
                    if value > highest_hazard_value[0]:
                        highest_hazard_value = (
                            value,
                            hazard_attributes
                        )

                    # Let's do a faster processing.
                    continue

                    # We compare size if same hazard value :
                    # if value == highest_hazard_value[0]:
                    #    # TODO We should add another test to check the biggest
                    #     # aggregation area.
                    #     highest_hazard_value = (
                    #         value,
                    #         hazard_attributes
                    #     )

        if not highest_hazard_value[1]:
            # It means the feature has no intersection at all with the
            # aggregation layer at all.
            # The layer has not been clip before in the tests.
            continue

        out_feature.setGeometry(geom)
        attrs = []
        attrs.extend(attributes)
        attrs.extend(highest_hazard_value[1])
        out_feature.setAttributes(attrs)
        writer.addFeature(out_feature)

    writer.commitChanges()

    inasafe_fields = exposure_layer.keywords['inasafe_fields'].copy()
    inasafe_fields.update(hazard_layer.keywords['inasafe_fields'])
    writer.keywords = exposure_layer.keywords
    writer.keywords['inasafe_fields'] = inasafe_fields
    writer.keywords['layer_purpose'] = 'impact'

    writer.keywords['exposure_keywords'] = exposure_layer.keywords
    writer.keywords['aggregation_keywords'] = (
        hazard_layer.keywords['aggregation_keywords'])
    writer.keywords['hazard_keywords'] = (
        hazard_layer.keywords['hazard_keywords'])

    writer.keywords['title'] = output_layer_name

    return writer
