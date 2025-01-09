import os
import subprocess
import unittest


class TestValidateDemoUOD(unittest.TestCase):
    def test_validate(self):
        # Construct path to file relative to test_validate_demo_uod.py
        uod_file_path = os.path.join(
            os.path.dirname(  # openpectus
                os.path.dirname(  # openpectus/test
                    os.path.dirname(__file__)  # openpectus/test/engine
                )
            ),
            'engine',  # openpectus/engine
            'configuration',  # openpectus/engine/configuration
            'demo_uod.py',  # openpectus/engine/configuration/demo_uod.py
        )

        # Run validation in subprocess to avoid side effects from other
        # unittests messing with the logging module.
        process = subprocess.run(
            ["pectus-engine", "-v", "-uod", uod_file_path],
            capture_output=True,
            encoding="utf-8"
        )

        # Look for errors or worse in the logs
        if "ERROR:openpectus" in process.stderr:
            print(process.stderr)
            self.assertTrue(
                False,
                msg="Error encountered during validation of 'demo_uod.py'."
            )


if __name__ == "__main__":
    unittest.main()
