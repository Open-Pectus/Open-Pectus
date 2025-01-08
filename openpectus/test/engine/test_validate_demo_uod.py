import os
import logging
import unittest

from openpectus.engine.main import validate_and_exit


def listloggers():
    rootlogger = logging.getLogger()
    print(rootlogger)
    for h in rootlogger.handlers:
        print('     %s' % h)

    for nm, lgr in logging.Logger.manager.loggerDict.items():
        print('+ [%-20s] %s ' % (nm, lgr))
        if not isinstance(lgr, logging.PlaceHolder):
            for h in lgr.handlers:
                print('     %s' % h)


class TestValidateDemoUOD(unittest.TestCase):
    def test_validate(self):
        logging.getLogger().setLevel(logging.INFO)
        # Remove potential side effects on logging from other tests
        # Source: https://gist.github.com/andreasWallner/c7e677eaade39b49a70b
        listloggers()
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
        with self.assertLogs("openpectus", level=logging.INFO) as log:
            # validate_and_exit calls "exit(0)". Catch this to avoid
            # terminating the unittest.
            try:
                validate_and_exit(uod_file_path)
            except SystemExit:
                pass

        # Look for errors or worse in the logs
        error_encountered = False
        for statement in log.records:
            if statement.levelno >= logging.ERROR:
                error_encountered = True

        # Only print validation output if there is something wrong
        if error_encountered:
            # Set up formatter to print captured logs
            formatter = logging.Formatter("%(levelname)s:" +
                                          "%(name)s:" +
                                          "%(message)s")
            for statement in log.records:
                print(formatter.format(statement))

        # Raise assert error if logging.ERROR or greater encountered
        self.assertFalse(error_encountered,
                         msg="Error encountered during validation.")


if __name__ == "__main__":
    unittest.main()
