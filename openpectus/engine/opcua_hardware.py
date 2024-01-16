import logging
from typing import Any, Dict, Iterable

from openpectus.engine.hardware import (
    HardwareLayerBase,
    Register,
    RegisterDirection,
    HardwareLayerException
)

logger = logging.getLogger(__name__)


class OPCUA_Hardware(HardwareLayerBase):
    """ Represents OPCUA hardware layer. """
    def __init__(self) -> None:
        self.registers: Dict[str, Register] = {}

    def read(self, r: Register) -> Any:        
        return 87

    def read_batch(self, registers: list[Register]) -> list[Any]:
        """ Read batch of register values. Override to provide efficient implementation """
        values = []
        for r in registers:
            if RegisterDirection.Read in r.direction:
                values.append(self.read(r))
        return values

    def write(self, value: Any, r: Register):
        if RegisterDirection.Write not in r.direction:
            pass

        pass

    def write_batch(self, values: Iterable[Any], registers: Iterable[Register]):
        """ Write batch of register values. Override to provide efficient implementation """
        for v, r in zip(values, registers):
            if RegisterDirection.Write in r.direction:
                self.write(v, r)

    def connect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        logger.info("Connecting to OPCUA...")
        pass

    def disconnect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        logger.info("Disconnecting from OPCUA...")
        pass
