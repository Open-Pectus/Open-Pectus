import unittest
import logging

from openpectus.lang.exec.units import (
    convert_value_to_unit,
    is_supported_unit,
    get_supported_units,
    get_compatible_unit_names,
    compare_values,
    QUANTITY_UNIT_MAP,
    add_unit,
 )

logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logging.getLogger("openpectus.lang.exec.units").setLevel(logging.INFO)


class TestUnits(unittest.TestCase):
    def test_is_supported_unit(self):
        def test_unit(unit: str | None, expect_supported: bool, quantity_name: str = ""):
            if unit is not None:
                test_name = unit if quantity_name == "" else quantity_name + ": " + unit
                with self.subTest(test_name):
                    self.assertEqual(is_supported_unit(unit), expect_supported)

        test_unit("L", True)
        test_unit("%", True)
        test_unit("degC", True)
        test_unit("degF", True)
        test_unit("K", True)
        test_unit("CV", True)
        test_unit("bar", True)
        test_unit("kg/h", True)
        test_unit("AU", True)  # absorbance unit, not 'au'
        test_unit("mS/cm", True)  # milisiemens/cm, electrical conductance
        test_unit("Hz", True)
        test_unit("kHz", True)
        test_unit("m2", True)
        test_unit("kg/L", True)
        test_unit("wt%", True)
        test_unit("LMH", True)
        test_unit("L/m2/h", True)
        test_unit("L/m2/h/bar", True)
        test_unit("°C", True)

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
        with self.subTest(value_a + sua + " " + operator + " " + value_b + sub + ", " + s):

            result : bool | None = None
            try:
                result = compare_values(operator, value_a, unit_a, value_b, unit_b)
            except ValueError as ve:
                if expected_value_error_msg is None:
                    raise AssertionError(f"compare_value raised ValueError '{ve}' but no error was expected")
                elif str(ve) != expected_value_error_msg:
                    raise AssertionError(f"compare_value raised a ValueError with msg '{str(ve)}' but expected msg " +
                                         f"{expected_value_error_msg}")
            except Exception as ex:
                raise AssertionError("compare_value raised unextected exception: " + str(ex))

            if result is None and expected_result is not None:
                raise AssertionError(f"Expected result={expected_result} but got no result")
            elif result is not None and expected_result is not None:
                if result != expected_result:
                    raise AssertionError(f"Expected result={expected_result} but got result {result}")


    def test_compare_values_numeric_equality(self):
        self.comp("=", "5", None, "5", None, True)
        self.comp("==", "5", None, "5", None, True)
        self.comp("!=", "5", None, "5", None, False)

        self.comp("=", "5", None, "7", None, False)
        self.comp("==", "5", None, "7", None, False)
        self.comp("!=", "5", None, "7", None, True)

    def test_compare_values_numeric_inequality(self):
        self.comp("<", "5", None, "5", None, False)
        self.comp("<=", "5", None, "5", None, True)
        self.comp(">", "5", None, "5", None, False)

        self.comp("<", "5", None, "7", None, True)
        self.comp("<=", "5", None, "7", None, True)
        self.comp(">", "5", None, "7", None, False)

    def test_compare_values_string_equality(self):
        self.comp("=", "foo", None, "foo", None, True)
        self.comp("==", "foo", None, "foo", None, True)
        self.comp("!=", "foo", None, "foo", None, False)

        self.comp("=", "foo", None, "bar", None, False)
        self.comp("==", "foo", None, "bar", None, False)
        self.comp("!=", "foo", None, "bar", None, True)

    def test_compare_values_string_inequality(self):
        self.comp("<", "foo", None, "foo", None, None, "Cannot compare values, first value is missing or not numeric")
        self.comp("<=", "foo", None, "foo", None, None, "Cannot compare values, first value is missing or not numeric")
        self.comp(">", "foo", None, "foo", None, None, "Cannot compare values, first value is missing or not numeric")

        self.comp("<", "5", None, "foo", None, None, "Cannot compare values, second value is missing or not numeric")
        self.comp("<", "", None, "foo", None, None, "Cannot compare values, first value is missing or not numeric")
        self.comp("<", "5", None, "", None, None, "Cannot compare values, second value is missing or not numeric")

    def test_compare_values_invalid_operator(self):
        self.comp("><", "5", None, "7", None, None, "Invalid operator: '><'")

    def test_compare_values_numeric_equality_w_unit(self):
        self.comp("=", "5", "s", "5", "s", True)
        self.comp("=", "5", "s", "5", "s", True)
        self.comp("=", "5", "s", "5.0", "s", True)
        self.comp("==", "5", "s", "5", "s", True)
        self.comp("!=", "5", "s", "5", "s", False)

        self.comp("=", "5", "s", "7", "s", False)
        self.comp("==", "5.0", "s", "7", "s", False)
        self.comp("!=", "5", "s", "7", "s", True)

        self.comp("=", "5", "kg/h", "7", "kg/h", False)
        self.comp("!=", "5", "kg/h", "5", "g/s", True)

        self.comp("=", "60", "L/h", "1", "L/min", True)
        self.comp(">", "61", "L/h", "1", "L/min", True)
        self.comp("<", "59", "L/h", "1", "L/min", True)


    def test_compare_values_numeric_equality_w_unit_error(self):
        self.comp("=", "5", "s", "5", None, None, "Cannot compare values with incompatible units 's' and 'None'")
        self.comp("=", "5", None, "5", "s", None, "Cannot compare values with incompatible units 'None' and 's'")

    def test_compare_values_numeric_equality_w_unit_incompatible(self):
        self.comp("=", "5", "s", "5", "L", None, "Cannot compare values with incompatible units 's' and 'L'")

    def test_compare_values_numeric_inequality_w_unit(self):
        self.comp("<", "5", "s", "5", "s", False)
        self.comp("<", "5", "s", "5", "s", False)

        self.comp("<=", "5", "s", "5", "s", True)
        self.comp(">", "5", "s", "5", "s", False)

        self.comp("<", "5", "s", "7", "s", True)
        self.comp("<=", "5", "s", "7", "s", True)
        self.comp(">", "5", "s", "7", "s", False)

        self.comp(">", "5", "degC", "7", "degC", False)
        self.comp("<", "5", "degC", "7", "degC", True)

    def test_compare_values_compatible_units(self):
        self.comp("=", "60", "s", "1", "min", True)
        self.comp("==", "60", "s", "1", "min", True)
        self.comp("!=", "60", "s", "1", "min", False)

        self.comp("<", "50", "s", "1", "min", True)
        self.comp("<=", "50", "s", "1", "min", True)
        self.comp("<=", "60", "s", "1", "min", True)
        self.comp(">", "70", "s", "1", "min", True)

        self.comp("=", "1", "m2", "100", "dm2", True)
        self.comp("=", "1", "m2", "10000", "cm2", True)
        self.comp("=", "1", "dm2", "100", "cm2", True)

        self.comp("=", "0", "degC", "32", "degF", True)
        self.comp(">", "1", "degC", "32", "degF", True)
        self.comp(">=", "1", "degC", "32", "degF", True)
        self.comp(">", "0", "degC", "33", "degF", False)
        self.comp(">=", "0", "degC", "33", "degF", False)

        self.comp("=", "0", "degC", "273.15", "K", True)
        self.comp(">", "1", "degC", "274", "K", True)
        self.comp(">=", "1", "°C", "274", "K", True)
        self.comp(">", "0", "degC", "274", "K", False)
        self.comp(">=", "0", "degC", "274", "K", False)
        self.comp("=", "13", "degC", "13", "°C", True)

        self.comp("<=", "5", "kg/h", "5000", "g/h", True)
        self.comp(">=", "5", "kg/h", "5000", "g/h", True)
        self.comp("<", "5", "kg/h", "5001", "g/h", True)
        self.comp(">", "5", "kg/h", "4999", "g/h", True)

        self.comp("=", "9", "%", "9", "vol%", True)
        self.comp("=", "9", "%", "9", "wt%", True)
        self.comp("=", "1000", "mAU", "1", "AU", True)
        self.comp("=", "1000", "milliAU", "1", "AU", True)

    def test_compare_multidimensional_pint_units(self):
        # pint treats 'L/d' as 'liter / day' which must be mapped back
        self.comp("=", "48", "L/d", "2", "L/h", True)
        self.comp("<", "48", "L/d", "2.1", "L/h", True)
        self.comp(">", "48.1", "L/d", "2", "L/h", True)
        self.comp("=", "1.4", "LMH", "1.4", "L/m2/h", True)
        self.comp("=", "1.42", "LMH", "1.42", "L/h/m2", True)
        self.comp("=", "1", "kg/L", "1000", "g/L", True)

    def test_troublesome_pint_units(self):
        # pint prefers pascal over Pa so we have defined both. As long as pint
        # is used for comparison via Quantity, it still works.
        self.comp("=", "5", "Pa", "5", "pascal", True)
        self.comp("<", "5", "Pa", "5.1", "pascal", True)
        self.comp(">", "5.1", "Pa", "5", "pascal", True)

    def test_custom_units(self):
        def test(unit: str):
            with self.subTest(unit):
                self.assertTrue(is_supported_unit(unit))

        test("CV")

    def test_compare_custom_units(self):
        self.comp("<", "5", "%", "5.0", "%", False)
        self.comp("==", "5", "%", "5.0", "%", True)

        # TODO: comparison of % to no unit? would seem to be valid 10% == 0.1?

        self.comp("<", "5", "CV", "5.0", "CV", False)
        self.comp("==", "5", "CV", "5.0", "CV", True)

    def test_disallowed_comparison(self):
        with self.assertRaises(ValueError):
            compare_values("=", "9", "vol%", "9", "wt%")
        with self.assertRaises(ValueError):
            compare_values("=", "9", "mol%", "9", "wt%")
        with self.assertRaises(ValueError):
            compare_values("=", "9", "mol%", "9", "vol%")

    def test_convert_value_to_unit(self):
        self.assertAlmostEqual(0.05, convert_value_to_unit(5, "cm", "m"))
        self.assertAlmostEqual(50, convert_value_to_unit(5, "m", "dm"))
        self.assertAlmostEqual(1.0, convert_value_to_unit(60, "L/h", "L/min"))

    def test_convert_value_to_unit_raises_on_incompatible_units(self):
        with self.assertRaises(ValueError):
            convert_value_to_unit(5, "m", "L")

    def test_add_unit(self):
        self.assertFalse(is_supported_unit("DV"))
        add_unit("DV", quantity="diavolume")
        self.assertTrue(is_supported_unit("DV"))
        with self.assertLogs(logging.getLogger(), level=logging.WARNING):
            add_unit("DV", quantity="diavolume")

        add_unit("kg/m2/h", quantity_relation={"mass_flux": "[mass] / [length] ** 2 / [time]"})

        add_unit("mDV", quantity="diavolume")
        self.comp("=", "1000", "mDV", "1", "DV", True)
