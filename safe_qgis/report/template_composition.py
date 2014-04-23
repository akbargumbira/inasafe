# coding=utf-8
"""
Module to handle report templating.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '21/03/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

#noinspection PyPackageRequirements
from PyQt4 import QtCore, QtXml

from qgis.core import QgsComposition, QgsMapRenderer

from safe_qgis.exceptions import (
    LoadingTemplateError,
    TemplateElementMissingError)


class TemplateComposition(object):
    """Class for handling composition using template."""
    def __init__(self):
        """Class constructor.
        """
        self.template_path = ''
        self.composition = None
        self.renderer = None
        # Needed elements on the template. It is set from outer class/function
        self.component_ids = []
        # Flag for verbose warning on template
        self.warning_verbose_flag = False
        # Template Map Substitution
        self.template_substitution = {}

    @staticmethod
    def tr(string):
        """We implement this since we do not inherit QObject.

        :param string: String for translation.
        :type string: QString, str

        :returns: Translated version of theString.
        :rtype: QString
        """
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        return QtCore.QCoreApplication.translate('TemplateComposition', string)

    def set_template_path(self, path):
        """Set template path.

        :param path: Path for the template
        :type path: str
        """
        self.template_path = path

    def set_renderer(self, renderer):
        """Set composition renderer.

        :param renderer: The renderer for the composition
        :type renderer: QgsMapRenderer
        """
        self.renderer = renderer

    def set_component_ids(self, component_ids):
        """Set component ids that should exist on this template.

        :param component_ids: List of component ids of this template
        :type component_ids: list
        """
        self.component_ids = component_ids

    def set_template_substitution(self, substitution):
        """Set substitution for the template.

        :param substitution: the substituion for the template.
        :type substitution: dict
        """
        self.template_substitution = substitution

    def load_template(self):
        """Load a QgsComposer map from a template.

        :raises: TemplateElementMissingError - when template elements are
            missing
        """
        # Create Composition
        self.composition = QgsComposition(self.renderer)

        template_file = QtCore.QFile(self.template_path)
        template_file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)
        template_content = template_file.readAll()
        template_file.close()

        # Create a dom document containing template content
        document = QtXml.QDomDocument()
        document.setContent(template_content)

        # Load template
        load_status = self.composition.loadFromTemplate(
            document, self.template_substitution)
        if not load_status:
            raise LoadingTemplateError(
                self.tr('Error loading template %s') %
                self.template_path)

    def validate_template(self):
        """Validate template to check the missing elements on self.composition.

        :return: Sublist of component_ids missing from composition
        :rtype: list
        """
        missing_elements = []
        for component_id in self.component_ids:
            component = self.composition.getComposerItemById(component_id)
            if component is None:
                missing_elements.append(component_id)

        # Validate the template components
        if self.warning_verbose_flag:
            if len(missing_elements) > 0:
                missing_elements_string = ''
                for missing_element in missing_elements:
                    missing_elements_string += missing_element + ', '
                missing_elements_string = missing_elements_string[:-2]
                raise TemplateElementMissingError(
                    self.tr(
                        'The composer template you are printing to is '
                        'missing '
                        'these elements: %s') % missing_elements_string)
