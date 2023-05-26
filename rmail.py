#!/usr/bin/env python3
# _*_coding:utf-8 _*_
# Auth by raysuen
#v3.1

######################################
#2.5 修正
#   1 不传参数报错。
#   2 不传邮件内容报错。

#3.0 修正
#   1 可以指定发送人，如果不知道发送人，发送用户和发送用户的密码，
#     则使用脚本内部字典设定的发送人，发送用户和发送用户密码
#   2 可以使用-f 指定参数文件，通过参数文件获取邮件参数

#3.1 修正
#   1 可以指定ssl连接smtp服务器，
######################################



import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import validators
import re,os,sys
import logging
from configparser import ConfigParser
from ansible_collections.ansible.posix.tests.utils.shippable.check_matrix import fail

class Rsendmail(object):
    DictMailInfo = {
        "sender": None,  # 发件人
        "receiver": None,  # 收件人,多个收件人用逗号分隔
        "Carbon": None,  # CC,抄送接收人，多个接收人使用逗号分隔
        "smtpServer": None,  # SMTP服务器
        "username": None,  # 发送邮箱的用户名和授权码
        "password": None,  # 发送邮箱的密码
        "title": None,  # 邮件主题
        "content": None,  # 邮件内容
        "attachment": None,  # 邮件附件,多个附件以逗号分隔
        "usingssl": False
    }
    def __init__(self, mailto=None, mailfrom=None,mailcc=None, mailsmtp=None, mailuser=None, mailpwd=None, mailtitle=None,mailcontent=None,mailattch=None):
        if mailto != None:
            self.DictMailInfo["receiver"] = mailto
        if mailfrom != None:
            self.DictMailInfo["sender"] = mailfrom
        if mailcc != None:
            self.DictMailInfo["Carbon"] = mailcc
        if mailsmtp != None:
            self.DictMailInfo["smtpServer"] = mailsmtp
        if mailcc != None:
            mailuser.DictMailInfo["username"] = mailuser
        if mailpwd != None:
            self.DictMailInfo["password"] = mailpwd
        if mailtitle != None:
            self.DictMailInfo["title"] = mailtitle
        if mailcontent != None:
            self.DictMailInfo["content"] = mailcontent
        if mailattch != None:
            self.DictMailInfo["attachment"] = mailattch

    #验证字符串中是否存在中文
    def __isChinese(self,word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    #验证邮件地址格式
    def __validatorsmail(self,emails):
        ret = False
        # arrayemails = emails.split(",")
        for i in emails.split(","):
            # print(i)
            if validators.email(i):
                ret = True
                continue
            else:
                ret = False
                break
        return ret

    def __createMailMessage(self):
        if self.DictMailInfo["attachment"] == None:
            # 创建一个实例
            if self.DictMailInfo["content"] != None:
                message = MIMEText(self.DictMailInfo["content"], 'plain', 'utf-8')  # 邮件正文
            else:
                message = MIMEText('', 'plain', 'utf-8')  # 邮件正文
            message['From'] = self.DictMailInfo["sender"]  # 邮件上显示的发件人
            message['To'] = self.DictMailInfo["receiver"]  # 邮件上显示的收件人
            if (self.DictMailInfo["receiver"] != None) and (self.DictMailInfo["Carbon"] != None):  # 判断收件人和抄送人都非空
                if self.__validatorsmail(self.DictMailInfo["Carbon"]) == False:
                    print("The email address of receiver is not a correct format.")
                    exitnum = 61
                    exit(exitnum)
                message["Cc"] = self.DictMailInfo["Carbon"]  # 设置抄送人
                self.DictMailInfo["receiver"] = self.DictMailInfo["receiver"] + ',' + self.DictMailInfo["Carbon"]  # 把所有收件人的地址放在一起
            message['Subject'] = Header(self.DictMailInfo["title"], 'utf-8')  # 邮件主题

        else:
            message = MIMEMultipart()
            message['From'] = self.DictMailInfo["sender"]  # 邮件上显示的发件人
            message['To'] = self.DictMailInfo["receiver"]  # 邮件上显示的收件人
            if (self.DictMailInfo["receiver"] != None) and (self.DictMailInfo["Carbon"] != None):  # 判断收件人和抄送人都非空
                message["Cc"] = self.DictMailInfo["Carbon"]  # 设置抄送人
                self.DictMailInfo["receiver"] = self.DictMailInfo["receiver"] + ',' + self.DictMailInfo["Carbon"]  # 把所有收件人的地址放在一起
            message['Subject'] = Header(self.DictMailInfo["title"], 'utf-8')  # 邮件主题
            if self.DictMailInfo["content"] != None:
                message.attach(MIMEText(self.DictMailInfo["content"], 'plain', 'utf-8'))
            for arr in self.DictMailInfo["attachment"].split(','):
                if os.path.isfile(arr):
                    if self.__isChinese(os.path.basename(os.path.abspath(arr))):
                        att = MIMEText(open(os.path.abspath(arr), "rb").read(), "base64", "utf-8")
                        att["Content-Type"] = "application/octet-stream"
                        att.add_header("Content-Disposition", "attachment",
                                       filename=("gbk", "", os.path.basename(os.path.abspath(arr))))
                    else:
                        att = MIMEText(open(arr, 'rb').read(), 'base64', 'utf-8')
                        att["Content-Type"] = 'application/octet-stream'
                        att["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(
                            os.path.abspath(arr))
                    message.attach(att)
                else:
                    print("The attachment path is incorrect！")
                    exit(20)
        return message


    def send_mail(self,usingssl=False):
        if self.__validatorsmail((self.DictMailInfo["receiver"])) == False:
            print("The email address of receiver is not a correct format.")
            exitnum = 89
            exit(exitnum)
        message = self.__createMailMessage()
        try:
            if usingssl:
                smtp = smtplib.SMTP_SSL(self.DictMailInfo["smtpServer"])
                smtp.connect(self.DictMailInfo["smtpServer"], 465)  # 连接发送邮件的服务器
            else:
                smtp = smtplib.SMTP()  # 创建一个连接
                smtp.connect(self.DictMailInfo["smtpServer"])  # 连接发送邮件的服务器,默认端口25
            smtp.login(self.DictMailInfo["username"], self.DictMailInfo["password"])  # 登录服务器
            smtp.sendmail(self.DictMailInfo["sender"], self.DictMailInfo["receiver"].split(","),
                          message.as_string())  # 填入邮件的相关信息并发送
            print("邮件发送成功！！！")
            smtp.close()
            return True
        except Exception as e:
            print(e)
            print("邮件发送失败！！！")
            return False

#去人配置项大小写，重写函数
class RConfigParser(ConfigParser):
    def __init__(self,defaults=None):
        ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        # return ConfigParser.optionxform(self, optionstr)
        return optionstr

def ReadConfig(rfile,sectionname=None):
    rdict={}
    # rconf = ConfigParser()
    # rconf.optionxform(optionstr)
    rconf = RConfigParser()
    rconf.read(rfile)
    if sectionname == None:
        for i in rconf.sections():
            for j in rconf.options(i):
                rdict[j]=rconf.get(i, j)
    else:
        for j in rconf.options(sectionname):
            rdict[j]=rconf.get(sectionname, j)
    return rdict

def CopyMailDict(fdict,rdict):  #fdict为-f参数指定文件的内容，rdict为邮件类里面的dict
    for i in fdict:

        if fdict[i] != None:
            rdict[i] = fdict[i]

def help_func():
    print("""
        NAME:
            rmail  --send mail
        SYNOPSIS:
            rmail [-f] configfile [section] [-sm] mail address [-su] username [-sp] password [-s] smtpserver [-r] [receiver address] [-t] [mail title] [-c] [mail content] -cc [carbon copy] -a [mail attachment]
        DESCRIPTION:
            
            -sm:    Specify a sanding mail address.
            -su:    Specify a user of smtpserver.
            -sp:    Specify a passworf for user of smtpserver.
            -s:     Specify a smtpserver.
            -f:     Specify a Configuration file to get mail infomation.The second parameter specifies the section name. 
                    If multiple section configuration items exist in the configuration file, 
                    you are advised to specify the section name.
                    When both the command line and the configuration file are specified, 
                    the configuration file takes precedence。
            -r:     Receiver addresses.By default, the first parameter is the recipient。 
                    Multiple recipients are separated by commas。
            -t:     Mail title.By default, the second parameter is the title。 
            -c:     Mail content.By default, the third parameter is the content。 
            -cc:    The addresses of carbon copy.Multiple recipients are separated by commas
            -a:     Mail attachmen.Multiple attachmen are separated by commas
            -ssl:   Using ssl connecting.
        EXAMPLE:
            rmail.py 123456@mail.com title content
            rmail.py -f config.ini
            rmail.py -sm 12345@mail.com -su 12345 -sp 12345 -s smtp.mail.com -r 5678@mail.com -t "mail title" -c "mail content"
            rmail.py -r 123456@mail.com -t "mail title" -c "mail content"
            rmail.py -r 123456@mail.com -t "mail title" -c "mail content" -cc "123456@mail.com,789@mail.com"
            rmail.py -r 123456@mail.com -t "mail title" -c "mail content" -cc "123456@mail.com,789@mail.com" -a "test.txt"
            """)


def GetParameters(Rsmail):
    # print(sys.argv)
    num = 1
    exitnum = 0
    # 获取参数
    if len(sys.argv) > 1:  # 判断是否有参数输入
        while num < len(sys.argv):
            if sys.argv[num] == "-h":
                help_func()  # 执行帮助函数
                exitnum = 0
                exit(exitnum)
            elif sys.argv[num] == "-r":  #指定收件人
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 90
                    print("The parameter must be specified a value,-r.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["receiver"] = sys.argv[num]  #获取收件人
                    num += 1
                else:
                    print("Please specify a valid value for -r.")
                    exitnum = 88
                    exit(exitnum)
            elif sys.argv[num] == "-cc":  #指定抄送人
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 60
                    print("The parameter must be specified a value,-cc.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["Carbon"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -cc.")
                    exitnum = 62
                    exit(exitnum)
            elif sys.argv[num] == "-t":  #指定邮件主题title
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 63
                    print("The parameter must be specified a value,-t.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["title"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -t.")
                    exitnum = 64
                    exit(exitnum)
            elif sys.argv[num] == "-c":  #指定邮件内容
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 65
                    print("The parameter must be specified a value,-c.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["content"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -c.")
                    exitnum = 66
                    exit(exitnum)
            elif sys.argv[num] == "-a":  #指定邮件附件
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 67
                    print("The parameter must be specified a value,-a.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["attachment"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -a.")
                    exitnum = 68
                    exit(exitnum)
            elif sys.argv[num] == "-sm":  #指定发送邮箱名称
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 72
                    print("The parameter must be specified a value,-sm.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["sender"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -sm.")
                    exitnum = 73
                    exit(exitnum)
            elif sys.argv[num] == "-su":  #指定发送邮箱的用户名
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 74
                    print("The parameter must be specified a value,-su.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["username"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -su.")
                    exitnum = 75
                    exit(exitnum)
            elif sys.argv[num] == "-s":  #指定发送邮箱的smtp地址
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 76
                    print("The parameter must be specified a value,-s.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["smtpServer"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -s.")
                    exitnum = 77
                    exit(exitnum)
            elif sys.argv[num] == "-sp":  #指定发送邮箱的用户的密码
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 78
                    print("The parameter must be specified a value,-sp.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    Rsmail.DictMailInfo["password"] = sys.argv[num]
                    num += 1
                else:
                    print("Please specify a valid value for -sp.")
                    exitnum = 79
                    exit(exitnum)
            elif sys.argv[num] == "-f":  #指定配置文件信息
                num += 1  # 下标向右移动一位
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 80
                    print("The parameter must be specified a value,-f.")
                    exit(exitnum)
                elif re.match("^-", sys.argv[num]) == None:  # 判断当前参数是否为-开头，None为非-开头
                    
                    if (num == len(sys.argv)-1) and (re.match("^-", sys.argv[num]) == None):
                        fdict = ReadConfig(sys.argv[num])
                    elif (num == len(sys.argv)-2) and (re.match("^-", sys.argv[num]) == None):
                        fdict = ReadConfig(sys.argv[num],sys.argv[num+1])
                    num += 2
                else:
                    print("Please specify a valid value for -f.")
                    exitnum = 81
                    exit(exitnum)
            
            elif sys.argv[num] == "-ssl":  #指定使用ssl连接smtp服务器
                Rsmail.DictMailInfo["usingssl"] = True
                num += 1
            
            elif (num == 1) and (re.match("^-", sys.argv[num]) == None) :  #判断为第一个参数并且为非-开头的参数，默认为收件人
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 69
                    print("The receiver address must be specified")
                    exit(exitnum)
                else:

                    Rsmail.DictMailInfo["receiver"] = sys.argv[num]  #数据字典内的收件人赋值地址
                    num += 1

            elif (num == 2) and (re.match("^-", sys.argv[num]) == None) :  #判断为第二个参数并且为非-开头的参数，默认为邮件主题
                if num >= len(sys.argv):  # 判断是否存在当前下标的参数
                    exitnum = 71
                    print("The mail title must be specified")
                    exit(exitnum)
                else:
                    Rsmail.DictMailInfo["title"] = sys.argv[num]  #数据字典内的收件人赋值地址
                    num += 1
            elif (num == 3) and (re.match("^-", sys.argv[num]) == None) :  #判断为第二个参数并且为非-开头的参数，默认为邮件内容正文
                Rsmail.DictMailInfo["content"] = sys.argv[num]  # 数据字典内的收件人赋值地址
                num += 1

            else:
                print("Please use -h to get help.")
                exit(1)
                
        if "fdict" in dir():   #判断是否生产配置文件输入的参数字典
            CopyMailDict(fdict,Rsendmail.DictMailInfo)

    else:
        print("Please use -h to get help.")
        exit(2)



if __name__ == "__main__":
    myrmail = Rsendmail()
    GetParameters(myrmail)
    # print(myrmail.DictMailInfo)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d')
    logging.info("开始发送邮件")
    myrmail.send_mail(usingssl=myrmail.DictMailInfo["usingssl"])
    logging.info("结束发送邮件")


