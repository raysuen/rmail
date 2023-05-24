######################################
#2.5 修正
#   1 不传参数报错。
#   2 不传邮件内容报错。
#
#3.0 修正
#   1 可以指定发送人，如果不知道发送人，发送用户和发送用户的密码，
#     则使用脚本内部字典设定的发送人，发送用户和发送用户密码
#   2 可以使用-f 指定参数文件，通过参数文件获取邮件参数
######################################


使用方法：
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
	EXAMPLE:
	    rmail.py 123456@mail.com title content
	    rmail.py -f config.ini
	    rmail.py -sm 12345@mail.com -su 12345 -sp 12345 -s smtp.mail.com -r 5678@mail.com -t "mail title" -c "mail content"
	    rmail.py -r 123456@mail.com -t "mail title" -c "mail content"
	    rmail.py -r 123456@mail.com -t "mail title" -c "mail content" -cc "123456@mail.com,789@mail.com"
	    rmail.py -r 123456@mail.com -t "mail title" -c "mail content" -cc "123456@mail.com,789@mail.com" -a "test.txt"
 





