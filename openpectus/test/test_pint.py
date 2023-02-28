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

        velocity = 7 * ureg.meter / 1 * ureg.second
        self.assertIsInstance(velocity.dimensionality, UnitsContainer)
        self.assertEqual("[length] * [time]", velocity.dimensionality)

        weight = 2 * ureg.kg
        self.assertEqual("kilogram", str(weight.units))
        self.assertEqual("[mass]", weight.dimensionality)

        volume = 3 * ureg.liter  # hmm, no sign of 'volume' anywhere in the api
        self.assertEqual("liter", str(volume.units))
        self.assertEqual("[length] * [length] * [length]", volume.dimensionality)

    def test_conversion(self):
        distance_km = 3.2 * ureg.kilometers
        distance_m = distance_km.to(ureg.meter)
        self.assertEqual(3200, distance_m.magnitude)

    def test_conversion_invalid(self):
        distance_km = 3.2 * ureg.kilometers
        with self.assertRaises(DimensionalityError) as err:
            _ = distance_km.to(ureg.second)
        self.assertEqual("Cannot convert from 'kilometer' ([length]) to 'second' ([time])", str(err.exception))

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


if __name__ == "__main__":
    unittest.main()
