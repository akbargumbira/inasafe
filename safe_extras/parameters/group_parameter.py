# coding=utf-8
from safe.common.utilities import OrderedDict
from safe_extras.parameters.generic_parameter import GenericParameter
import uuid

__author__ = 'lucernae'


class GroupParameter(GenericParameter):
    """
    Parameter that is used to group parameters together as
    its child.
    """

    def __init__(self, guid=None):
        super(GroupParameter, self).__init__(guid)
        self._child = OrderedDict()

    @property
    def child(self):
        """Property for the child parameters

        :return: An OrderedDict contains child parameters
        :rtype: OrderedDict
        """
        return self._child

    @child.setter
    def child(self, val):
        """Set the property of child parameters

        :param val: An OrderedDict contains child parameters
        :type: OrderedDict
        """
        self._child = val

    def add_child(self, key, val):
        """Add keys, value (Parameter) to child. or set it if it is exists

        :param key: A string key
        :type key: str
        :param val:
        :type val: GenericParameter
        :return:
        """
        if self.child is None:
            self.child = OrderedDict()
        self.child[key] = val