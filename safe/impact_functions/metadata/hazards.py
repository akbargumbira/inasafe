from safe.utilities.i18n import tr

# categories
hazard_definition = {
    'id': 'hazard',
    'name': tr('hazard'),
    'description': tr(
        'A <b>hazard</b> layer represents '
        'something that will impact on the people or infrastructure '
        'in an area. For example; flood, earthquake, tsunami and  '
        'volcano are all examples of hazards.')
}

# subcategories
hazard_generic = {
    'id': 'generic',
    'name': tr('generic'),
    'description': tr(
        'A generic hazard can be used for any type of hazard where the data '
        'have been classified or generalised. For example: earthquake, flood, '
        'volcano, or tsunami.')
}
hazard_earthquake = {
    'id': 'earthquake',
    'name': tr('earthquake'),
    'description': tr(
        'An <b>earthquake</b> describes the sudden violent shaking of the '
        'ground that occurs as a result of volcanic activity or movement '
        'in the earth\'s crust.')
}
hazard_flood = {
    'id': 'flood',
    'name': tr('flood'),
    'description': tr(
        'A <b>flood</b> describes the inundation of land that is '
        'normally dry by a large amount of water. '
        'For example: A <b>flood</b> can occur after heavy rainfall, '
        'when a river overflows its banks or when a dam breaks. '
        'The effect of a <b>flood</b> is for land that is normally dry '
        'to become wet.')
}
hazard_tephra = {
    'id': 'tephra',
    'name': tr('tephra'),
    'description': tr(
        '<b>Tephra</b> describes the material, such as rock fragments and '
        'ash particles ejected by a volcanic eruption.')
}
hazard_tsunami = {
    'id': 'tsunami',
    'name': tr('tsunami'),
    'description': tr(
        'A <b>tsunami</b> describes a large ocean wave or series or '
        'waves usually caused by an under water earthquake or volcano.'
        'A <b>tsunami</b> at sea may go unnoticed but a <b>tsunami</b> '
        'wave that strikes land may cause massive destruction and '
        'flooding.')
}
hazard_volcano = {
    'id': 'volcano',
    'name': tr('volcano'),
    'description': tr(
        'A <b>volcano</b> describes a mountain which has a vent through '
        'which rock fragments, ash, lava, steam and gases can be ejected '
        'from below the earth\'s surface. The type of material '
        'ejected depends on the type of <b>volcano</b>.')
}

hazard_all = [
    hazard_earthquake,
    hazard_flood,
    hazard_tephra,
    hazard_tsunami,
    hazard_volcano,
    hazard_generic
]
