import serial
from time import sleep, time
import mraa

# GenImg       = '\x01'
# Img2Tz       = '\x02'
# Match        = '\x03'
# Search       = '\x04'
# RegModel     = '\x05'
# Store        = '\x06'
# LoadChar     = '\x07'
# UpChar       = '\x08'
# DownChar     = '\x09'
# UpImage      = '\x0a'
# DownImage    = '\x0b'
# DeletChar    = '\x0c'
# Empty        = '\x0d'
# SetSysPara   = '\x0e'
# ReadSysPara  = '\x0f'
# SetPwd       = '\x12'
# VfyPwd       = '\x13'
# GetRandomCode= '\x14'
# SetAddr      = '\x15'
# WriteNotepad = '\x18'
# ReadNotepad  = '\x19'
# TemplateNum  = '\x1d'
# ReadConList  = '\x1f'
# OpenLED      = '\x50'
# CloseLED     = '\x51'
# GetImageFree = '\x52'
# GetEcho      = '\x53'
# AutoLogin    = '\x54'
# AutoSearch   = '\x55'
# SearchResBack= '\x56'

confirm_index = 7

confirm_mesg = \
    {
        '\x00':"OK",
        '\x01':"pkg ERROR",
        '\x02':"no finger detected",
        '\x03':"get fingerprint failed",
        '\x06':"fingerprint image is too messy to create feature",
        '\x07':"fingerprint image is OK but feature point is too few to create feature",
        '\x08':"fingerprint mismatch",
        '\x09':"no fingerprint in base",
        '\x0a':"merge feature failed",
        '\x0b':"index to access database out of range",
        '\x0c':"read fingerprint frome database failed",
        '\x0d':"upload feature failed",
        '\x0e':"can not recive more packages",
        '\x0f':"upload image failed",
        '\x10':"delete demo failed",
        '\x11':"clear database failed",
        '\x13':"wrong password",
        '\x15':"no fingerprint resource to create feature",
        '\x18':"flash IO ERROR",
        '\x1a':"invalid reg",
        '\x20':"invalid address",
        '\x21':"confirm password first"
    }

class finger_senser_t(object):
    def __init__(self,addr=['\xff','\xff','\xff','\xff'],pswd=['\x00','\x00','\x00','\x00']):
        self.pkg_head = ('\xef','\x01')
        self.senser_addr  = addr
        self.pkg_pswd = pswd
        self.pkg_flag = ('\x01')
        self.pkg_len  = ('\x00','\x00')
        self.command  = ()
        self.pkg_payload = ()
        self.pkg_chksum = ()
        self.pkg_data = []
        self.recive_data = ""
        self.pswd = pswd
        self.char_buff = '\x01'

        self.confirm_code = '\x00'

        self.s_port = serial.Serial("/dev/ttyMFD1",57600)

    def _gen_chksum(self,command,payload):
        tmp = []
        tmp.extend(self.pkg_flag)
        tmp.extend(chr(self.pkg_len))
        tmp.extend(command)
        tmp.extend(payload)
        sum = 0
        for i in tmp:
            sum += ord(i)
            # print sum

        answer = []
        answer.extend(chr(sum/0x0100))
        answer.extend(chr(sum%0x0100))
        print answer
        return answer

    def _gen_package(self,command,payload):
        self.command = command
        self.pkg_payload = payload
        self.pkg_len = 0x02 + len(self.command) + len(self.pkg_payload)
        self.pkg_chksum = self._gen_chksum(command,payload)

        print self.command
        print self.pkg_payload
        print self.pkg_chksum
        print self.pkg_len

        self.pkg_data = []
        self.pkg_data.extend(self.pkg_head)
        self.pkg_data.extend(self.senser_addr)
        self.pkg_data.extend(self.pkg_flag)
        self.pkg_data.extend(chr(self.pkg_len/0xff))
        self.pkg_data.extend(chr(self.pkg_len%0xff))
        self.pkg_data.extend(self.command)
        self.pkg_data.extend(self.pkg_payload)
        self.pkg_data.extend(self.pkg_chksum)

        print "====package===="
        print self.pkg_data

        pkg_string = ""
        for i in self.pkg_data:
            pkg_string += i

        return pkg_string

    def get_replay_confirm_code(self):
        sleep (1)
        self.recive_data = self.s_port.read_all()
        print "====receive===="
        for i in self.recive_data: 
            print("%x"%(ord(i)))
        print "==============="
        if len(self.recive_data)>9:
            self.confirm_code = self.recive_data[9]
            print confirm_mesg[self.confirm_code]
        else:
            print "***recevie data UNKNOWN ERROR"

    def GenImg(self):
        self.s_port.write(self._gen_package('\x01',[]))

    def Img2Tz(self,buffID):
        self.s_port.write(self._gen_package('\x02',buffID))
        self.get_replay_confirm_code()

    def Match(self):
        self.s_port.write(self._gen_package('\x03',[]))
        self.get_replay_confirm_code()

    def Search(self,index):##1byte:bufferID;2byte:pageID;2byte:count
        self.s_port.write(self._gen_package('\x04',index))
        self.get_replay_confirm_code()

    def RegModel(self):
        self.s_port.write(self._gen_package('\x05',[]))
        self.get_replay_confirm_code()

    def Store(self,index):##1byte:bufferID;2byte:pageID
        self.s_port.write(self._gen_package('\x06',index))
        self.get_replay_confirm_code()

    def LoadChar(self,index):##1byte:bufferID;2byte:pageID
        self.s_port.write(self._gen_package('\x07',index))
        self.get_replay_confirm_code()

    def UpChar(self):
        pass

    def DownChar(self):
        pass

    def UpImage(self):
        pass

    def DownImage(self):
        pass

    def DeletChar(self,index): ##2byte:page;2byte:count
        self.s_port.write(self._gen_package('\x0c',index))
        self.get_replay_confirm_code()

    def Empty(self):
        self.s_port.write(self._gen_package('\x0d',[]))
        self.get_replay_confirm_code()

    def SetSysPara(self,para):
        self.s_port.write(self._gen_package('\x0e',para))
        self.get_replay_confirm_code()

    def ReadSysPara(self):
        self.s_port.write(self._gen_package('\x0f',[]))
        self.get_replay_confirm_code()

    def SetPwd(self,password):
        self.s_port.write(self._gen_package('\x12',password))
        self.get_replay_confirm_code()

    def VfyPwd(self):
        self.s_port.write(self._gen_package('\x13',self.pswd))
        self.get_replay_confirm_code()

    def GetRandomCode(self):
        pass

    def SetAddr(self,address):
        self.s_port.write(self._gen_package('\x15',address))
        self.get_replay_confirm_code()

    def WriteNotepad(self):
        pass

    def ReadNotepad(self):
        pass

    def TemplateNum(self):
        self.s_port.write(self._gen_package('\x1d',[]))
        self.get_replay_confirm_code()

    def ReadConList(self,index):
        self.s_port.write(self._gen_package('\x1f',index))
        self.get_replay_confirm_code()

    def OpenLED(self):
        self.s_port.write(self._gen_package('\x50',[]))
        self.get_replay_confirm_code()

    def CloseLED(self):
        self.s_port.write(self._gen_package('\x51',[]))
        self.get_replay_confirm_code()

    def GetImageFree(self):
        self.s_port.write(self._gen_package('\x52',[]))
        self.get_replay_confirm_code()

    def GetEcho(self):
        self.s_port.write(self._gen_package('\x53',[]))
        self.get_replay_confirm_code()

    def AutoLogin(self,index):
        self.s_port.write(self._gen_package('\x54',['\x36','\x02',index[0],index[1],'\x00']))
        self.get_replay_confirm_code()

    def analyse_search_replay(self):
        ID = self.recive_data[10:12]
        score = self.recive_data[12:14]
        print ID
        print score

    def AutoSearch(self):
        led_r.write(0)
        led_b.write(0)
        self.s_port.write(self._gen_package('\x55',['\x36','\x00','\x00','\x00','\xff']))
        sleep(3.5)
        self.get_replay_confirm_code()
        if self.confirm_code == '\x00':
            self.analyse_search_replay()
            led_b.write(1)
            return True
        led_r.write(1)

    def SearchResBack(self):
        self.s_port.write(self._gen_package('\x56',[self.char_buff,'\x00','\xff','\xff']))
        self.get_replay_confirm_code()

if __name__ == '__main__':
    print "start"
    mysensor = finger_senser_t()
    mysensor.VfyPwd()

    led_r = mraa.Gpio(13)
    led_r.dir(mraa.DIR_OUT)
    led_r.write(0)

    led_b = mraa.Gpio(12)
    led_b.dir(mraa.DIR_OUT)
    led_b.write(0)

    finger_etect = mraa.Gpio(2)
    finger_etect.dir(mraa.DIR_IN)

    while(1):
        if finger_etect.read() == 1:
            mysensor.OpenLED()
            mysensor.AutoSearch()
            # sleep (1)
            # mysensor.CloseLED()
        else:
            sleep(0.1)


