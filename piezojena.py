import serial

from multiprocessing import Lock
from typing import Callable

from piezo_jena_controllers import PiezoJenaControllers, ControlerName


class PiezoJena():
    """
    Simple basic driver for known Piezo Jena controllers containing basic function only

    currently implemented:
        self.move: moves to position in um
        self.pos: returns the position in um
        self.give_control: unlocks the control knob function if available
        self.take_control: locks the control knob function and takes back control if available
    """
    def __init__(self, COMport : str | int,
                 controler : ControlerName,
                 timeout_s : float | None = 10,
                 write_timeout_s : float | None = 10,
                 inter_byte_timeout_s : float | None = 10,
                 threadsafe : bool = True,
                 votage_mode : bool = False,
                 message : Callable[[str], any] | None = None) -> None:
        """
        voltage_mode: if false set disdance in um instaed of voltage (default)
        message: function for optional callback
        """

        if type(COMport) is int:
            COMport = f"COM{COMport}"
        
        params = PiezoJenaControllers[controler]
        comparams = params.COMparams

        self._piezo = serial.Serial(COMport, timeout = timeout_s, write_timeout = write_timeout_s,
                                    inter_byte_timeout = inter_byte_timeout_s,
                                    baudrate = comparams.baudrate, parity = comparams.parity,
                                    stopbits = comparams.stopbits, xonxoff = comparams.xonxoff,
                                    rtscts = comparams.rtscts, dsrdtr = comparams.dsrdtr)
        self.__mutex = Lock()
        self.__cmds = params.cmds
        self._send_cmd = self.__safe_send_cmd if threadsafe else self.__unsafe_send_cmd
        self._read_cmd = self.__safe_read_cmd if threadsafe else self.__unsafe_read_cmd
        self.__send_term, self.__rcv_term = params.term_in, params.term_out

    def move_um(self, um):
        """
        move piezo to psosition in um
        """
        self.__send_cmd(self.cmds.move(um))

    def __safe_send_cmd(self, cmd):
        with self.__mutex:
            self._piezo.write((cmd + self.__send_term).encode())
    
    def __safe_read_cmd(self, cmd):
        with self.__mutex:
            self._piezo.write((cmd + self.__send_term).encode())
            return self._piezo.readline().decode().split(",")[-1].removesuffix(self.__rcv_term)

    def __unsafe_read_cmd(self, cmd):
        self._piezo.write((cmd + self.__send_term).encode())
        return self._piezo.readline().decode().split(",")[-1].removesuffix(self.__rcv_term)

    def __unsafe_send_cmd(self, cmd):
        self._piezo.write((cmd + self.__send_term).encode())


if __name__ == "__main__":
    from piezo_jena_controllers import NV200_DNET
    test = PiezoJena(6, NV200_DNET)
