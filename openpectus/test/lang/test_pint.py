import unittest

import pint
from pint import UndefinedUnitError, UnitRegistry, Quantity, Unit, DimensionalityError
from pint.util import UnitsContainer

ureg = UnitRegistry()
Q_ = Quantity
U_ = Unit


class PintTest(unittest.TestCase):

    def test_basics_quantity(self):
        distance = 24.0 * ureg.meter
        assert isinstance(distance, Quantity)
        self.assertIsInstance(distance, Quantity)
        self.assertEqual("24.0 meter", str(distance))

        self.assertEqual(24.0, distance.magnitude)

        self.assertIsInstance(distance.units, Unit)
        self.assertEqual("meter", str(distance.units))

        self.assertIsInstance(distance.dimensionality, UnitsContainer)
        self.assertEqual("[length]", distance.dimensionality)
        self.assertFalse(distance.dimensionless)

        velocity = 7 * ureg.meter / 1 * ureg.second
        self.assertIsInstance(velocity.dimensionality, UnitsContainer)
        self.assertEqual("[length] * [time]", velocity.dimensionality)

        weight = 2 * ureg.kg
        assert isinstance(weight, Quantity)
        self.assertEqual("kilogram", str(weight.units))
        self.assertEqual("[mass]", weight.dimensionality)

        volume = 3 * ureg.liter  # hmm, no sign of 'volume' anywhere in the api
        assert isinstance(volume, Quantity)
        self.assertEqual("liter", str(volume.units))
        self.assertEqual("[length] * [length] * [length]", volume.dimensionality)

        time = Q_("1 min")  # Note: need 'min' as 'm' is meter
        self.assertEqual("minute", str(time.units))
        self.assertEqual("[time]", time.dimensionality)

        length = Q_("1 m")
        self.assertEqual("meter", str(length.units))
        self.assertEqual("[length]", length.dimensionality)

    def test_basics_unit(self):
        u = U_("s")
        self.assertFalse(u.dimensionless)
        self.assertEqual("second", str(u))
        self.assertEqual("[time]", str(u.dimensionality))
        # print("{!r}".format(u))

        q = 5 * u  # noqa: F841
        # print("{!r}".format(q))

    def test_dimensionless(self):
        count = Q_(3)
        self.assertTrue(count.dimensionless)
        self.assertEqual("<Quantity(3, 'dimensionless')>", "{!r}".format(count))

        count = Q_(3, None)
        self.assertTrue(count.dimensionless)
        self.assertEqual("<Quantity(3, 'dimensionless')>", "{!r}".format(count))

        u1 = U_("")  # must use empty string, not None or no argument
        self.assertTrue(u1.dimensionless)
        self.assertEqual("<Unit('dimensionless')>", u1.__repr__())

    def test_dimensionless_percentage(self):
        count = Q_(3, "%")
        self.assertTrue(count.dimensionless)
        self.assertTrue(count.unitless)
        self.assertEqual("<Quantity(3, 'percent')>", "{!r}".format(count))
        self.assertEqual(count.units.__repr__(), "<Unit('percent')>")

    def test_pressure(self):
        val = Q_(1, "bar")
        exp_dimensionality = "[mass] / [length] / [time] ** 2"
        self.assertEqual(exp_dimensionality, str(val.dimensionality))

        compatibles = ureg.get_compatible_units(exp_dimensionality)  # type: ignore
        self.assertIn('bar', [str(c) for c in compatibles])

        # Note: 'Pa' is not in compatibles but 'pascal' is
        self.assertNotIn('Pa', [str(c) for c in compatibles])
        self.assertIn('pascal', [str(c) for c in compatibles])

        # but Pa is a valid unit
        val2 = Q_(1, "Pa")
        self.assertEqual(exp_dimensionality, str(val2.dimensionality))

    def test_flow(self):
        val = Q_(1, "l/h")
        exp_dimensionality = "[length] ** 3 / [time]"
        self.assertEqual(exp_dimensionality, str(val.dimensionality))

    def test_mass_flow_rate(self):
        val = Q_(1, "kg/h")
        exp_dimensionality = "[mass] / [time]"
        self.assertEqual(exp_dimensionality, str(val.dimensionality))

    def test_frequency(self):
        val = Q_(1, "Hz")
        exp_dimensionality = "1 / [time]"
        self.assertEqual(exp_dimensionality, str(val.dimensionality))

    def test_absorbance(self):
        val = Q_(1, "mS/cm")
        exp_dimensionality = "[current] ** 2 * [time] ** 3 / [mass] / [length] ** 3"
        self.assertEqual(exp_dimensionality, str(val.dimensionality))

    def test_area(self):
        val_m2 = Q_(1, "m**2")
        unit_cm2 = Unit("cm**2")
        val_cm2 = val_m2.to(unit_cm2)
        self.assertAlmostEqual(10000, val_cm2.magnitude, delta=0.001)
        unit_dm2 = Unit("dm**2")
        val_dm2 = val_m2.to(unit_dm2)
        self.assertAlmostEqual(100, val_dm2.magnitude, delta=0.001)

    def test_formatting(self):
        weight = 2 * ureg.kg
        s = 'The magnitude is {0.magnitude} with units {0.units}'.format(weight)
        self.assertEqual("The magnitude is 2 with units kilogram", s)
        repr = 'The representation is {!r}'.format(weight)
        self.assertEqual("The representation is <Quantity(2, 'kilogram')>", repr)
        # or just use __repr__()
        self.assertEqual("<Quantity(2, 'kilogram')>", weight.__repr__())

    def test_conversion(self):
        distance_km = 3.2 * ureg.kilometers
        assert isinstance(distance_km, Quantity)
        distance_m = distance_km.to(ureg.meter)
        self.assertEqual(3200, distance_m.magnitude)

    def test_conversion_invalid(self):
        distance_km = 3.2 * ureg.kilometers
        assert isinstance(distance_km, Quantity)
        with self.assertRaises(DimensionalityError) as err:
            _ = distance_km.to(ureg.second)
        self.assertEqual("Cannot convert from 'kilometer' ([length]) to 'second' ([time])", str(err.exception))

    def test_compatibility_quantity(self):
        dist = Q_("310m")
        weight = Q_("3kg")
        temp = Q_(3, ureg.degC)
        time = Q_("5 sec")

        # NOTE: don't use ureg.is_compatible_with:
        # self.assertFalse(ureg.is_compatible_with(dist1, weight))  # this fails
        # Instead, use the Quantity.is_compatible_with() method:
        self.assertFalse(dist.is_compatible_with(weight))
        self.assertFalse(dist.is_compatible_with(temp))
        self.assertFalse(time.is_compatible_with(temp))

        # or use this for testing compability then
        with self.assertRaises(DimensionalityError):
            _ = dist.to(ureg.second)
        with self.assertRaises(DimensionalityError):
            _ = dist.to(ureg.mass)

        # or maybe just check dimensionality with the check() method
        self.assertTrue(dist.check('[length]'))
        self.assertTrue(Q_("3kg").check('[mass]'))

    def test_compatibility_unit(self):
        second = pint.Unit("sec")  # the default constructor
        hour = U_("h")  # or the short hand
        kg = U_("kg")

        self.assertTrue(second.is_compatible_with(hour))
        self.assertFalse(second.is_compatible_with(kg))

    @unittest.skip("Not sure we need this. Requres the Babel lib")
    def test_locale(self):
        # print("locale:", ureg.fmt_locale)  # is None by default
        # set_fmt_locale: None: (do not translate), 'sys' (detect the system locale) or a locale id string.
        ureg.set_fmt_locale('sys')
        distance = 24.0 * ureg.meter
        self.assertEqual("24.0 meter", str(distance))

    def test_dimensions(self):
        # temperature = 9.5 * ureg.degC  # fails, because degC is not a multiplicative unit,
        # see https://pint.readthedocs.io/en/0.10.1/nonmult.html

        # this works. but beware of deltas. temperature calculus is tricky
        # alternatively, use ureg = UnitRegistry(autoconvert_offset_to_baseunit = True)
        # to perform automatic conversions
        temperature = Q_(25.4, ureg.degC)
        self.assertEqual("25.4 degree_Celsius", str(temperature))

    def test_higher_dimensionality(self):
        flow = Q_("10 L/h")
        self.assertIsInstance(flow, Quantity)
        self.assertEqual("<Quantity(10.0, 'liter / hour')>", "{!r}".format(flow))
        self.assertEqual("liter / hour", str(flow.units))

        flow = Q_("10 L/d")
        self.assertIsInstance(flow, Quantity)
        self.assertEqual("<Quantity(10.0, 'liter / day')>", "{!r}".format(flow))

        flow = Q_("10 L/min")
        self.assertIsInstance(flow, Quantity)
        self.assertEqual("<Quantity(10.0, 'liter / minute')>", "{!r}".format(flow))

    def test_string_parsing(self):
        distance = Q_("24cm")
        self.assertIsInstance(distance, Quantity)
        self.assertEqual("24 centimeter", str(distance))

        distance = 2.54 * ureg('nm')
        self.assertIsInstance(distance, Quantity)
        self.assertEqual("2.54 nanometer", str(distance))

        volume = Q_("3 L")
        self.assertEqual("<Quantity(3, 'liter')>", "{!r}".format(volume))

        count = Q_(7)
        self.assertEqual("<Quantity(7, 'dimensionless')>", "{!r}".format(count))

    def test_comparison(self):
        a = Q_("10 cm")
        b = Q_("20 cm")
        c = Q_("0.2 m")
        self.assertTrue(a < b)
        self.assertTrue(a < c)
        self.assertEqual(b, c)

    def test_test_for_unknown_unit(self):
        with self.assertRaises(UndefinedUnitError):
            _ = Q_("7.0 CV")

    @unittest.skip(reason="Not a test. Merely documenttion of ureg.get_compatible_units")
    def test_list_compatible_units(self):
        a = Q_("10 cm")
        result = ureg.get_compatible_units(a.units)  # type: ignore
        print(result)
        # Returns lots of useless values like parsec, nautical mile, angstrom_star, light_year and such
        # and a few useful ones, like meter. Need to rool our own or customize pint defaults
        # see https://github.com/hgrecco/pint/blob/master/pint/default_en.txt

    # def test_customizing_pint_registry(self):
    #     ureg = UnitRegistry(cache_folder=":auto:")
    #     print("ureg.cache_folder", ureg.cache_folder)


if __name__ == "__main__":
    unittest.main()
