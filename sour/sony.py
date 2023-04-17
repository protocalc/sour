import logging
import time
import struct
import copy
import os
import io
import json
import datetime

from fractions import Fraction
import decimal

import sour.usb_connection as USBconn

#Codes Import
import sour.codes.utils as code_utils
import sour.codes.usb as USBcodes
import sour.codes.operational as OPcodes
import sour.codes.properties as PROPcodes
import sour.codes.datatype as DTcodes
import sour.codes.sony_misc as SMcodes
import sour.codes.fileops as FOcodes



if logging.getLogger().hasHandlers():
    logger = logging.getLogger()
else:
    path = os.path.dirname(os.path.realpath(__file__))
    date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    if not os.path.exists(path+'/logs'):
        os.mkdir(path+'/logs')

    logname = path+'/logs/camera_'+date+'.log'

    logging.basicConfig(
        filename=logname,
        filemode='w',
        format='%(asctime)s    [%(threadName)s]    %(levelname)s:%(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        level=logging.DEBUG
        )
    logger = logging.getLogger('CameraLog')

class SONYconn:

    def __init__(
        self, name, **kwargs
    ):
        
        self.name = name

        camera = kwargs.get('camera', None)

        if camera:
            self.connection = USBconn.USBconn(camera=camera)
        else:
            self.connection = USBconn.USBconn()

        self._OPCODES = code_utils.combine_dict(OPcodes.OPCODES)
        self._PROPCODES = code_utils.combine_dict(PROPcodes.PROPCODES)

        self.transactionID = 0

        self._session_open = False
        self.sessionID = 0
        self.prop_loaded = False
        self.__endian = self.connection._endian
        self.__video_modes = ['Movie', 'HiFrameRate']
        self.__photo_count = 0
        
    def _session_handler(self, ControlMode='RemoteControl'):

        """
        Handle the session to the USB camera device

        Args:
        - mode (str): The specific mode to use to open the session to
                      the camera. This is used only for opening the
                      session. Indeed for closing, the command seems
                      to be the same
        """

        self.sessionID += 1

        if ControlMode.lower() == 'remotecontrol':
            params = {
                'Msg' : {
                    'Value': self.sessionID,
                    'DataType': 'L'
                }
            }
            if not self._session_open:
                cmd = self._OPCODES['Values']['OpenSession']
            else:
                cmd = self._OPCODES['Values']['CloseSession']
        else:
            if not self._session_open:
                cmd = self._OPCODES['Values']['MTPSession']
                params = {
                    'Msg' : {
                        'Value': 0x0000000100000001,
                        'DataType': 'Q'
                    }
                }
            else:
                self._request_handler(True)
                time.sleep(0.05)
                cmd = self._OPCODES['Values']['CloseSession']
                params = {
                    'Msg' : {
                        'Value': self.sessionID,
                        'DataType': 'L'
                    }
                }


        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            params = params,
            receive = True,
            transaction = self.transactionID
            )

        resp = self.connection._decode_msg(PTPmsg)

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                self._session_open = not self._session_open
                if self._session_open:
                    logger.info(f'Open Session to Camera in {ControlMode} mode')
                else:
                    logger.info('Close Session to Camera')
            else:
                if not self._session_open:
                    logger.info('Cannot Open Session to Camera')
                else:
                    logger.info('Cannot Close Session to Camera')

        self.transactionID += 1

    def __handshake(self, count, key1 = 0, key2 = 0):

        """Generate a handshake for the USB connection

        Args:
        - count (int): a counter for the number of handshakes
        - key1 (int): unknown
        - key2 (int): unknown

        Returns:
        - resp (str): Return the response code to the command
        """

        params = {
            'Msg' : {
                'Value': [count, key1, key2],
                'DataType': ['L']*3
            }
        }

        _ = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SDIOConnect'],
            params= params,
            receive = True,
            transaction = self.transactionID
            )

        resp = self.connection._decode_msg(self.connection._receive())

        self.transactionID += 1

        if resp['MsgType'] == 'Response':
            return resp['RespCode']
        else:
            return None
        
    def __sony_info(self, code=0x12c):

        """Request some info to the camera

        Args:
        - code (int): The default value has been found through
                      reverse engineering, so its meaning is
                      unknown

        Returns:
        - resp (str): Return the response code to the command
        """

        params = {
            'Msg' : {
                'Value': code,
                'DataType': 'L'
            }
        }

        _ = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SDIOGetExtDeviceInfo'],
            params= params,
            receive = True,
            transaction = self.transactionID
            )

        resp = self.connection._decode_msg(self.connection._receive())

        self.transactionID += 1

        if resp['MsgType'] == 'Response':
            return resp['RespCode']
        else:
            return None
    
    def initialize_camera(self, ControlMode='RemoteControl'):

        """Initialize the camera. The full handshake has been
        found using reverse engineering

        Args:
        - ControlMode (str): The specific mode to control the camera
        
        """

        self._session_handler(ControlMode=ControlMode)

        resp = []

        resp.append(self.__handshake(1))
        resp.append(self.__handshake(2))
        resp.append(self.__sony_info())
        resp.append(self.__handshake(3))
        resp.append(self.__sony_info())

        if all(list(map(lambda r: r == 'OK', resp))):
            logger.info('Camera Initialized Correctly')
        else:
            logger.info('Camera Not Initialized Correctly')

        time.sleep(0.05)

        self.get_camera_properties()

        time.sleep(0.5)
        self.get_camera_properties()

        mode = self.camera_properties['ExposureProgramMode']['CurrentValue']

        if any(md in mode for md in self.__video_modes):
            self._current_mode = 'Video'
        else:
            self._current_mode = 'Photo'
    
    def _request_handler(self, close = False):

        cmd = self._OPCODES['Values']['SendRequest']

        if close:
            request = [
                '0002', '0000', '0000', '0000',
                '0001', '0000'
            ]
        else:
            request = [
                '0002', '0000', '0001', '0000',
                '0000', '0000'
            ]

        request = [int(x,16) for x in request]

        request_params = {
            'Msg' : {
                'DataType' : ['H']*len(request),
                'Value': request
            }
        }

        _ = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            params= request_params,
            receive = True,
            transaction = self.transactionID
        )

        self.transactionID += 1
    
    def start_MTP_comms(self):

        data_trusted_file_op = [
            '0003', '0001', '0008', '0701',
            '0000', '0000', '0100', '0002',
            '0008', 'FF03', '0000', '0000',
            '0000', '0003', '0008', 'FF00',
            'FFFF', '0000', '0000'
        ]

        data_trusted_file_op = [int(x, 16) for x in data_trusted_file_op]

        cmd = self._OPCODES['Values']['EnableTrustedFileOp']

        data = {
            'Msg': {
                'DataType': ['H']*len(data_trusted_file_op),
                'Value' : data_trusted_file_op
            }
        }

        _ = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            data = data,
            receive = True,
            transaction = self.transactionID
        )

        self.transactionID += 1

        self._request_handler()

    def __decode_obj_list(self, msg):

        objLength = struct.unpack('<L', msg[:4])[0]

        objList = {
            'Code': [],
            'Date': []
        }

        single_objLength = int((len(msg)-4)/objLength)
        start_length = 4
        sep_lenth = 4

        for i in range(objLength):

            tmp = copy.copy(
                msg[4+single_objLength*i:4+single_objLength*(i+1)]
                )
            
            objList['Code'].append(
                struct.unpack('<L', tmp[:start_length])[0]
                )

            date_temp = struct.unpack(
                '<'+10*'H',
                tmp[start_length+sep_lenth+1:start_length+sep_lenth+21]
            )

            date_temp = ''.join(str(hex(x)[2:]) for x in date_temp)

            objList['Date'].append(
                bytes.fromhex(date_temp).decode('utf-8')
            )

        return objList

    def _getObjList(self):

        cmd = self._OPCODES['Values']['GetObjPropList']

        params = [
            '0000', '0000', '3001', '0000',
            'DC07', '0000', '0000', '0000',
            '0001', '0000'
        ]

        params = [int(x,16) for x in params]
        
        cmd_params = {
            'Msg' : {
                'DataType' : ['H']*len(params),
                'Value': params
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            params= cmd_params,
            receive = True,
            transaction = self.transactionID
        )

        _ = self.connection._receive()

        resp = self.connection._decode_msg(PTPmsg)

        self.objList = self.__decode_obj_list(resp['Payload'])

        self.transactionID += 1

    def __decode_file_code_objList(self, msg):

        file_number = struct.unpack('<L', msg[:4])[0]
        
        files = []

        for i in range(file_number):

            files.append(
                struct.unpack('<L', msg[4*(i+1):4*(i+2)])[0]
            )

        return files
    
    def __decode_file_name(self, msg):

        length = copy.copy(msg[0])

        datatype = '<'+'H'*(length-1)
        tmp = struct.unpack(datatype, msg[1:-2])

        name = ''.join(str(hex(x)[2:]) for x in tmp)

        return bytes.fromhex(name).decode('utf-8')

    def __get_single_file_info(self, code):

        cmd = self._OPCODES['Values']['GetObjInfo']

        params_name = {
            'Msg' : {
                'DataType' : ['L', FOcodes.SONY_FILE_OPS['DataType']],
                'Value' : [code, FOcodes.SONY_FILE_OPS['Value']['GetName']]
            }
        }


        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            params= params_name,
            receive = True,
            transaction = self.transactionID
        )

        _ = self.connection._receive()

        resp = self.connection._decode_msg(PTPmsg)

        name = self.__decode_file_name(resp['Payload'])

        self.transactionID += 1

        params_code = {
            'Msg' : {
                'DataType' : ['L', FOcodes.SONY_FILE_OPS['DataType']],
                'Value' : [code, FOcodes.SONY_FILE_OPS['Value']['GetDownloadCode']]
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            params= params_code,
            receive = True,
            transaction = self.transactionID
        )

        _ = self.connection._receive()

        resp = self.connection._decode_msg(PTPmsg)

        code = copy.copy(resp['Payload'])

        return name, code

    def _get_files_single_objList(self, objcode):

        cmd = self._OPCODES['Values']['GetObjectHandles']

        cmds_val = [
            '0001', '0001', '0000', '0000'
        ]

        cmds_val = [int(x, 16) for x in cmds_val]

        cmds_val.append(objcode)

        datatype = ['H']*(len(cmds_val)-1)
        datatype.append('L')

        cmd_params = {
            'Msg' : {
                'DataType' : datatype,
                'Value' : cmds_val
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            cmd,
            params= cmd_params,
            receive = True,
            transaction = self.transactionID
        )

        _ = self.connection._receive()

        resp = self.connection._decode_msg(PTPmsg)

        self.transactionID += 1

        files = self.__decode_file_code_objList(resp['Payload'])

        return files

    def get_files_info(self):

        self._getObjList()

        files_dict = {}
        files_count = 0

        for i in range(len(self.objList['Date'])):

            files_dict[self.objList['Date'][i]] = {}
            files_dict[self.objList['Date'][i]]['Code'] = self.objList['Code'][i]

            file_codes = self._get_files_single_objList(self.objList['Code'][i])

            files_dict[self.objList['Date'][i]]['FileCode'] = copy.copy(file_codes)
            files_dict[self.objList['Date'][i]]['Name'] = []
            files_dict[self.objList['Date'][i]]['DownloadCode'] = []

            for j in file_codes:

                name, code = self.__get_single_file_info(j)

                files_dict[self.objList['Date'][i]]['Name'].append(name)
                files_dict[self.objList['Date'][i]]['DownloadCode'].append(code)

                files_count += 1

        return files_dict, files_count
    
    def __decode_single_property_msg(self, msg):

        """Helper method to decode a single property message
        
        Args:
        - msg (bytes): a stream of bytes starting with the message to be decoded

        Returns:
        - property_name (str): the name of the property
        - vals (dict): a dictionary with the property characteristics, such as
                       current values, avalailable values and others
        - msg_len (int): the length of the bytes stream just decoded
        """

        vals = {}

        msg_len = 0

        vals['PropertyCode'] = struct.unpack(
            (
                self.__endian
                + 'H'
                ),
            msg[:2])[0]

        property_name = code_utils.decode_code(self._PROPCODES['Values'], vals['PropertyCode'])

        msg_len += 2

        dataType = code_utils.decode_datatype(
            DTcodes.PTP_DATATYPE['Values'],
            struct.unpack(
                (
                    self.__endian
                    + DTcodes.PTP_DATATYPE['DataType']
                    ),
                msg[msg_len:msg_len+2]
                )[0]
            )
        
        vals['DataType'] = copy.copy(dataType)

        dataType_len = struct.Struct(
            self.__endian
            + dataType
            ).size

        msg_len += 2

        if struct.unpack(self.__endian + 'B', msg[msg_len:msg_len+1])[0] == 1:
            vals['GetSet'] = 'GetSet'
        else:
            vals['GetSet'] = 'Set'

        msg_len += 1

        vals['Visibility'] = code_utils.decode_code(
            SMcodes.SONY_VISIBILITY['Values'],
            struct.unpack(
                (
                    self.__endian
                    + 'B'
                ),
                msg[msg_len:msg_len+1]
                )[0]
            )
        msg_len += 1

        val = struct.unpack(
            (
                self.__endian
                + dataType
            ),
            msg[msg_len:msg_len+dataType_len]
            )[0]

        
        val = code_utils.property(property_name, val, self.__endian).decoder()

        if isinstance(val, bytes):
            val = val.decode('utf-8')

        vals['FactoryDefaultValue'] = val

        msg_len += dataType_len

        val = struct.unpack(
            (
                self.__endian
                + dataType
                ),
            msg[msg_len:msg_len+dataType_len]
            )[0]
        
        val = code_utils.property(property_name, val, self.__endian).decoder()

        if isinstance(val, bytes):
            val = val.decode('utf-8')

        vals['CurrentValue'] = val

        msg_len += dataType_len

        vals['FmtFlag'] = struct.unpack(
            (
                self.__endian
                +'B'
            ),
            msg[msg_len:msg_len+1]
            )[0]

        msg_len += 1

        if vals['FmtFlag'] == 0:
            pass
        elif vals['FmtFlag'] == 1:
            tmp = struct.unpack(
                (
                    self.__endian
                    + 3*dataType
                    ),
                msg[msg_len:msg_len+dataType_len*3]
                )

            vals['MinValue'] = tmp[0]
            vals['MaxValue'] = tmp[1]
            vals['StepValue'] = tmp[2]

            msg_len += 3*dataType_len

        elif vals['FmtFlag'] == 2:
            fmt_len = struct.unpack(
                (
                    self.__endian
                    + 'H'
                    ),
                msg[msg_len:msg_len+2]
                )[0]

            msg_len += 2

            vals['AvailableValues'] = {}
            vals['AvailableValues']['Photo'] = []

            for _ in range(fmt_len):

                val = struct.unpack(
                    (
                        self.__endian
                        + dataType
                        ),
                    msg[msg_len:msg_len+dataType_len]
                    )[0]

                val = code_utils.property(property_name, val, self.__endian).decoder()

                if isinstance(val, bytes):
                    val = val.decode('utf-8')

                vals['AvailableValues']['Photo'].append(val)

                msg_len += dataType_len

            tmp = struct.unpack(
                (
                    self.__endian
                    + 'H'
                    ),
                msg[msg_len:msg_len+2]
                )[0]

            if tmp < 0x1000:

                vals['AvailableValues']['Video'] = []

                fmt_len = copy.copy(tmp)

                msg_len += 2

                for _ in range(fmt_len):
                    
                    val = struct.unpack(
                        (
                            self.__endian
                            + dataType
                            ),
                        msg[msg_len:msg_len+dataType_len]
                        )[0]

                    val = code_utils.property(property_name, val, self.__endian).decoder()

                    if isinstance(val, bytes):
                        val = val.decode('utf-8')

                    vals['AvailableValues']['Video'].append(val)

                    msg_len += dataType_len

        return property_name, vals, msg_len

    def _all_properties_msg(self, msg):

        msg_len = struct.unpack(
            (
                self.__endian
                + 'Q'
            ),
            msg[:8]
            )[0]
        
        properties = {}

        msg_read = 8

        count = 0

        while count < msg_len:

            prop, vals, tmp = self.__decode_single_property_msg(msg[msg_read:])

            properties[prop] = vals

            msg_read += tmp
            count += 1

        return properties
    
    def get_camera_properties(self):

        """Ask the camera for all the properties

        Returns:
        - vals (str) : A decoded dictionary with all the properties
        """

        file_path = 'sour/camera_database/'
        file_name = self.name.strip().lower().replace(' ', '')+'.json'

        if os.path.exists(file_path+file_name) and not self.prop_loaded:
            with open(file_path+file_name, 'r') as jfile:
                vals = json.load(jfile)
            self.prop_loaded = True

        else:
            params = {
                'Msg' : {
                    'Value': 0,
                    'DataType': 'L'
                }
            }

            PTPmsg = self.connection.send_recv_Msg(
                USBcodes.USB_OPERATIONS['Command'],
                self._OPCODES['Values']['GetAllDevicePropData'],
                params=params,
                receive = True,
                transaction = self.transactionID
                )

            _ = self.connection._receive()

            resp = self.connection._decode_msg(PTPmsg)

            vals = self._all_properties_msg(resp['Payload'])

            self.transactionID += 1

            self.camera_properties = copy.copy(vals)

            self.__focus_mode = copy.copy(
                self.camera_properties['FocusMode']['CurrentValue']
            )
    
    def save_camera_properties(self):

        file_path = 'sour/camera_database/'
        file_name = self.name.strip().lower().replace(' ', '')+'.json'

        with open(file_path+file_name, 'w') as j:
            json.dump(self.camera_properties, j)
    
    def messageHandler(self, command, value):

        cmd = command.strip().lower().replace(' ', '')

        if cmd == 'focusmode':
            out = self._set_focus_mode(value)

        elif cmd == 'shutterspeed':
            out = self._set_shutter_speed(value)

        elif cmd == 'iso':
            out = self._set_iso(value)

        elif cmd == 'programmode':
            out = self._set_camera_mode(value)

        elif cmd == 'image':
            out = self._get_live_view()

        elif cmd == 'capture':
            out = self._capture_photo()

        return out
    
    def _capture_photo(self):

        capture = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['Capture'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        autofocus = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['AutoFocus'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        down = {
            'Msg' : {
                'Value': SMcodes.SONY_BUTTON['Values']['Down'],
                'DataType': SMcodes.SONY_BUTTON['DataType']
            }
        }

        up = {
            'Msg' : {
                'Value': SMcodes.SONY_BUTTON['Values']['Up'],
                'DataType': SMcodes.SONY_BUTTON['DataType']
            }
        }

        resp = []

        expected_resp = 2

        if self.__focus_mode == 'AF_S':
            
            tmp = self.connection.send_recv_Msg(
                USBcodes.USB_OPERATIONS['Command'],
                self._OPCODES['Values']['SetControlDeviceB'],
                params=autofocus,
                data=down,
                transaction = self.transactionID
            )

            tmp = self.connection._decode_msg(tmp)

            if tmp['MsgType'] == 'Response':
                resp.append(tmp['RespCode'])

            self.transactionID += 1

            expected_resp = 4

            time.sleep(0.5)

        tmp = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=capture,
            data=down,
            transaction = self.transactionID
            )

        t = time.time()

        tmp = self.connection._decode_msg(tmp)

        if tmp['MsgType'] == 'Response':
            resp.append(tmp['RespCode'])

        self.transactionID += 1
        
        time.sleep(0.035)

        tmp = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=capture,
            data=up,
            transaction = self.transactionID
            )

        self.transactionID += 1

        tmp = self.connection._decode_msg(tmp)

        if tmp['MsgType'] == 'Response':
            resp.append(tmp['RespCode'])

        if self.__focus_mode == 'AF_S':

            time.sleep(0.5)

            tmp = self.connection.send_recv_Msg(
                USBcodes.USB_OPERATIONS['Command'],
                self._OPCODES['Values']['SetControlDeviceB'],
                params=autofocus,
                data=up,
                transaction = self.transactionID
            )

            tmp = self.connection._decode_msg(tmp)

            if tmp['MsgType'] == 'Response':
                resp.append(tmp['RespCode'])

            self.transactionID += 1

        if len(resp) == expected_resp:
            if all(list(map(lambda r: r == 'OK', resp))):
                logger.info(f'Photo Captured # {self.__photo_count} at {t} s')

                self.__photo_count += 1
                return True
            else:
                logger.info('Photo not Captured')
                return False
        else:
            logger.info('Did not get response from Commands')
            return False

    def _set_focus_mode(self, mode='auto'):

        if mode == 'manual':
            mode = 'MF'
        elif mode == 'auto':
            mode = 'AF_S'

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['FocusMode'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode_msg = {
            'Msg' : {
                'Value': PROPcodes.SONY_FOCUS_MODE['Values'][mode],
                'DataType': PROPcodes.SONY_FOCUS_MODE['DataType']
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode_msg,
            transaction = self.transactionID
            )

        resp = self.connection._decode_msg(PTPmsg)

        self.transactionID += 1

        time.sleep(0.05)

        self.get_camera_properties()

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set Focus Mode: {mode}')
                
                return True
            
        return False
    
    def _set_shutter_speed(self, value):

        if isinstance(value, float) or isinstance(value, int):
            value = value
        else:
            value = float(Fraction(value))

        self.camera_properties = self.get_camera_properties()
        

        available_shutter = list(
            map(
                lambda x: float(Fraction(x)),
                self.camera_properties['ShutterSpeed']['AvailableValues'][self._current_mode]
            )
        )

        if value not in available_shutter:
            tmp = list(
                map(
                    lambda x: abs(x-value),
                    available_shutter
                    )
                )

            if len(tmp) < 1:
                value = value
                old = copy.copy(value)
            else:

                idx = tmp.index(min(tmp))

                old = copy.copy(value)

                value = available_shutter[idx]

            logger.info(f'Choose the closest Shutter Speed, {value}, to the one selected {old}')

        num, den = decimal.Decimal(str(value)).as_integer_ratio()

        num_bytes = struct.pack(
            self.__endian
            + 'H', num
            )
        
        den_bytes = struct.pack(
            self.__endian
            + 'H', den
            )

        val = den_bytes+num_bytes

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['ShutterSpeed'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode = {
            'Msg' : {
                'Value': val,
                'DataType': 'NA'
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode,
            transaction = self.transactionID
            )

        resp = self.connection._decode_msg(PTPmsg)

        self.transactionID += 1

        time.sleep(0.05)

        self.get_camera_properties()

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set New Shutter Speed: {value}')

                return True

        return False

    def _set_iso(self, value):

        if isinstance(value, int) or isinstance(value, float):
            mode = 0
            ext = 0

        elif isinstance(value, list):
            if len(value) > 2:
                ext = value[2]

            mode = value[0]
            value = value[1]
        
        available_ISO = list(
            map(
                lambda x: self.__ISO2bin(x),
                self.camera_properties['ISO']['AvailableValues'][self._current_mode]
            )
        )

        newISO = self.__ISO2bin(value, mode, ext)

        if newISO not in available_ISO:
            tmp = list(
                map(
                    lambda x: abs(x-newISO),
                    available_ISO
                    )
                )
            idx = tmp.index(min(tmp))

            newISO = available_ISO[idx]

            tmp = self.__bin2ISO(newISO)

            logger.info(f'Choose the closest ISO, {tmp}, to the one selected {value}')

        
        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['ISO'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode = {
            'Msg' : {
                'Value': newISO,
                'DataType': 'L'
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode,
            )

        resp = self.connection._decode_msg(PTPmsg)

        self.transactionID += 1

        time.sleep(0.05)

        self.get_camera_properties()

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set New ISO: {value}')

                return True

        return False

    def _set_camera_mode(self, mode = 'Photo_M'):

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['ExposureProgramMode'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode_dict = {
            'Msg' : {
                'Value': PROPcodes.SONY_EXPMODE['Values'][mode],
                'DataType': PROPcodes.SONY_EXPMODE['DataType']
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode_dict,
            )

        resp = self.connection._decode_msg(PTPmsg)

        if any(md in mode for md in self.__video_modes):
            self._current_mode = 'Video'
        else:
            self._current_mode = 'Photo'

        self.transactionID += 1

        time.sleep(0.05)

        self.get_camera_properties()

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set Camera mode: {self._current_mode}_{mode}')

                return True
            else:
                logger.info(f'Impossible to set Camera mode to {mode}')

                return False
            
        return False

    def _get_live_view(self):

        import PIL.Image
        import PIL.ImageOps
        import numpy as np

        params = {
            'Msg' : {
                'Value' : 0xFFFFc002,
                'DataType': 'L'
            }
        }

        PTPmsg = self.connection.send_recv_Msg(
            USBcodes.USB_OPERATIONS['Command'],
            self._OPCODES['Values']['GetObject'],
            params=params,
            receive = True,
            transaction = self.transactionID
            )

        _ = self.connection._receive()

        resp = self.connection._decode_msg(PTPmsg)

        raw_img_start = resp['Payload'].find(b'\xff\xd8\xff')
        raw_img = io.BytesIO(resp['Payload'][raw_img_start:])
        img = np.asarray(
            PIL.ImageOps.flip(
                PIL.Image.open(raw_img).rotate(90, expand=True)
            )
        )

        self.transactionID += 1

        return img
    
    def _transfer_large_files(self, file_name, file_code, file_download_code, chunk_size = 15*1e3*2**10):

        def generate_download_codes_params(file_download_code, counter1, counter2):

            cmd = [
                file_code,
                0, 0, 0, counter1,
                counter2,
                file_download_code
            ]

            cmd_params = {
                'Msg': {
                    'DataType': [
                        'L',
                        'B', 'B', 'B', 'B',
                        'L',
                        'L'
                    ],
                    'Value': cmd
                }
            }

            return cmd_params

        if isinstance(file_download_code, bytes):
            download_code = struct.unpack('<L', file_download_code)[0]
        else:
            download_code = copy.copy(file_download_code)

        if file_name[file_name.find('.')+1:] == 'MP4':
            file_download_code = 0x08000000
            header = b'\x66\x74\x79\x70'
        else:
            header = b'\xff\xd8\xff'

        buffer_size = int(os.popen('cat /sys/module/usbcore/parameters/usbfs_memory_mb').read()[:-1])*2**10*1e3

        if chunk_size > buffer_size:
            size = buffer_size
        else:
            size = chunk_size

        file_data = b''
        
        counter1 = 0
        counter2 = 0

        while True:

            cmd_params = generate_download_codes_params(file_download_code, counter1, counter2)

            PTPmsg = self.connection.send_recv_Msg(
                USBcodes.USB_OPERATIONS['Command'],
                self._OPCODES['Values']['GetFile'],
                params= cmd_params,
                receive = True,
                transaction = self.transactionID,
                max_reading_size = int(size)
            )

            resp = self.connection._receive(max_reading_size=15*1e3*2**10)
            resp = self.connection._decode_msg(resp)

            msg = self.connection._decode_msg(PTPmsg)

            file_data += msg['Payload']

            self.transactionID += 1

            if resp['Payload'] == download_code:
                print('Finished Transfer')
                logger.info(f'Downloaded File {file_name}')
                break

            counter1 += 8
            if counter1 > int('F8', 16):
                counter1 = 0
                counter2 += 1

        file_start = file_data.find(header)

        with open(file_name, 'wb') as writer:
            writer.write(file_data[file_start:])
        
        del file_data
