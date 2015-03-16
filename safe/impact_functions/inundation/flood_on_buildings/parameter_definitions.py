# coding=utf-8
"""This file is intended to store all available default parameters for IF.."""
from safe_extras.parameters.boolean_parameter import BooleanParameter
from safe_extras.parameters.float_parameter import FloatParameter

__author__ = 'ismailsunni'
__project_name = 'impact_function_registry'
__filename = 'impact_function_parameter'
__date__ = '8/26/14'
__copyright__ = 'imajimatika@gmail.com'
__doc__ = ''

from safe_extras.parameters.string_parameter import StringParameter


def flooded_target_field():
    """Generator for the flooded target field parameter."""
    field = StringParameter()
    field.name = 'Target Field'
    field.is_required = True
    field.help_text = (
        'This field of impact layer marks inundated roads by \'1\' value')
    field.description = (
        'This field of impact layer marks inundated roads by \'1\' value. '
        'This is the longer description of this parameter.')
    field.value = 'flooded'  # default value
    return field


def building_type_field():
    """Generator for the building tpe field parameter."""
    field = BooleanParameter()
    field.name = 'Building Type Field'
    field.is_required = True
    field.help_text = (
        'This field of the exposure layer contains information about building '
        'types')
    field.description = (
        'This field of the exposure layer contains information about building '
        'types This is the longer description of this parameter.')
    field.value = True  # default value
    return field


def affected_field():
    """"Generator for selection of affected field parameter."""
    field = StringParameter()
    field.name = 'Affected Field'
    field.is_required = True
    field.help_text = (
        'This field of the  hazard layer contains information about inundated '
        'areas')
    field.description = (
        'This field of the  hazard layer contains information about inundated '
        'areas. This is the longer description of this parameter.')
    field.value = 'affected'  # default value
    return field


def affected_value():
    """Generator for parameter stating what values constitute 'affected'."""
    field = StringParameter()
    field.name = 'Affected Value'
    field.is_required = True
    field.help_text = (
        'This value in \'affected_field\' of the hazard layer marks the areas '
        'as inundated')
    field.description = (
        'This value in \'affected_field\' of the hazard layer marks the areas '
        'as inundated. This is the longer description of this parameter.')
    field.value = '1'  # default value
    return field


def threshold_parameter_field():
    """
    Generator for parameter stating what values constitute 'parameters'.
    """
    field = FloatParameter()
    field.name = 'Threshold [m]'
    field.is_required = True
    field.help_text = 'Threshold help'
    field.description = 'Threshold description'
    field.value = 1.0
    return field
