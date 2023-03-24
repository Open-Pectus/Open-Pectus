import unittest
from pint import UnitRegistry, Quantity, Unit, DimensionalityError
from pint.util import UnitsContainer


ureg = UnitRegistry()
Q_ = Quantity


class PintTest(unittest.TestCase):

    def test_basics(self):
        distance = 24.0 * ureg.meter
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
        self.assertEqual("kilogram", str(weight.units))
        self.assertEqual("[mass]", weight.dimensionality)

        volume = 3 * ureg.liter  # hmm, no sign of 'volume' anywhere in the api
        self.assertEqual("liter", str(volume.units))
        self.assertEqual("[length] * [length] * [length]", volume.dimensionality)

    def test_dimensionless(self):
        count = Q_(3)
        self.assertTrue(count.dimensionless)
        self.assertEqual("<Quantity(3, 'dimensionless')>", "{!r}".format(count))

        count = Q_(3, None)
        self.assertTrue(count.dimensionless)
        self.assertEqual("<Quantity(3, 'dimensionless')>", "{!r}".format(count))

    def test_formatting(self):
        weight = 2 * ureg.kg
        s = 'The magnitude is {0.magnitude} with units {0.units}'.format(weight)
        self.assertEqual("The magnitude is 2 with units kilogram", s)
        repr = 'The representation is {!r}'.format(weight)
        self.assertEqual("The representation is <Quantity(2, 'kilogram')>", repr)

    def test_conversion(self):
        distance_km = 3.2 * ureg.kilometers
        distance_m = distance_km.to(ureg.meter)
        self.assertEqual(3200, distance_m.magnitude)

    def test_conversion_invalid(self):
        distance_km = 3.2 * ureg.kilometers
        with self.assertRaises(DimensionalityError) as err:
            _ = distance_km.to(ureg.second)
        self.assertEqual("Cannot convert from 'kilometer' ([length]) to 'second' ([time])", str(err.exception))

    def test_compatibility(self):
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

    @unittest.skip("Not sure we need this. Requres the Babel lib")
    def test_locale(self):
        print("locale:", ureg.fmt_locale)  # is None by default
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



if __name__ == "__main__":
    unittest.main()
