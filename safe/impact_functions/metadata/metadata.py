# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Metadata for SAFE.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '19/03/14'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from safe.utilities.i18n import tr

# Please group them and sort them alphabetical



















# Converter new keywords to old keywords
converter_dict = {
    'subcategory': {
        'all': [],
        'earthquake': [],
        'flood': [],
        'population': [],
        'road': [],
        'structure': [],
        'tephra': [],
        'tsunami': [],
        'volcano': []
    },
    'layertype': {
        'raster': [],
        'vector': []
    },
    'date_type': {
    },
    'unit': {
        'm': ['metres_depth'],  # FIXME(Ismail): Please check for feet_depth
        'MMI': ['mmi'],
    }
}



