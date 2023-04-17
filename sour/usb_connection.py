import usb
from usb.util import (
    endpoint_type, endpoint_direction, ENDPOINT_TYPE_BULK, ENDPOINT_TYPE_INTR,
    ENDPOINT_OUT, ENDPOINT_IN,
)
import struct
import logging
import time
import copy

import sour.codes.utils as code_utils
import sour.codes.usb as USBcodes
import sour.codes.operational as OPcodes
import sour.codes.response as RESPcodes

logger = logging.getLogger()

PTP_USB_CLASS = 0x06
BASE_PTP_MSG_LENGTH = 12
LIMIT_MSG_SIZE = 128 #kb

PTP_MSG_STRUCT = {
    'Length' : 'L',
    'MsgType' : 'H',
    'OpCode' : 'H',
    'TransactionId' : 'L',
    'Payload' : 'Variable'
}

class find_class(object):
    def __init__(self, class_, name=None):
        self._class = class_
        self._name = name
    def __call__(self, device):
        if device.bDeviceClass == self._class:
            return (
                self._name in usb.util.get_string(device, device.iProduct)
                if self._name else True
            )
        for cfg in device:
            intf = usb.util.find_descriptor(
                cfg,
                bInterfaceClass=self._class
            )
            if intf is not None:
                return (
                    self._name in usb.util.get_string(device, device.iProduct)
                    if self._name else True
                )
        return False

def find_usb_cameras(name=None):
    return usb.core.find(
        find_all=True,
        custom_match=find_class(PTP_USB_CLASS, name=name)
    )


class USBconn:

    def __init__(
        self, camera = None,
        idVendor = None, idProduct = None,
        endian = 'little'
    ):
        
        """Connect to a Sony Camera using USB protocol.

        If no arguments are specified the code connects to the first available
        camera

        Args:
        - camera (usb.core.Device): the camera usb object to connect to
        - idVendor (int): USB idVendor of the camera to use. It needs to
                          be expressed as an hex
        - idProduct (int): USB idProduct of the camera to use. It needs to
                           be expressed as an hex
        - endian (string): set the endianess of the messages used in the
                           communications
        """
        

        if isinstance(camera, usb.core.Device):
            self.camera = camera
        else:
            if idProduct and idVendor:
                self.camera = self._choose_specific_camera(
                    idVendor = idVendor,
                    idProduct = idProduct
                    )
            else:
                self.camera = list(find_usb_cameras())[0]

        self._OPCODES = code_utils.combine_dict(OPcodes.OPCODES)

        self.__set_endianess(endian)
        self.__setup_camera()

        usb.util.claim_interface(self.__dev, self.__intf)

    def _choose_specific_camera(self, **kwargs):

        """Select a specific camera
        """

        idVendor = kwargs.get('idVendor')
        idProduct = kwargs.get('idProduct')

        return usb.core.find(
            idVendor=idVendor,
            idProduct=idProduct
            )
    
    def __setup_camera(self):

        """Setup ENPOINTS for USB communication
        """

        for cfg in self.camera:

            for intf in cfg:

                if intf.bInterfaceClass == PTP_USB_CLASS:
                    
                    for EP in intf:
                        
                        ep_type = endpoint_type(EP.bmAttributes)
                        ep_dir = endpoint_direction(EP.bEndpointAddress)
                        
                        if ep_type == ENDPOINT_TYPE_BULK:
                            
                            if ep_dir == ENDPOINT_IN:
                                self.__inep = EP
                            elif ep_dir == ENDPOINT_OUT:
                                self.__outep = EP
                                self.out = EP
                        
                        elif ((ep_type == ENDPOINT_TYPE_INTR) and (ep_dir == ENDPOINT_IN)):
                            self.__intep = EP
                
                if not (self.__inep and self.__outep and self.__intep):
                    self.__inep = None
                    self.__outep = None
                    self.__intep = None
                
                else:
                    self.__cfg = cfg
                    self.__dev = self.camera
                    self.__intf = intf
                    logger.info('USB Device Found and Connected')
                    return True
        
        logger.info('USB Camera not Found')
        return False
    
    def __set_endianess(self, value):

        """Define the endianess of the messages used to communicate
        """

        if value.lower() == 'little':
            self._endian = '<'
        elif value.lower() == 'big':
            self._endian = '>'
        elif value.lower() == 'native_@':
            self._endian = '@'
        elif value.lower() == 'native_=':
            self._endian = '='
        elif value.lower() == 'network':
            self._endian = '!'
    
    def _PTPMsg(self, MsgType, MsgOp, transaction = 0, params = None):

        """Method for building messages using PTP protocol

        Args:
        - MsgType (str) : The type of message that needs to be sent
        - opId (int): The operation ID which is identified with the message count
        - params (dict): A dictionary with the additional paramters to be appendend
                         at the outgoing message. This dictionary has two keys: DataType
                         and Values. The first one has the info about the type of variable
                         (e.g. long, float or char) and it is a string corrisponding to the
                         type using the struct library. The second one is the value of the
                         variable. If there are more variable, both keys need to have list
                         as items of the same length. If the values are bytes the DataType
                         keys is not used
        """
        
        length = 0

        if params:
            paramsMsg = {
                'DataType': [],
                'Value' : []
            }
            for i in params.keys():
                
                if isinstance(params[i]['DataType'], list):
                    
                    for j in range(len(params[i]['DataType'])):
                        if isinstance(params[i]['Value'][j], bytes):
                            length += len(params[i]['Value'][j])
                        else:
                    
                            length += (
                                struct.Struct(
                                    (
                                        self._endian
                                        + params[i]['DataType'][j]
                                        )
                                    ).size
                                )

                        paramsMsg['DataType'].append(params[i]['DataType'][j])
                        paramsMsg['Value'].append(params[i]['Value'][j])

                else:
                    paramsMsg['DataType'].append(params[i]['DataType'])
                    paramsMsg['Value'].append(params[i]['Value'])

                    if isinstance(params[i]['Value'], bytes):
                        length += len(params[i]['Value'])
                    else:
                        length += (
                            struct.Struct(
                                (
                                    self._endian
                                    + params[i]['DataType']
                                    )
                                ).size
                            )
        
        length += BASE_PTP_MSG_LENGTH

        cmdMsg = {
            'length' : {
                'DataType': 'L',
                'Value' : length
                },
            'MsgType' : {
                'DataType': 'H',
                'Value' : MsgType
                },
            'MsgOp' : {
                'DataType': 'H',
                'Value' : MsgOp
                },
            'TransactionId' : {
                'DataType': 'L',
                'Value' : transaction
                },
            }
        
        if params:
            cmdMsg['Params'] = paramsMsg

        return cmdMsg
    
    def _encode_msg(self, ptp_msg):

        """Method to encode a ptp message

        Args:
        - ptp_msg (dict): A dictionary with the message data

        Return:
        - msg (bytes): the encoded message
        """

        msg = b''

        for i in ptp_msg.keys():

            if isinstance(ptp_msg[i]['Value'], list):
                for j in range(len(ptp_msg[i]['Value'])):
                    if isinstance(ptp_msg[i]['Value'][j], bytes):
                        msg += ptp_msg[i]['Value'][j]
                    else:
                        msg += struct.pack(
                            (
                                self._endian
                                + ptp_msg[i]['DataType'][j]
                                ),
                            ptp_msg[i]['Value'][j]
                            )
                    

            elif isinstance(ptp_msg[i]['Value'], bytes):
                msg += ptp_msg[i]['Value']

            else:
                msg += struct.pack(
                    (
                        self._endian
                        + ptp_msg[i]['DataType']
                        ),
                    ptp_msg[i]['Value']
                    )

        return msg
    
    def _decode_msg(self, PTPmsg):

        """Decode a PTP Message

        Args:
        - PTPmsg (bytes): the incoming message to be decoded

        Return:
        - msg (dict): return a dictionary with the decoded message.
                      If a payload is present only for Response type
                      messages this one is decoded. For the other
                      types, the payload is returned as bytes
        """

        msg = {}

        idx_start = 0

        for i in PTP_MSG_STRUCT.keys():

            if i == 'Payload':
                if len(PTPmsg) > BASE_PTP_MSG_LENGTH:

                    if msg['MsgType'] == 'Response':
                        msg['Payload'] = struct.unpack(
                            (
                                self._endian
                                + 'L'
                                ),
                            PTPmsg[idx_start:]
                            )[0]
                    
                    elif msg['MsgType'] == 'Data':
                        #Data Message are parsed only if required
                        msg[i] = PTPmsg[idx_start:]
            
            else:

                idx_end = (
                    struct.Struct(
                        (
                            self._endian
                            + PTP_MSG_STRUCT[i]
                            )
                        ).size
                    + idx_start
                    )

                msg[i] = struct.unpack(
                    (
                        self._endian
                        + PTP_MSG_STRUCT[i]
                        ),
                    PTPmsg[idx_start:idx_end]
                    )[0]

                if i == 'MsgType':
                    msg[i] = code_utils.decode_code(USBcodes.USB_OPERATIONS, msg[i])
                
                elif i == 'OpCode':
                    
                    if msg['MsgType'] == 'Response':
                        msg['RespCode'] = code_utils.decode_code(RESPcodes.RESPCODES['Values'], msg[i])
                    else:
                        msg[i] = code_utils.decode_code(self._OPCODES['Values'], msg[i])

                idx_start = copy.copy(idx_end)
        
        return msg
    
    def _send(self, ptp_msg, EP):
        """Helper method for sending data
        
        Args:
        - ptp_msg (bytes): encoded message to be sent
        - EP : endpoint used for sending the message
        """
        
        try:
            sent = 0
            while sent < len(ptp_msg):
                sent = EP.write(
                    ptp_msg[sent:(sent + LIMIT_MSG_SIZE*2**10)]
                )
        except usb.core.USBError:
            pass

    def _receive(self, max_reading_size=None, event=False):

        """Helper method for receiving a message

        Return:
        - ptp_msg (bytes): encoded PTP message (can be data or a response)
        """

        EP = self.__intep if event else self.__inep

        ptp_msg = b''

        reads = 0

        while len(ptp_msg) < BASE_PTP_MSG_LENGTH and reads < 5:

            ptp_msg += EP.read(EP.wMaxPacketSize)

            reads += 1
        
        msg_length = struct.unpack(
            (
                self._endian
                + 'L'
                ),
            ptp_msg[:4])[0]
        
        if not max_reading_size:
            max_reading_size=LIMIT_MSG_SIZE*2**10

        while len(ptp_msg) < msg_length:
            ptp_msg +=  EP.read(
                min(
                    msg_length - BASE_PTP_MSG_LENGTH,
                    # Up to 128kB
                    max_reading_size
                    )
                )

        return ptp_msg
    
    def send_recv_Msg(
        self, MsgType, opId, params = None, receive = True,
        transaction = 0, data = None, event = False, timeout = 0.004,
        max_reading_size=None
    ):
        
        """Method to send a message and receive a response

        Args:
        - MsgType (str) : The type of message that needs to be sent
        - opId (int): The operation ID which is identified with the message count
        - params (dict): A dictionary with the additional paramters to be appendend
                         at the outgoing message
        - receive (bool): If True, a returning message is expected
        - transaction (int): transaction counter for USB operation
        - data (dict): A dictionary with the same structure of the params dict. This
                       dict contains additional data that needs to be sent other than
                       the original command
        - timout (float): a timeout in sec to wait between the outgoing message and the
                          eventual incoming message. This is to ensure that also long messages
                          are sent
        """

        EP = self.__intep if event else self.__outep

        PTPmsgOut = self._PTPMsg(MsgType, opId, params = params, transaction = transaction)

        PTPbyteMsg = self._encode_msg(PTPmsgOut)

        if data:
            dataMsg = self._PTPMsg(USBcodes.USB_OPERATIONS['Data'], opId, params = data, transaction = transaction)

            databyeMsg = self._encode_msg(dataMsg)
            self._send(PTPbyteMsg, EP)
            self._send(databyeMsg, EP)
        else:
            self._send(PTPbyteMsg, EP)

        if receive:
            time.sleep(timeout)
            PTPmsgIn = self._receive(max_reading_size = max_reading_size)

        return PTPmsgIn
