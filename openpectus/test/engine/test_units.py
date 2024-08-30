import unittest

from openpectus.lang.exec.units import (
    is_supported_unit,
    get_supported_units,
    get_compatible_unit_names,
    compare_values,
    QUANTITY_UNIT_MAP,
 )


class TestUnits(unittest.TestCase):
    def test_is_supported_unit(self):
        def test_unit(unit: str | None, expect_supported, quantity_name: str = ""):
            if unit is not None:
                test_name = unit if quantity_name == "" else quantity_name + ': ' + unit
                with self.subTest(test_name):                
                    self.assertEqual(is_supported_unit(unit), expect_supported)

        test_unit( 'L', True)
        test_unit("%", True)
        for quantity_name in QUANTITY_UNIT_MAP.keys():
            for unit in QUANTITY_UNIT_MAP[quantity_name]:
                test_unit(unit, True, quantity_name)                

        test_unit("", False)
        test_unit("X", False)
        test_unit("ML", False)

    def test_get_compatible_unit_names(self):
        def test_unit(unit: str):
            with self.subTest(unit):
                compatibles = get_compatible_unit_names(unit)
                self.assertIsNotNone(compatibles)
        for unit in get_supported_units():
            if unit is not None:
                test_unit(unit)

    def comp(
            self,
            operator: str,
            value_a: str, unit_a: str | None,
            value_b: str, unit_b: str | None,
            expected_result: bool | None = None,
            expected_value_error_msg: str | None = None):
        s = str(expected_result) if expected_result is not None else expected_value_error_msg or "error"
        sua, sub = unit_a or "", unit_b or ""
        with self.subTest(value_a + sua + ' ' + operator + ' ' + value_b + sub + ', ' + s):

            result : bool | None = None
            try:
                result = compare_values(operator, value_a, unit_a, value_b, unit_b)
            except ValueError as ve:
                if expected_value_error_msg is None:
                    raise AssertionError(f"compare_value raised ValueError '{ve}' but no error was expected")
                elif str(ve) != expected_value_error_msg:
                    raise AssertionError(f"compare_value raised a ValueError with msg '{str(ve)}' but expected msg {expected_value_error_msg}")
            except Exception as ex:
                raise AssertionError("compare_value raised unextected exception: " + str(ex))

            if result is None and expected_result is not None:
                raise AssertionError(f"Expected result={expected_result} but got no result")

    def test_compare_values_numeric_equality(self):
        self.comp('=', '5', None, '5', None, True)
        self.comp('==', '5', None, '5', None, True)
        self.comp('!=', '5', None, '5', None, False)

        self.comp('=', '5', None, '7', None, False)
        self.comp('==', '5', None, '7', None, False)
        self.comp('!=', '5', None, '7', None, True)

    def test_compare_values_numeric_inequality(self):
        self.comp('<', '5', None, '5', None, False)
        self.comp('<=', '5', None, '5', None, True)
        self.comp('>', '5', None, '5', None, False)

        self.comp('<', '5', None, '7', None, True)
        self.comp('<=', '5', None, '7', None, True)
        self.comp('>', '5', None, '7', None, False)

    def test_compare_values_string_equality(self):
        self.comp('=', 'foo', None, 'foo', None, True)
        self.comp('==', 'foo', None, 'foo', None, True)
        self.comp('!=', 'foo', None, 'foo', None, False)

        self.comp('=', 'foo', None, 'bar', None, False)
        self.comp('==', 'foo', None, 'bar', None, False)
        self.comp('!=', 'foo', None, 'bar', None, True)

    def test_compare_values_string_inequality(self):        
        self.comp('<', 'foo', None, 'foo', None, None, "Cannot compare values, first value is missing or not numeric")
        self.comp('<=', 'foo', None, 'foo', None, None, "Cannot compare values, first value is missing or not numeric")
        self.comp('>', 'foo', None, 'foo', None, None, "Cannot compare values, first value is missing or not numeric")

        self.comp('<', '5', None, 'foo', None, None, "Cannot compare values, second value is missing or not numeric")
        self.comp('<', '', None, 'foo', None, None, "Cannot compare values, first value is missing or not numeric")
        self.comp('<', '5', None, '', None, None, "Cannot compare values, second value is missing or not numeric")

    def test_compare_values_invalid_operator(self):
        self.comp('><', '5', None, '7', None, None, "Invalid operator: '><'")

    def test_compare_values_numeric_equality_w_unit(self):
        self.comp('=', '5', 's', '5', 's', True)
        self.comp('=', '5', 's', '5', 's', True)
        self.comp('=', '5', 's', '5.0', 's', True)
        self.comp('==', '5', 's', '5', 's', True)
        self.comp('!=', '5', 's', '5', 's', False)

        self.comp('=', '5', 's', '7', 's', False)
        self.comp('==', '5.0', 's', '7', 's', False)
        self.comp('!=', '5', 's', '7', 's', True)

    def test_compare_values_numeric_equality_w_unit_error(self):
        self.comp('=', '5', 's', '5', None, None, "Cannot compare values with incompatible units 's' and 'None'")
        self.comp('=', '5', None, '5', 's', None, "Cannot compare values with incompatible units 'None' and 's'")
        #self.comp('=', '5', 's', '5', 'min', None, "Cannot compare values with units 's' and 'None'")

    def test_compare_values_numeric_equality_w_unit_incompatible(self):
        self.comp('=', '5', 's', '5', 'L', None, "Cannot compare values with incompatible units 's' and 'L'")

    def test_compare_values_numeric_inequality_w_unit(self):
        self.comp('<', '5', 's', '5', 's', False)
        self.comp('<', '5', 's', '5', 's', False)

        self.comp('<=', '5', 's', '5', 's', True)
        self.comp('>', '5', 's', '5', 's', False)

        self.comp('<', '5', 's', '7', 's', True)
        self.comp('<=', '5', 's', '7', 's', True)
        self.comp('>', '5', 's', '7', 's', False)

    def test_compare_values_compatible_units(self):
        self.comp('=', '60', 's', '1', 'min', True)
        self.comp('==', '60', 's', '1', 'min', True)
        self.comp('!=', '60', 's', '1', 'min', False)

        self.comp('<', '50', 's', '1', 'min', True)
        self.comp('<=', '50', 's', '1', 'min', True)
        self.comp('<=', '60', 's', '1', 'min', True)
        self.comp('>', '70', 's', '1', 'min', True)

    def test_complex_pint_units(self):
        # pint treats 'L/d' as 'liter / day' which must be mapped back
        self.comp('=', '48', 'L/d', "2", "L/h", True)
