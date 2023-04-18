PTP_PROPCODE = {
    'DataType'  : 'L',
    'Values'    : {
        'Undefined'                         : 0x5000,
        'BatteryLevel'                      : 0x5001,
        'FunctionalMode'                    : 0x5002,
        'ImageSize'                         : 0x5003,
        'CompressionSetting'                : 0x5004,
        'WhiteBalance'                      : 0x5005,
        'RGBGain'                           : 0x5006,
        'FNumber'                           : 0x5007,
        'FocalLength'                       : 0x5008,
        'FocusDistance'                     : 0x5009,
        'FocusMode'                         : 0x500A,
        'ExposureMeteringMode'              : 0x500B,
        'FlashMode'                         : 0x500C,
        'ExposureTime'                      : 0x500D,
        'ExposureProgramMode'               : 0x500E,
        'ExposureIndex'                     : 0x500F,
        'ExposureBiasCompensation'          : 0x5010,
        'DateTime'                          : 0x5011,
        'CaptureDelay'                      : 0x5012,
        'StillCaptureMode'                  : 0x5013,
        'Contrast'                          : 0x5014,
        'Sharpness'                         : 0x5015,
        'DigitalZoom'                       : 0x5016,
        'EffectMode'                        : 0x5017,
        'BurstNumber'                       : 0x5018,
        'BurstInterval'                     : 0x5019,
        'TimelapseNumber'                   : 0x501A,
        'TimelapseInterval'                 : 0x501B,
        'FocusMeteringMode'                 : 0x501C,
        'UploadURL'                         : 0x501D,
        'Artist'                            : 0x501E,
        'CopyrightInfo'                     : 0x501F,
    }
}

SONY_PROPCODE = {
    'Values' : {
        'DPCCompensation'                   : 0xD200,
        'DRangeOptimizer'                   : 0xD201,
        'SonyImageSize'                     : 0xD203,
        'ShutterSpeed'                      : 0xD20D,
        'ColorTemp'                         : 0xD20F,
        'CCFilter'                          : 0xD210,
        'AspectRatio'                       : 0xD211,
        'FocusFound'                        : 0xD213,
        'ObjectInMemory'                    : 0xD215,
        'ExposeIndex'                       : 0xD216,
        'SonyBatteryLevel'                  : 0xD218,
        'PictureEffect'                     : 0xD21B,
        'ABFilter'                          : 0xD21C,
        'ISO'                               : 0xD21E,
        'AutoFocus'                         : 0xD2C1,
        'Capture'                           : 0xD2C2,
        'Movie'                             : 0xD2C8,
        'StillImage'                        : 0xD2C7,
        'ManualFocusMode'                   : 0xD2D2,
        'FocusDistance'                     : 0xD2D1,
        'FileFormat'                        : 0xD253,
        'MovieFormat'                       : 0xD241,
        'MovieSetting'                      : 0xD242,
        'DateTime'                          : 0xD223,
        'ManualFocusDistance'               : 0xD24C
        }
}

PROPCODES = [PTP_PROPCODE, SONY_PROPCODE]

### Here are defined the dictionaries
### with the values for each of the Sony
### property decoded

SONY_ISO_AUTO = 0xffffff

SONY_ISO_MODE = {
    'Values' : {
        'Normal': 0,
        'MultiFrameNR' : 1,
        'MultiFrameNR_High' : 2,
    }
}

SONY_PICTURE_EFFECT = {
    'DataType' : 'L',
    'Values' :{
        'PictureEffect_Off'                         : 0x00008000,
        'PictureEffect_ToyCameraNormal'             : 0x00008001,
        'PictureEffect_ToyCameraCool'               : 0x00008002,
        'PictureEffect_ToyCameraWarm'               : 0x00008003,
        'PictureEffect_ToyCameraGreen'              : 0x00008004,
        'PictureEffect_ToyCameraMagenta'            : 0x00008005,

        'PictureEffect_Pop'                         : 0x00008010,
        'PictureEffect_PosterizationBW'             : 0x00008020,
        'PictureEffect_PosterizationColor'          : 0x00008021,

        'PictureEffect_Retro'                       : 0x00008030,
        'PictureEffect_SoftHighkey'                 : 0x00008040,
        'PictureEffect_PartColorRed'                : 0x00008050,
        'PictureEffect_PartColorGreen'              : 0x00008051,
        'PictureEffect_PartColorBlue'               : 0x00008052,
        'PictureEffect_PartColorYellow'             : 0x00008053,

        'PictureEffect_HighContrastMonochrome'      : 0x00008060,
        'PictureEffect_SoftFocusLow'                : 0x00008070,
        'PictureEffect_SoftFocusMid'                : 0x00008071,
        'PictureEffect_SoftFocusHigh'               : 0x00008072,
        'PictureEffect_HDRPaintingLow'              : 0x00008080,
        'PictureEffect_HDRPaintingMid'              : 0x00008081,
        'PictureEffect_HDRPaintingHigh'             : 0x00008082,
        'PictureEffect_RichToneMonochrome'          : 0x00008091,
        'PictureEffect_MiniatureAuto'               : 0x000080A0,
        'PictureEffect_MiniatureTop'                : 0x000080A1,
        'PictureEffect_MiniatureMidHorizontal'      : 0x000080A2,
        'PictureEffect_MiniatureBottom'             : 0x000080A3,
        'PictureEffect_MiniatureLeft'               : 0x000080A4,
        'PictureEffect_MiniatureMidVertical'        : 0x000080A5,
        'PictureEffect_MiniatureRight'              : 0x000080A6,
        'PictureEffect_MiniatureWaterColor'         : 0x000080B0,
        'PictureEffect_MiniatureIllustrationLow'    : 0x000080C0,
        'PictureEffect_MiniatureIllustrationMid'    : 0x000080C1,
        'PictureEffect_MiniatureIllustrationHigh'   : 0x000080C2,
    }
}

SONY_DRIVE_MODE = {
    'DataType': 'L',
    'Values' : {
        'Drive_Single'					                : 0x00000001,
        'Drive_Continuous_Hi'				            : 0x00000002,
        'Drive_Continuous_Hi_Plus'                      : 0x00018010,
        'Drive_Continuous_Hi_Live'                      : 0x00018011,
        'Drive_Continuous_Lo'                           : 0x00018012,
        'Drive_Continuous'                              : 0x00018013,
        'Drive_Continuous_SpeedPriority'                : 0x00018014,
        'Drive_Continuous_Mid'                          : 0x00018015,
        'Drive_Continuous_Mid_Live'                     : 0x00018016,
        'Drive_Continuous_Lo_Live'                      : 0x00018017,
        'Drive_SingleBurstShooting_lo'		            : 0x00018001,
        'Drive_SingleBurstShooting_mid'                 : 0x00018002,
        'Drive_SingleBurstShooting_hi'                  : 0x00018003,
        'Drive_FocusBracket'					        : 0x00018001,
        'Drive_Timelapse'				                : 0x00028001,
        'Drive_Timer_2s'				                : 0x00038005,
        'Drive_Timer_5s'                                : 0x00038003,
        'Drive_Timer_10s'                               : 0x00038004,
        'Drive_Continuous_Bracket_03Ev_3pics'           : 0x00048337,
        'Drive_Continuous_Bracket_03Ev_5pics'           : 0x00048537,
        'Drive_Continuous_Bracket_03Ev_9pics'           : 0x00048937,
        'Drive_Continuous_Bracket_05Ev_3pics'           : 0x00048357,
        'Drive_Continuous_Bracket_05Ev_5pics'           : 0x00048557,
        'Drive_Continuous_Bracket_05Ev_9pics'           : 0x00048957,
        'Drive_Continuous_Bracket_07Ev_3pics'           : 0x00048377,
        'Drive_Continuous_Bracket_07Ev_5pics'           : 0x00048577,
        'Drive_Continuous_Bracket_07Ev_9pics'           : 0x00048977,
        'Drive_Continuous_Bracket_10Ev_3pics'           : 0x00048311,
        'Drive_Continuous_Bracket_10Ev_5pics'           : 0x00048511,
        'Drive_Continuous_Bracket_10Ev_9pics'           : 0x00048911,
        'Drive_Continuous_Bracket_20Ev_3pics'           : 0x00048321,
        'Drive_Continuous_Bracket_20Ev_5pics'           : 0x00048521,
        'Drive_Continuous_Bracket_30Ev_3pics'           : 0x00048331,
        'Drive_Continuous_Bracket_30Ev_5pics'           : 0x00048531,
        'Drive_Continuous_Bracket_03Ev_7pics'           : 0x00048737,
        'Drive_Continuous_Bracket_05Ev_7pics'           : 0x00048757,
        'Drive_Continuous_Bracket_07Ev_7pics'           : 0x00048777,
        'Drive_Continuous_Bracket_10Ev_7pics'           : 0x00048711,


        'Drive_Single_Bracket_03Ev_3pics'		        : 0x00058336,
        'Drive_Single_Bracket_03Ev_5pics'               : 0x00058536,
        'Drive_Single_Bracket_03Ev_9pics'               : 0x00058936,
        'Drive_Single_Bracket_05Ev_3pics'               : 0x00058356,
        'Drive_Single_Bracket_05Ev_5pics'               : 0x00058556,
        'Drive_Single_Bracket_05Ev_9pics'               : 0x00058956,
        'Drive_Single_Bracket_07Ev_3pics'               : 0x00058376,
        'Drive_Single_Bracket_07Ev_5pics'               : 0x00058576,
        'Drive_Single_Bracket_07Ev_9pics'               : 0x00058976,
        'Drive_Single_Bracket_10Ev_3pics'               : 0x00058310,
        'Drive_Single_Bracket_10Ev_5pics'               : 0x00058510,
        'Drive_Single_Bracket_10Ev_9pics'               : 0x00058910,
        'Drive_Single_Bracket_20Ev_3pics'               : 0x00058320,
        'Drive_Single_Bracket_20Ev_5pics'               : 0x00058520,
        'Drive_Single_Bracket_30Ev_3pics'               : 0x00058330,
        'Drive_Single_Bracket_30Ev_5pics'               : 0x00058530,

        'Drive_Single_Bracket_03Ev_7pics'               : 0x00058736,
        'Drive_Single_Bracket_05Ev_7pics'               : 0x00058756,
        'Drive_Single_Bracket_07Ev_7pics'               : 0x00058776,
        'Drive_Single_Bracket_10Ev_7pics'               : 0x00058710,

        'Drive_WB_Bracket_Lo'                           : 0x00068018,
        'Drive_WB_Bracket_Hi'                           : 0x00068028,
        'Drive_DRO_Bracket_Lo'                          : 0x00078019,
        'Drive_DRO_Bracket_Hi'                          : 0x00078029,
        'Drive_Continuous_Timer_2s_3pics'               : 0x0008800E,
        'Drive_Continuous_Timer_2s_5pics'               : 0x0008800F,
        'Drive_Continuous_Timer_5s_3pics'               : 0x0008800C,
        'Drive_Continuous_Timer_5s_5pics'               : 0x0008800D,
        'Drive_Continuous_Timer_10s_3pics'              : 0x00088008,
        'Drive_Continuous_Timer_10s_5pics'              : 0x00088009,
        'Drive_LPF_Bracket'                             : 0x10008001,
        'Drive_RemoteCommander'                         : 0x10008002,
        'Drive_MirrorUp'                                : 0x10008003,
        'Drive_SelfPortrait_1'                          : 0x10008004,
        'Drive_SelfPortrait_2'                          : 0x10008005,
    }
}

SONY_DRANGE_OPTIMIZER = {
    'DataType' : 'L',
    'Values' : {
        'DRangeOptimizer_Off'                   : 0x0000,
        'DRangeOptimizer_On'                    : 0x0001,
        'DRangeOptimizer_Plus'                  : 0x0010,
        'DRangeOptimizer_Plus_Manual_1'         : 0x0011,
        'DRangeOptimizer_Plus_Manual_2'         : 0x0012,
        'DRangeOptimizer_Plus_Manual_3'         : 0x0013,
        'DRangeOptimizer_Plus_Manual_4'         : 0x0014,
        'DRangeOptimizer_Plus_Manual_5'         : 0x0015,
        'DRangeOptimizer_Auto'				    : 0x0020,
        'DRangeOptimizer_HDR_Auto'			    : 0x0030,
        'DRangeOptimizer_HDR_10Ev'              : 0x0031,
        'DRangeOptimizer_HDR_20Ev'              : 0x0032,
        'DRangeOptimizer_HDR_30Ev'              : 0x0033,
        'DRangeOptimizer_HDR_40Ev'              : 0x0034,
        'DRangeOptimizer_HDR_50Ev'              : 0x0035,
        'DRangeOptimizer_HDR_60Ev'              : 0x0036,
    }
}

SONY_EXPOSURE_METERING_MODE = {
    'DataType': 'L',
    'Values' : {
        'Metering_Average'                      : 0x0001,
        'Metering_CenterWeightedAverage'        : 0x0002,
        'Metering_MultiSpot'                    : 0x0003,
        'Metering_CenterSpot'                   : 0x0004,
        'Metering_Multi'                        : 0x0005,
        'Metering_CenterWeighted'               : 0x0006,
        'Metering_EntireScreenAverage'          : 0x0007,
        'Metering_Spot_Standard'                : 0x0008,
        'Metering_Spot_Large'                   : 0x0009,
        'Metering_HighLightWeighted'            : 0x000A,
    }
}

SONY_WHITE_BALANCE = {
    'DataType': 'L',
    'Values': {
        'WhiteBalance_AWB'                      : 0x0002,
        'WhiteBalance_Underwater_Auto'          : 0x8030,
        'WhiteBalance_Daylight'                 : 0x0004,
        'WhiteBalance_Shadow'                   : 0x8011,
        'WhiteBalance_Cloudy'                   : 0x8010,
        'WhiteBalance_Tungsten'                 : 0x0006,
        'WhiteBalance_Fluorescent'		        : 0x0020,
        'WhiteBalance_Fluorescent_WarmWhite'    : 0x8001,
        'WhiteBalance_Fluorescent_CoolWhite'    : 0x8002,
        'WhiteBalance_Fluorescent_DayWhite'     : 0x8003,
        'WhiteBalance_Fluorescent_Daylight'     : 0x8004,
        'WhiteBalance_Flash	'                   : 0x0007,
        'WhiteBalance_ColorTemp'                : 0x8012,
        'WhiteBalance_Custom_1'                 : 0x8020,
        'WhiteBalance_Custom_2'                 : 0x8021,
        'WhiteBalance_Custom_3'                 : 0x8022,
        'WhiteBalance_Custom'                   : 0x0104
    }
}

SONY_MOVIE_FORMAT = {
    'DataType': 'H',
    'Values': {
        'AVCHD'                 :0x0000,
        'MP4'                   :0x0001,
        'XAVC_S_4K'             :0x0002,
        'XAVC_S_HD'             :0x0003,
        'XAVC_HS_8K'            :0x0004,
        'XAVC_HS_4K'            :0x0005,
        'XAVC_S_L_4K'           :0x0006,
        'XAVC_S_L_HD'           :0x0007,
        'XAVC_S_I_4K'           :0x0008,
        'XAVC_S_I_HD'           :0x0009,
        'XAVC_I'                :0x000A,
        'XAVC_L'                :0x000B
    }
}

SONY_EXPMODE = {
    'DataType' : 'L',
    'Values' : {
        'Photo_M'                 : 0x00000001,
        'Photo_P'                 : 0x00010002,
        'Photo_Auto'              : 0x00048000,
        'Photo_AutoPlus'          : 0x00048001,
        'MovieP'                  : 0x00078050,
        'MovieM'                  : 0x00078053,
        'MovieA'                  : 0x00078054,
        'HiFrameRate_P'           : 0x00088080,
        'HiFrameRate_M'           : 0x00088083,
        }
    }

SONY_MOVIE_SETTINGS = {
    'DataType': 'L',
    'Values': {
        '60p_50M'                           : 0x0001,
        '30p_50M'                           : 0x0002,
        '24p_50M'                           : 0x0003,
        '50p_50M'                           : 0x0004,
        '25p_50M'                           : 0x0005,
        '60i_24M'                           : 0x0006,
        '50i_24M_FX'                        : 0x0007,
        '60i_17M_FH'                        : 0x0008,
        '50i_17M_FH'                        : 0x0009,
        '60p_28M_PS'                        : 0x000A,
        '50p_28M_PS'                        : 0x000B,
        '24p_24M_FX'                        : 0x000C,
        '25p_24M_FX'                        : 0x000D,
        '24p_17M_FH'                        : 0x000E,
        '25p_17M_FH'                        : 0x000F,
        '120p_50M_1280x720'                 : 0x0010,
        '100p_50M_1280x720'                 : 0x0011,
        '1920x1080_30p_16M'                 : 0x0012,
        '1920x1080_25p_16M'                 : 0x0013,
        '1280x720_30p_6M'                   : 0x0014,
        '1280x720_25p_6M'                   : 0x0015,
        '1920x1080_60p_28M'                 : 0x0016,
        '1920x1080_50p_28M'                 : 0x0017,
        '60p_25M_XAVC_S_HD'                 : 0x0018,
        '50p_25M_XAVC_S_HD'                 : 0x0019,
        '30p_16M_XAVC_S_HD'                 : 0x001A,
        '25p_16M_XAVC_S_HD'                 : 0x001B,
        '120p_100M_1920x1080_XAVC_S_HD'     : 0x001C,
        '100p_100M_1920x1080_XAVC_S_HD'     : 0x001D,
        '120p_60M_1920x1080_XAVC_S_HD'      : 0x001E,
        '100p_60M_1920x1080_XAVC_S_HD'      : 0x001F,
        '30p_100M_XAVC_S_4K'                : 0x0020,
        '25p_100M_XAVC_S_4K'                : 0x0021,
        '24p_100M_XAVC_S_4K'                : 0x0022,
        '30p_60M_XAVC_S_4K'                 : 0x0023,
        '25p_60M_XAVC_S_4K'                 : 0x0024,
        '24p_60M_XAVC_S_4K'                 : 0x0025,
        '600M_422_10bit'                    : 0x0026,
        '500M_422_10bit'                    : 0x0027,
        '400M_420_10bit'                    : 0x0028,
        '300M_422_10bit'                    : 0x0029,
        '280M_422_10bit'                    : 0x002A,
        '250M_422_10bit'                    : 0x002B,
        '240M_422_10bit'                    : 0x002C,
        '222M_422_10bit'                    : 0x002D,
        '200M_422_10bit'                    : 0x002E,
        '200M_420_10bit'                    : 0x002F,
        '200M_420_8bit'                     : 0x0030,
        '185M_422_10bit'                    : 0x0031,
        '150M_420_10bit'                    : 0x0032,
        '150M_420_8bit'                     : 0x0033,
        '140M_422_10bit'                    : 0x0034,
        '111M_422_10bit'                    : 0x0035,
        '100M_422_10bit'                    : 0x0036,
        '100M_420_10bit'                    : 0x0037,
        '100M_420_8bit'                     : 0x0038,
        '93M_422_10bit'                     : 0x0039,
        '89M_422_10bit'                     : 0x003A,
        '75M_420_10bit'                     : 0x003B,
        '60M_420_8bit'                      : 0x003C,
        '50M_422_10bit'                     : 0x003D,
        '50M_420_10bit'                     : 0x003E,
        '50M_420_8bit'                      : 0x003F,
        '45M_420_10bit'                     : 0x0040,
        '30M_420_10bit'                     : 0x0041,
        '25M_420_8bit'                      : 0x0042,
        '16M_420_8bit'                      : 0x0043,
        '520M_422_10bit'                    : 0x0044,
        '260M_422_10bit'                    : 0x0045,
    }
}

SONY_FOCUS_MODE = {
    'DataType' : 'H',
    'Values' : {
        'MF'            : 0x0001,
        'AF_S'          : 0x0002
    }
}

SONY_PROPVALUES = {
    'ExposureProgramMode'       : SONY_EXPMODE,
    'MovieSetting'              : SONY_MOVIE_SETTINGS,
    'MovieFormat'               : SONY_MOVIE_FORMAT,
    'WhiteBalance'              : SONY_WHITE_BALANCE,
    'ExposureMeteringMode'      : SONY_EXPOSURE_METERING_MODE,
    'StillCaptureMode'          : SONY_DRIVE_MODE,
    'DrangeOptimizer'           : SONY_DRANGE_OPTIMIZER,
    'PictureEffect'             : SONY_PICTURE_EFFECT,
    'FocusMode'                 : SONY_FOCUS_MODE
}
