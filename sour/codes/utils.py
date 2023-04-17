import copy
import struct
import decimal

import sour.codes.properties as PROPcodes

def decode_code(codes_dict, code):

    """Find the string corrispond to a specific code

    Args:
    - codes_dict (dict): the lookup dictionary
    - code (int): the code to be looked for

    Returns:
    - code_name (str): the corrispondent code name
    """

    try:
        code_name = list(codes_dict.keys())[list(codes_dict.values()).index(code)]
    except ValueError:
        code_name = 'Unknown : ' + str(hex(code))
    return code_name

def decode_datatype(codes_dict, code):

    """Find the string corrispond to a specific code just
    for a datatype-like dictionary

    Args:
    - codes_dict (dict): the lookup dictionary
    - code (int): the code to be looked for

    Returns:
    - code_name (str): the corrispondent code name
    """
    
    try:
        idx = list(map(lambda x: x['Code'], codes_dict.values())).index(code)
        code_name = list(codes_dict.keys())[idx]
    except ValueError:
        code_name = 'Unknown : ' + str(hex(code))
    return code_name

def combine_dict(dict_list):

    """Combine Codes dictionaries together

    Args:
    - dict_list (dict): a list with the dictionaries to be comined

    Returns:
    - final_dict (dict): the final dictionary that combines together
                         all the input dictionaries
    """

    final_dict = copy.copy(dict_list[0])

    for i in range(len(dict_list)-1):

        for key, value in dict_list[i+1].items():
            if key in final_dict:
                if isinstance(final_dict[key], str):
                    pass
                else:
                    final_dict[key].update(value)
            else:
                final_dict[key] = value
    
    return final_dict

class property:

    def __init__(
            self, prop, val, endian,
    ):
        
        self.prop = prop
        self.val = val
        self.__endian = endian

    def decoder(self, **kwargs):

        if self.prop == 'ISO':
            return self.bin2ISO(self.val)
        elif self.prop == 'ShutterSpeed':
            return self.bytes2shutter(self.val)
        elif self.prop == 'ExposureBiasCompensation':
            return self.bytes2expcomp(self.val)
        else:
            if self.prop in list(PROPcodes.SONY_PROPVALUES.keys()):
                return decode_code(PROPcodes.SONY_PROPVALUES[self.prop]['Values'], self.val)
            return self.val

    def encoder(self, **kwargs):

        if self.prop == 'ISO':
            mode = kwargs.get('mode', 0)
            ext = kwargs.get('ext', 0)
            return self.ISO2bin(self.val, mode, ext)
        elif self.prop == 'ShutterSpeed':
            return self.shutter2bytes(self.val)
        elif self.prop == 'ExposureBiasCompensation':
            return self.expcomp2bytes(self.val)
        else:
            if self.prop in list(PROPcodes.SONY_PROPVALUES.keys()):
                return PROPcodes.SONY_PROPVALUES[self.prop]['Values'].index(self.val)
            return self.val

    def bin2ISO(self, val):
        """Convert binary value of ISO to a readable string

        Args:
        - val (bytes): value to be converted

        Returns:
        - ISO (str): a string with the ISO value
        """
        
        tmp = bin(val)[2:]
        
        if len(tmp) < 32:
            tmp = (
                '0' * (
                    32
                    - len(tmp)
                    )
                + tmp
                )
        
        ISOmode = int(tmp[-28:-24],2)
        ISOval = int(tmp[-24:],2)

        ISO = ''

        if ISOmode != 0:
            ISO += decode_code(PROPcodes.SONY_ISO_MODE['Values'], ISOmode)
            ISO += ' '

        if ISOval == PROPcodes.SONY_ISO_AUTO:
            ISO += 'AUTO'
        else:
            ISO += str(ISOval)

        return ISO

    def ISO2bin(self, val, mode=0, ext=0):

        """Return a binary encoding of the ISO value

        Args:
        - val (int or str): the value of the ISO to be encoded.
                            If a string, The first part includes
                            the possible ISO modes
        - mode (int or str): the mode of the ISO. If val is a string
                             this is superseeded by that.
        - ext (int): the extension of the ISO
        """

        if isinstance(val, str):

            if len(val) > 6:
                if val.find('_High') >=0:
                    mode_len = len('MultiFrameNR_High ')
                else:
                    if val.find('MultiFrameNR') >= 0:
                        mode_len = len('MultiFrameNR ')

                mode = val[:mode_len-1]
                val = val[mode_len:]

            if val.lower() == 'auto':
                val = PROPcodes.SONY_ISO_AUTO
            else:
                val = int(val)

        ISOval = str(bin(val)[2:])
        
        if len(ISOval) < 24:
            ISOval = (
                '0' * (
                    24
                    - len(ISOval)
                    )
                + ISOval
                )
        
        if isinstance(mode, str):
            ISOmode = str(bin(PROPcodes.SONY_ISO_MODE['Values'][mode])[2:])
        elif isinstance(mode, int):
            ISOmode = str(bin(mode)[2:])

        if len(ISOmode) < 4:
            ISOmode = (
                '0' * (
                    4
                    - len(ISOmode)
                    )
                + ISOmode
                )

        ISOext = str(bin(ext)[2:])

        if len(ISOext) < 4:
            ISOext = (
                '0' * (
                    4
                    - len(ISOext)
                    )
                + ISOext
                )

        ISOfinal = ISOext+ISOmode+ISOval

        return int(ISOfinal, 2)
    
    def shutter2bytes(self, val):

        """ Convert a shutter speed value

        This function convert the value of the shutter speed in a
        format that is required as input for a Sony Camera

        Args:
        - val (float): value of the shutter speed

        Return:
        - res (bytes): struct version of the shutter speed
        """

        num, den = decimal.Decimal(str(val)).as_integer_ratio()

        num_bytes = struct.pack(
            self.__endian
            + 'H', num
            )
        
        den_bytes = struct.pack(
            self.__endian
            + 'H', den
            )

        return den_bytes+num_bytes

    def bytes2shutter(self, val):

        tmp = struct.pack(
            self.__endian+'L',
            val
            )

        num = struct.unpack(
            self.__endian
            + 'H', tmp[2:]
            )[0]
        
        den = struct.unpack(
            self.__endian
            + 'H', tmp[:2]
            )[0]
        
        if num >= den:
            return str(num/den)
        else:
            return str(num)+'/'+str(den)

    def expcomp2bytes(self, val):

        """Convert Exposure Compensation to bytes

        Args:
        - val (float): value to be converted

        Returns:
        - res (bytes): encoded value of the compensation
        """

        res = struct.pack(
            self.__endian
            + 'L', int(val*1000)
            )
        
        return res
    
    def bytes2expcomp(self, val):

        """Convert Exposure Compensation to float

        Args:
        - val (bytes): value to be converted

        Returns:
        - res (float): decoded value of the compensation
        """

        if isinstance(val, bytes):
            res = struct.unpack(
                self.__endian
                + 'L', val
                )
        else:
            res = copy.copy(val)
        
        return res/1000.
