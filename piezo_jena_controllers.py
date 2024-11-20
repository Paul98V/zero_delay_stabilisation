import serial
from dataclasses import dataclass
from typing import Callable

type ByeteSize = serial.FIVEBITS | serial.SIXBITS | serial.SEVENBITS | serial.EIGHTBITS  
type Parity = serial.PARITY_NONE | serial.PARITY_EVEN | serial.PARITY_ODD | \
              serial.PARITY_MARK | serial.PARITY_SPACE
type StopBits = serial.STOPBITS_ONE | serial.STOPBITS_ONE_POINT_FIVE | serial.STOPBITS_TWO

@dataclass
class COMParams:
    baudrate : int
    bytesize : ByeteSize = serial.EIGHTBITS
    parity : Parity = serial.PARITY_NONE
    stopbits : StopBits = serial.STOPBITS_ONE
    xonxoff : bool = False
    rtscts : bool = False
    dsrdtr : bool = False

@dataclass
class CMDS:
    move : Callable[[float], str]
    pos : str
    setmode_um : str
    setmode_V : str

@dataclass
class ControlerParams:
    COMparams : COMParams
    cmds : CMDS
    term_in : str = "\r"
    term_out : str = "\r\n"

#######################################################################################
###
###  enter names of new controlers here
###
#######################################################################################

@dataclass
class NV200_DNET:
    pass

type ControlerName = NV200D_NET

#######################################################################################
###
###  enter values of new controlers here
###
#######################################################################################

PiezoJenaControllers : dict[ControlerName, ControlerParams] = {
        NV200_DNET : ControlerParams(
            COMParams(baudrate = 115200,
                      bytesize = serial.EIGHTBITS,
                      parity = serial.PARITY_NONE,
                      stopbits = serial.STOPBITS_ONE,
                      xonxoff = True),
            CMDS(move = lambda x: f"set,{x}",
                 pos = "meas",
                 setmode_um = "cl,1",
                 setmode_V = "cl,0"),
            ),
        }
