# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid **GUI Keywords Creation Wizard Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '21/02/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QListWidgetItem

from third_party.odict import OrderedDict

from safe_qgis.safe_interface import InaSAFEError
from safe_qgis.ui.keywords_wizard_base import Ui_KeywordsWizardBase
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.utilities import (
    get_error_message,
    is_raster_layer,
    layer_attribute_names)


LOGGER = logging.getLogger('InaSAFE')


class KeywordsWizard(QtGui.QDialog, Ui_KeywordsWizardBase):
    """Dialog implementation class for the InaSAFE keywords wizard."""

    def __init__(self, parent, iface, dock=None, layer=None):
        """Constructor for the dialog.

        .. note:: In QtDesigner the advanced editor's predefined keywords
           list should be shown in english always, so when adding entries to
           cboKeyword, be sure to choose :safe_qgis:`Properties<<` and untick
           the :safe_qgis:`translatable` property.

        :param parent: Parent widget of this dialog.
        :type parent: QWidget

        :param iface: Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param dock: Dock widget instance that we can notify of changes to
            the keywords. Optional.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('InaSAFE')
        self.keywordIO = KeywordIO()
        # note the keys should remain untranslated as we need to write
        # english to the keywords file. The keys will be written as user data
        # in the list widget items.

        self.standard_categories = [{
            'value': 'hazard',
            'name': self.tr('hazard'),
            'description': self.tr('A <b>hazard</b> layer represents '
                'something that will impact the people or infrastructure '
                'in area. For example a flood, earth quake, tsunami '
                'inundation are all different kinds of hazards.'),
            'subcategory_question': self.tr('What kind of hazard does this '
                'layer represent? The choice you make here will determine '
                'which impact functions this hazard layer can be used with. '
                'For example, if you have choose <i>flood</i> you will be '
                'able to use this hazard layer with impact functions such '
                'as <i>flood impact on population</i>.'),
            'subcategories': [{
                'value': 'flood',
                'name': self.tr('flood'),
                'description': self.tr('description of subcategory: flood'),
                'units': [{
                    'value': 'meters',
                    'name': self.tr('meters'),
                    'description': self.tr('description of meters')
                },{
                    'value': 'feet',
                    'name': self.tr('feet'),
                    'description': self.tr('description of feet')
                },{
                    'value': 'wet/dry',
                    'name': self.tr('wet/dry'),
                    'description': self.tr('description of wet/dry')
                }]
            },{
                'value': 'tsunami',
                'name': self.tr('tsunami'),
                'description': self.tr('description of subcategory: tsunami'),
                'units': [{
                    'value': 'meters',
                    'name': self.tr('meters'),
                    'description': self.tr('description of meters')
                },{
                    'value': 'feet',
                    'name': self.tr('feet'),
                    'description': self.tr('description of feet')
                },{
                    'value': 'wet/dry',
                    'name': self.tr('wet/dry'),
                    'description': self.tr('description of wet/dry')
                }]
            },{
                'value': 'earthquake',
                'name': self.tr('earthquake'),
                'description': self.tr('description of subcategory: earthquake'),
                'units': [{
                    'value': 'MMI',
                    'name': self.tr('MMI'),
                    'description': self.tr('description of MMI'),
                },{
                    'value': '',
                    'name': self.tr('Not Set'),
                    'description': self.tr('description of Not Set'),
                }]
            },{
                'value': 'tephra',
                'name': self.tr('tephra'),
                'description': self.tr('description of subcategory: tephra'),
                'units': [{
                    'value': 'kg/m2',
                    'name': self.tr('kg/m2'),
                    'description': self.tr('description of kg/m<sup>2</sup>')
                },{
                    'value': '',
                    'name': self.tr('Not Set'),
                    'description': self.tr('description of Not Set')
                }]
            },{
                'value': 'volcano',
                'name': self.tr('volcano'),
                'description': self.tr('description of subcategory: volcano')
            },{
                'value': '',
                'name': self.tr('Not Set'),
                'description': self.tr('description of subcategory: empty')
            }]
        }, {
            'value': 'exposure',
            'name': self.tr('exposure'),
            'description': self.tr('An <b>exposure</b> layer represents '
                'people, property or infrastructure that may be affected '
                'in the event of a flood, earthquake, volcano etc.'),
            'subcategory_question': self.tr('What kind of exposure does this '
                'layer represent? The choice you make here will determine '
                'which impact fundtions this exposure layer can be used with. '
                'For example, if you have choose <i>population</i> you will be '
                'able to use this exposure layer with impact functions such as '
                '<i>flood impact on population</i>.'),
            'subcategories': [{
                'value': 'population',
                'name': self.tr('population'),
                'description': self.tr('description of subcategory: pupulation'),
            },{
                'value': 'buildings',
                'name': self.tr('buildings'),
                'description': self.tr('description of subcategory: buildings'),
            },{
                'value': 'roads',
                'name': self.tr('roads'),
                'description': self.tr('description of subcategory: roads')
            }]
        }, {
            'value': 'aggregation',
            'name': self.tr('aggregation'),
            'description': self.tr('An <b>aggregation</b> layer represents '
                'regions you can use to summarize the results by. For '
                'example, we might summarise the affected people after'
                'a flood according to city districts.')
        }]

        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock

        self.layer = layer or self.iface.mapCanvas().currentLayer()

        #set widgets on the first tab
        for i in self.standard_categories:
            item = QListWidgetItem(i['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, i['value'])
            self.lstCategories.addItem(item)
        self.lblDescribeCategory.setText('')

        self.pbnBack.setEnabled(False)
        self.pbnNext.setEnabled(False)

        self.pbnCancel.released.connect(self.reject)

        self.go_to_step(1)



    def selected_category(self):
        """Obtain the category selected by user.

        :returns: Metadata of the selected category
        :rtype: dict or None
        """
        if self.lstCategories.selectedIndexes():
            row = self.lstCategories.selectedIndexes()[0].row()
            return self.standard_categories[row]
        else:
            return None


    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory
        :rtype: dict or None
        """
        if self.lstSubcategories.selectedIndexes():
            row = self.lstSubcategories.selectedIndexes()[0].row()
            return self.selected_category()['subcategories'][row]
        else:
            return None


    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: Metadata of the selected unit
        :rtype: dict or None
        """
        if self.lstUnits.selectedIndexes():
            row = self.lstUnits.selectedIndexes()[0].row()
            return self.selected_subcategory()['units'][row]
        else:
            return None


    # prevents actions being handled twice
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Automatic slot executed when category change. Set description label
           and subcategory widgets according to the selected category
        """
        #
        self.lstFields.clear()

        category = self.selected_category()
        # exit if no selection
        if not category:
            return

        # set description label
        self.lblDescribeCategory.setText(category['description'])

        # set subcategory tab widgets
        self.lstSubcategories.clear()
        self.lstUnits.clear()
        self.lstFields.clear()
        self.lblDescribeSubcategory.setText('')
        if category.has_key('subcategory_question'):
            self.lblSelectSubcategory.setText(category['subcategory_question'])
            for i in category['subcategories']:
                item = QListWidgetItem(i['name'], self.lstSubcategories)
                item.setData(QtCore.Qt.UserRole, i['value'])
                self.lstSubcategories.addItem(item)

        # enable the next button
        self.pbnNext.setEnabled(True)



    def on_lstSubcategories_itemSelectionChanged(self):
        """Automatic slot executed when subcategory change. Set description
          label and unit widgets according to the selected category
        """
        category = self.selected_category()
        subcategory = self.selected_subcategory()

        # exit if no selection
        if not subcategory:
            return

        self.lblDescribeSubcategory.setText(subcategory['description'])

        # set unit tab widgets
        self.lblSelectUnit.setText(self.tr('You have selected <b>%s</b> '
            'for this <b>%s</b> layer type. We need to know what units the '
            'data are in. For example in a raster layer, each cell might '
            'represent depth in meters or depth in feet. If the dataset '
            'is a vector layer, each polygon might represent an inundated '
            'area, while ares with no polygon coverage would be assumed '
            'to be dry.') % (subcategory['name'], category['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        self.lstFields.clear()
        if subcategory.has_key('units'):
            for i in subcategory['units']:
                item = QListWidgetItem(i['name'], self.lstUnits)
                item.setData(QtCore.Qt.UserRole, i['value'])
                self.lstUnits.addItem(item)


        # enable the next button
        self.pbnNext.setEnabled(True)



    def on_lstUnits_itemSelectionChanged(self):
        """Automatic slot executed when unit change. Set description label
           and field widgets according to the selected category
        """
        unit = self.selected_unit()
        # exit if no selection
        if not unit:
            return

        self.lblDescribeUnit.setText(unit['description'])

        # set field tab widgets
        self.lblSelectField.setText(self.tr('You have selected <b>%s</b> '
            'measured in <b>%s</b>, and the selected layer is vector layer. '
            'Please choose the attribute that contains the selected value.')
            % (self.selected_subcategory()['name'], unit['name']))
        self.lstFields.clear()
        if self.layer and not is_raster_layer(self.layer):
            for field in self.layer.dataProvider().fields():
                self.lstFields.addItem(field.name())

        # enable the next button
        self.pbnNext.setEnabled(True)



    def on_lstFields_itemSelectionChanged(self):
        """Automatic slot executed when field change.
           Unlocks the Next button.
        """
        # enable the next button
        self.pbnNext.setEnabled(True)



    def on_leSource_textChanged(self):
        """Automatic slot executed when the source change.
           Unlocks the Next button.
        """
        # enable the next button
        self.pbnNext.setEnabled(bool(self.leSource.text()))



    def on_leTitle_textChanged(self):
        """Automatic slot executed when the title change.
           Unlocks the Next button.
        """
        # enable the next button
        self.pbnNext.setEnabled(bool(self.leTitle.text()))



    def go_to_step(self, step):
        """Set the stacked widget to the given step

        :param step: The step number to be moved to
        :type step: int
        """
        self.stackedWidget.setCurrentIndex(step-1)
        self.lblStep.setText(self.tr("step %d of %d") % (step, 6))
        self.pbnBack.setEnabled(step>1)



    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnNext_released(self):
        """Automatic slot executed when the pbnNext button is released."""
        current_step = self.stackedWidget.currentIndex() + 1
        # determine the new step to be switched
        if current_step == 1:
            category = self.selected_category()
            if category.has_key("subcategories") and category["subcategories"]:
                new_step = current_step + 1
            else:
                new_step = 5
        elif current_step == 2:
            subcategory = self.selected_subcategory()
            if subcategory.has_key("units") and subcategory["units"]:
                new_step = current_step + 1
            else:
                new_step = 5
        elif current_step == 3:
           if self.lstFields.count():
                new_step = current_step + 1
           else:
               new_step = 5
        elif current_step in (4,5) :
            new_step = current_step + 1
        elif current_step == self.stackedWidget.count():
            # step 6
            self.accept()
            return
        else:
            raise Exception("Unexpected number of steps")
            return

        #set Next button label
        if new_step == self.stackedWidget.count():
            self.pbnNext.setText(self.tr('Finish'))
        #disable the Next button unless new data already entered
        self.pbnNext.setEnabled(self.is_ready_to_next_step(new_step))
        self.go_to_step(new_step)



    # prevents actions being handled twice
    @pyqtSignature('')
    def on_pbnBack_released(self):
        """Automatic slot executed when the pbnBack button is released."""
        #new_step = self.stackedWidget.currentIndex()
        current_step = self.stackedWidget.currentIndex() + 1
        # determine the new step to be switched
        if current_step == 5:
            if self.selected_unit() and self.lstFields.selectedIndexes():
                # note the fields list may be obsolete if no unit selected
                new_step = 4
            elif self.selected_unit():
                new_step = 3
            elif self.selected_subcategory():
                new_step = 2
            else:
                new_step = 1
        else:
            new_step = current_step - 1

        #set Next button label
        self.pbnNext.setText(self.tr('Next'))
        self.pbnNext.setEnabled(True)
        self.go_to_step(new_step)



    def is_ready_to_next_step(self, step):
        """Check if widgets are filled an new step can be enabled

        :param step: The present step number
        :type step: int

        :returns: True if new step may be enabled
        :rtype: bool
        """
        if step == 1: return bool(self.selected_category())
        if step == 2: return bool(self.selected_subcategory())
        if step == 3: return bool(self.selected_unit())
        if step == 4: return bool(len(self.lstFields.selectedIndexes())
                                  or not self.lstFields.count())
        if step == 5: return bool(self.leSource.text())
        if step == 6: return bool(self.leTitle.text())



    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        my_keywords = {}
        my_keywords['category'] = self.selected_category()['value']
        if self.selected_subcategory() and self.selected_subcategory()['value']:
            my_keywords['subcategory'] = self.selected_subcategory()['value']
        if self.selected_unit() and self.selected_unit()['value']:
            my_keywords['unit'] = self.selected_unit()['value']
        if self.lstFields.currentItem():
            my_keywords['field'] = self.lstFields.currentItem().text()
        if self.leSource.text():
            my_keywords['source'] = self.leSource.text()
        if self.leTitle.text():
            my_keywords['title'] = self.leTitle.text()
        return my_keywords



    def accept(self):
        """Automatic slot executed when the Finish button is pressed.

        It will write out the keywords for the layer that is active.
        This method is based on the KeywordsDialog class.
        """
        self.keywordIO = KeywordIO()
        my_keywords = self.get_keywords()
        try:
            self.keywordIO.write_keywords(
                layer=self.layer, keywords=my_keywords)
        except InaSAFEError, e:
            myErrorMessage = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, self.tr('InaSAFE'),
                ((self.tr(
                    'An error was encountered when saving the keywords:\n'
                    '%s' % myErrorMessage.to_html()))))
        if self.dock is not None:
            self.dock.get_layers()
        self.done(QtGui.QDialog.Accepted)


