import re
import smtplib

def validate_password(password):
    if 8 <= len(password) <= 24:
        if re.search('[a-z]', password) and re.search('[A-Z]', password):
            if re.search('[0-9]', password):
                return True
    return False

def send_email(corre_usuario, name_file, new_format):
    connection = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    email_addr = 'mailtotestandes1@gmail.com'
    email_passwd = 'uqpimdgplbxssgay'
    subject = "Archivo convertido exitosamente"
    body = "Su archivo " + name_file +  " ha sido convertido a formato " + new_format
    message = 'Subject: {}\n\n{}'.format(subject, body)
    connection.login(email_addr, email_passwd)
    connection.sendmail(from_addr=email_addr, to_addrs = corre_usuario, msg= message)
    connection.close()