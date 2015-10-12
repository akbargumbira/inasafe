# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from unittest import TestCase, expectedFailure

from PyQt4.QtCore import QDate, QUrl

from safe.common.exceptions import MetadataInvalidPathError
from safe.metadata.property import (
    CharacterStringProperty,
    DateProperty,
    UrlProperty)


class TestMetadataProperty(TestCase):

    def test_value_date(self):
        test_property = DateProperty(
            'test name',
            QDate.currentDate(),
            'gco:Date'
        )

        test_property.value = QDate.fromString('2015-06-07')

        with self.assertRaises(TypeError):
            test_property.value = 20150607

    def test_value_str(self):
        test_property = CharacterStringProperty(
            'test string',
            'random string',
            'gco:CharacterString'
        )

        with self.assertRaises(TypeError):
            # list is not a valid data type
            test_property.value = ['20150607']

    def test_value_url(self):
        test_property = UrlProperty(
            'test url',
            QUrl('http://inasafe.org'),
            'gmd:URL'
        )

        with self.assertRaises(TypeError):
            test_property.value = 20150607

        # this should work due to casting
        test_property.value = 'http://inasafe.org'

    def test_xml_path(self):
        valid_path = 'gmd:URL'
        invalid_path = 2345

        test_property = UrlProperty(
            'test url',
            QUrl('http://inasafe.org'),
            valid_path
        )
        # xml_path should be read-only
        with self.assertRaises(AttributeError):
            test_property.xml_path = 'random string'

        with self.assertRaises(MetadataInvalidPathError):
            UrlProperty(
                'test url',
                QUrl('http://inasafe.org'),
                invalid_path
            )

    @expectedFailure
    def test_xml_path_stronger(self):
        # TODO (MB): remove expected failure when a better _is_valid_path is
        # implemented
        error_path = '\\test\\path'
        with self.assertRaises(MetadataInvalidPathError):
            UrlProperty(
                'test url',
                QUrl('http://inasafe.org'),
                error_path
            )

    def test_python_type(self):
        test_property = UrlProperty(
            'test url',
            QUrl('http://inasafe.org'),
            'gmd:URL'
        )

        # type should be read-only
        with self.assertRaises(AttributeError):
            test_property.python_type = 'random string'
