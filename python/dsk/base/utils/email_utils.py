# simple email from python utilities

from dsk.base.resources import browser_default as initDefault
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.msg_utils import MsgUtils as log


def send_mail(sendFrom,
              sendTo,
              subject,
              text,
              files=[],
              sendCc=[],
              sendBcc=[],
              authName=None,
              authPass=None):
    """
    quick and easy utility function to send email from any system
    via a python interface.
    """

    import mimetypes
    import smtplib
    import os

    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.Utils import formatdate
    from email import Encoders

    import getpass
    assert type(sendTo) == list
    assert type(sendCc) == list
    assert type(sendBcc) == list
    assert type(files) == list

    addressEmailSuffix = initDefault.EMAIL_SUFFIX

    if '@' not in sendFrom:
        sendFrom += addressEmailSuffix

    for i in range(len(sendTo)):
        if '@' not in sendTo[i]:
            sendTo[i] += addressEmailSuffix

    for i in range(len(sendCc)):
        if '@' not in sendCc[i]:
            sendCc[i] += addressEmailSuffix

    for i in range(len(sendBcc)):
        if '@' not in sendBcc[i]:
            sendBcc[i] += addressEmailSuffix

    msg = MIMEMultipart()
    msg['From'] = sendFrom
    msg['To'] = ', '.join(sendTo)
    if len(sendCc) > 0:
        msg['Cc'] = ', '.join(sendCc)
    if len(sendBcc) > 0:
        msg['Bcc'] = ', '.join(sendBcc)
    msg['Date'] = formatdate(localtime=True)
    msg['Realname'] = getpass.getuser()
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    # attach files as mime parts
    for f in files:
        if DiskUtils.is_file_exist(f):
            ftxt = f.replace(".log", ".txt")
            mimeType = mimetypes.guess_type(ftxt)[0]
            mimeTuple = ('application', 'octet-stream')

            if mimeType is not None:
                mimeTuple = tuple(mimeType.split('/'))
                part = MIMEBase(mimeTuple[0], mimeTuple[1])
                part.set_payload(open(f, "rb").read())
                Encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    'attachment; filename="%s"' % os.path.basename(f))
                msg.attach(part)

    log.debug("sending email from %s to %s" % (sendFrom, sendTo))

    smtp = smtplib.SMTP(initDefault.SERVER_EMAIL_NAME)
    if authName is not None and authPass is not None:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(authName, authPass)
    smtp.sendmail(sendFrom, sendTo + sendCc + sendBcc, msg.as_string())
    smtp.close()


def _test():
    """ testing function to make sure the module is working correctly
    send an email to the person running the test
    """
    import getpass
    _emailAddress = '%s%s' % (getpass.getuser(), initDefault.EMAIL_SUFFIX)
    _msg = '''This test email was generated automatically.
    It is the result of running the EmailUtils module in
    stand-alone mode with the -test flag passed to it.'''

    try:
        send_mail(
            _emailAddress,
            [_emailAddress],
            'test email sent to myself',
            _msg)
    except Exception as e:
        print('Failure in emailUtil test message:')
        print(e.__str__())
        return 1
    return 0


if __name__ == '__main__':
    import sys
    if '-test' in sys.argv:
        sys.exit(_test())

    sys.exit(0)
