from safe.utilities.i18n import tr

unit_building_generic = {
    'id': 'building_generic',
    'name': tr('building generic'),
    'description': tr(
        '<b>Building generic</b> unit means that there is no building type '
        'attribute in the exposure data.')
}
unit_building_type_type = {
    'id': 'building_type',
    'name': tr('building type'),
    'description': tr(
        '<b>Building type</b> is a unit that represent the type of the '
        'building. In this case, building type will be used to group the '
        'result of impact function.'),
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_feet_depth = {
    'id': 'feet_depth',
    'name': tr('feet'),
    'description': tr(
        '<b>Feet</b> are an imperial unit of measure. There are 12 '
        'inches in 1 foot and 3 feet in 1 yard. '
        'In this case <b>feet</b> are used to describe the water depth.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_metres_depth = {
    'id': 'metres_depth',
    'name': tr('metres'),
    'description': tr(
        '<b>metres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 metre. In this case <b>metres</b> are used to '
        'describe the water depth.'),
    'constraint': 'continuous',
    'default_attribute': 'depth'  # applies to vector only
}
unit_mmi = {
    'id': 'mmi',
    'name': tr('MMI'),
    'description': tr(
        'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
        'the intensity of ground shaking from a earthquake based on the '
        'effects observed by people at the surface.'),
    'constraint': 'continuous',
    'default_attribute': 'mmi'  # applies to vector only
}
unit_normalised = {
    'id': 'normalised',
    'name': tr('normalised'),
    'description': tr(
        '<b>Normalised</b> data can be hazard or exposure data where the '
        'values '
        'have been classified or coded.'
    ),
    'constraint': 'continuous'
}
unit_people_per_pixel = {
    'id': 'people_per_pixel',
    'name': tr('people per pixel'),
    'description': tr(
        '<b>Count</b> is the number of people in each cell. For example <b>'
        'population count</b> might be measured as the number of people per '
        'pixel in a raster data set. This unit is relevant for population '
        'rasters in geographic coordinates.'),
    'constraint': 'continuous'
}
unit_road_type_type = {
    'id': 'road_type',
    'name': tr('Road Type'),
    'description': tr(
        '<b>Road type</b> is a unit that represent the type of the road. '
        'In this case, road type will be used to group the result of impact '
        'function.'),
    'constraint': 'unique values',
    'default_attribute': 'type'
}
unit_volcano_categorical = {
    'id': 'volcano_categorical',
    'name': tr('volcano categorical'),
    'description': tr(
        'This is a ternary description for an area. The area is either '
        'has <b>low</b>, <b>medium</b>, or <b>high</b> impact from the '
        'volcano.'),
    'constraint': 'categorical',
    'default_attribute': 'affected',
    'default_category': 'high',
    'classes': [
        {
            'name': 'high',
            'description': tr('Distance from the volcano.'),
            'string_defaults': ['Kawasan Rawan Bencana I',
                                'high'],
            'numeric_default_min': 0,
            'numeric_default_max': 3,
            'optional': False
        },
        {
            'name': 'medium',
            'description': tr('Distance from the volcano.'),
            'string_defaults': ['Kawasan Rawan Bencana II',
                                'medium'],
            'numeric_default_min': 3,
            'numeric_default_max': 5,
            'optional': False
        },
        {
            'name': 'low',
            'description': tr('Distance from the volcano.'),
            'string_defaults': ['Kawasan Rawan Bencana III',
                                'low'],
            'numeric_default_min': 5,
            'numeric_default_max': 10,
            'optional': False
        }
    ]
}

# constant
small_number = 2 ** -53  # I think this is small enough

unit_wetdry = {
    'id': 'wetdry',
    'constraint': 'categorical',
    'default_attribute': 'affected',
    'default_category': 'wet',
    'name': tr('wet / dry'),
    'description': tr(
        'This is a binary description for an area. The area is either '
        '<b>wet</b> (affected by flood water) or <b>dry</b> (not affected '
        'by flood water). This unit does not describe how <b>wet</b> or '
        '<b>dry</b> an area is.'),
    'classes': [
        {
            'name': 'wet',
            'description': tr('Water above ground height.'),
            'string_defaults': ['wet', '1', 'YES', 'y', 'yes'],
            'numeric_default_min': 1,
            'numeric_default_max': 9999999999,
            'optional': True
        },
        {
            'name': 'dry',
            'description': tr('No water above ground height.'),
            'string_defaults': ['dry', '0', 'No', 'n', 'no'],
            'numeric_default_min': 0,
            'numeric_default_max': (1 - small_number),
            'optional': True
        }
    ]
}

def old_to_new_unit_id(old_unit_id):
    """Convert old unit id to new unit id in keyword system.

    :param old_unit_id: Unit id in old keyword system.
    :type old_unit_id: str

    :returns: Unit id in new keyword system.
    :rtype: str
    """

    # These converter is used for wizard only, converting old keywords to new
    # keywords as default value when run the wizard.
    old_to_new_keywords = {
        'm': 'metres_depth',
        'mmi': 'MMI'
    }

    return old_to_new_keywords.get(old_unit_id, old_unit_id)
