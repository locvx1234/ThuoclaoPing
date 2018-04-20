import smtplib

from_add = 'poisonous1205@gmail.com'
to_addr_list = ['nguyenvanminhkma@gmail.com']
cc_add_list = []
subject = 'test sent mail'
message = 'minhkma dep trai tu nho'
user = 'poisonous1205@gmail.com'
password = 'minhnguyen'
smtpserver='smtp.gmail.com:587'


class Mail(object):

    def send_email(self, from_add, to_add_list, cc_add_list,
                  subject, message,user, password,
                  smtpserver):

        mes = 'From: {}\nTo: {}\nCc: {}\nSubject: {}\n{}'\
            .format(from_add, ','.join(to_add_list),
                    ','.join(cc_add_list),
                    subject, message)
        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(user, password)
        problems = server.sendmail(from_add, to_add_list, mes)
        server.quit()


mail = Mail()
mail.send_email(from_add, to_addr_list, cc_add_list,
                subject, message, user, password, smtpserver)
