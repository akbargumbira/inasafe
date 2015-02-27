from new_utilities import is_subset


class Registry(object):
    """A simple registry for keeping track of all impact functions.

    We will use a singleton pattern to ensure that there is only
    one canonical registry. The registry can be used by impact functions
    to register themselves and their GUID's.
    """

    _instance = None
    _impact_functions = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Registry, cls).__new__(
                cls, *args, **kwargs)
            cls._impact_functions = []
        return cls._instance

    @classmethod
    def register(cls, impact_function):
        if impact_function not in cls._impact_functions:
            cls._impact_functions.append(impact_function)

    @classmethod
    def list(cls):
        for impact_function in cls._impact_functions:
            print impact_function.metadata()['name']

    @classmethod
    def get(cls, name):
        """Return an instance of an impact function given its name."""
        for impact_function in cls._impact_functions:
            if impact_function.__name__ == name:
                return impact_function.instance()
        raise Exception('Impact function called %s not found' % name)

    @classmethod
    def filter(cls, hazard_keywords, exposure_keywords):
        """Filter impact function given the hazard and exposure keywords.

        :param hazard_keywords: Dictionary represent hazard keywords
        :type hazard_keywords: dict

        :param exposure_keywords: Dictionary represent exposure keywords
        :type exposure_keywords: dict

        :returns: List of impact functions.
        :rtype: list

        """
        impact_functions = cls._impact_functions
        impact_functions = cls.filter_by_hazard(
            impact_functions, hazard_keywords)
        impact_functions = cls.filter_by_exposure(
            impact_functions, exposure_keywords)

        return impact_functions

    @staticmethod
    def filter_by_hazard(impact_functions, hazard_keywords):
        """Filter impact function by hazard_keywords.

        :param impact_functions: List of impact functions.
        :type impact_functions: list

        :param hazard_keywords: Dictionary represent hazard keywords.
        :type hazard_keywords: dict

        :returns: List of impact functions.
        :rtype: list

        """
        filtered_impact_functions = []
        for impact_function in impact_functions:
            if_hazard_keywords = impact_function.metadata()[
                'categories']['hazard']
            subcategory = if_hazard_keywords['subcategory']
            units = if_hazard_keywords['units']
            layer_constraints = if_hazard_keywords['layer_constraints']

            if not is_subset(hazard_keywords['subcategory'], subcategory):
                continue
            if not is_subset(hazard_keywords['units'], units):
                continue
            if not is_subset(
                    hazard_keywords['layer_constraints'], layer_constraints):
                continue
            filtered_impact_functions.append(impact_function)

        return filtered_impact_functions

    @staticmethod
    def filter_by_exposure(impact_functions, exposure_keywords):
        """Filter impact function by exposure_keywords.

        :param impact_functions: List of impact functions
        :type impact_functions: list

        :param exposure_keywords: Dictionary represent exposure keywords
        :type exposure_keywords: dict

        :returns: List of impact functions.
        :rtype: list

        """
        filtered_impact_functions = []
        for impact_function in impact_functions:
            if_exposure_keywords = impact_function.metadata()[
                'categories']['exposure']
            subcategory = if_exposure_keywords['subcategory']
            units = if_exposure_keywords['units']
            layer_constraints = if_exposure_keywords['layer_constraints']

            if not is_subset(exposure_keywords['subcategory'], subcategory):
                continue
            if not is_subset(exposure_keywords['units'], units):
                continue
            if not is_subset(
                    exposure_keywords['layer_constraints'], layer_constraints):
                continue
            filtered_impact_functions.append(impact_function)

        return filtered_impact_functions
