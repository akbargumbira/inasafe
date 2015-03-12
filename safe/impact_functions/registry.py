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
        """Return an instance of an impact function given its name.

        :param name: the name of IF class
        :type name: str

        :return: impact function instance
        :rtype: safe.impact_functions.base.ImpactFunction.instance()
        """
        return cls.get_class(name).instance()

    @classmethod
    def get_class(cls, name):
        """Return an instance of an impact function given its name.

        :param name: the name of IF class
        :type name: str

        :return: impact function class
        :rtype: safe.impact_functions.base.ImpactFunction
        """
        for impact_function in cls._impact_functions:
            if impact_function.__name__ == name:
                return impact_function
        raise Exception('Impact function called %s not found' % name)

    @classmethod
    def filter_by_keyword_string(cls, hazard_keywords, exposure_keywords):
        if hazard_keywords is None and exposure_keywords is None:
            return cls._impact_functions

        impact_functions = cls._impact_functions
        categories = ['hazard', 'exposure']
        keywords = {'hazard': hazard_keywords, 'exposure': exposure_keywords}
        filtered = []
        for category in categories:
            for f in impact_functions:
                f_category = f.metadata()['categories'][category]
                subcategory = f_category[
                    'subcategory']
                subcategory = cls.project_list(
                    cls.convert_to_list(subcategory), 'id')
                units = f_category['units']
                units = cls.project_list(cls.convert_to_list(units), 'id')
                layer_constraints = cls.convert_to_list(f_category[
                    'layer_constraints'])
                layer_types = cls.project_list(layer_constraints, 'layer_type')
                data_types = cls.project_list(layer_constraints, 'data_type')

                keyword = keywords[category]
                if keyword.get('subcategory') not in subcategory:
                    continue
                if (keyword.get('units') is not None and
                        keyword.get('units') not in units):
                    continue
                if keyword.get('layertype') not in layer_types:
                    continue
                if keyword.get('data_type') not in data_types:
                    continue

                if f not in filtered:
                    filtered.append(f)

        return filtered

    @classmethod
    def convert_to_list(cls, var):
        return var if isinstance(var, list) else [var]

    @classmethod
    def project_list(cls, the_list, field):
        return [s[field] for s in the_list]

    @classmethod
    def filter(cls, hazard_keywords=None, exposure_keywords=None):
        """Filter impact function given the hazard and exposure keywords.

        :param hazard_keywords: Dictionary represent hazard keywords
        :type hazard_keywords: dict

        :param exposure_keywords: Dictionary represent exposure keywords
        :type exposure_keywords: dict

        :returns: List of impact functions.
        :rtype: list

        """
        if hazard_keywords is None and exposure_keywords is None:
            return cls._impact_functions

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
