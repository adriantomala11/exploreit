import base64
import six
import uuid
import imghdr
import io
import linecache
import sys

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from exploreit import settings


def send_html_email(to_list, subject, template_name, context, sender=settings.DEFAULT_FROM_EMAIL):
    msg_html = render_to_string(template_name, context)
    msg = EmailMessage(subject=subject, body=msg_html, from_email=sender, bcc=to_list)
    msg.content_subtype = "html"  # Main content is now text/html
    return msg.send()


def get_file_extension(file_name, decoded_file):
    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension
    return extension

def decode_base64_file(data):
    """
    Fuction to convert base 64 to readable IO bytes and auto-generate file name with extension
    :param data: base64 file input
    :return: tuple containing IO bytes file and filename
    """
    # Check if this is a base64 string
    if isinstance(data, six.string_types):
        # Check if the base64 string is in the "data:" format
        if 'data:' in data and ';base64,' in data:
            # Break out the header from the base64 content
            header, data = data.split(';base64,')

        # Try to decode the file. Return validation error if it fails.
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            TypeError('invalid_image')

        # Generate file name:
        file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
        # Get the file name extension:
        file_extension = get_file_extension(file_name, decoded_file)

        complete_file_name = "%s.%s" % (file_name, file_extension,)

        return io.BytesIO(decoded_file), complete_file_name

def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class Payphone():
    TOKEN = '2KAO-HrEN850Og0EenF_JmvaEMik8sOqvR7NmHg1rkAHGwehhWUBvjZxfjKjQPuuURPMkJF6oAaWWn1QqvFKeWIqi40k9ZltU0CWseEFWdoW3rQm3NgEGefZ0m8knZdtcP9wRQFJm5Vhx0PSgIeeh5OhRp5Poa6OsdLFrzPpo6FmYAT5f6Q_MGqwGKN4lRCt04NMCwXW_cS5rYKm994QWlmYzq7WnXX7b4NHqrxOSEF3Xl5Jb-nsRTUVngJmwvA0ue1GtobQyT6ii2-Cql5DzioerrsEr3lgwmQ_Vz3WW3iAxDSFZ8BKH_WjKVV73-pH8oMoaHq3e8NXMvWGoE4OQ4shrNM'
    PREPARE_URL = 'https://pay.payphonetodoesposible.com/api/button/Prepare'