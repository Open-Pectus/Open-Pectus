# adapted from https://stackoverflow.com/a/68843198
import os
from typing import Tuple

from starlette.staticfiles import StaticFiles


class SinglePageApplication(StaticFiles):
    """Acts similar to the bripkens/connect-history-api-fallback
    NPM package."""

    def __init__(self, directory: str, index='index.html') -> None:
        self.index = index

        # set html=True to resolve the index even when no
        # the base path is passed in
        super().__init__(directory=directory, packages=None, html=True, check_dir=True)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(directory="{self.directory}", index="{self.index}")'

    def lookup_path(self, path: str) -> Tuple[str, os.stat_result]:
        """Returns the index file when no match is found.

        Args:
            path (str): Resource path.

        Returns:
            [tuple[str, os.stat_result]]: Always returns a full path and stat result.
        """
        full_path, stat_result = super().lookup_path(path)

        # if a file cannot be found
        if stat_result is None:
            return super().lookup_path(self.index)

        return full_path, stat_result
