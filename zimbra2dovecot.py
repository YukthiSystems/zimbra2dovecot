#!/usr/bin/env python3

from os import path
from json import loads
from tarfile import TarFile
from mailbox import Maildir
from mailbox import MaildirMessage

import sys


# We store the flags of Zimbra as keys and flags of Maildir as values
# https://wiki.zimbra.com/wiki/Message_Flags
flagmap = {
    'f': 'F',
    'r': 'R',
    'w': 'P',
    'd': 'D'
}


def get_msgflags(metadata):
    """Read Zimbra metadata and return Maildir flags"""
    flags = [ flagmap[f] for f in metadata['FlagStr'] if flagmap.get(f) ]
    if not metadata['unread']:
        flags.append('S')
    flags.sort()
    return ''.join(flags)


def get_metadata(tf):
    """Return a dict of metadata for all mails with the filename of the
    mail as the key

    """
    return {k:v for k,v in
            # Build a list of tuples with (mail, metadata)
            map(lambda m: (m['name'].rstrip('.meta'),
                           # Load the JSON inside the metadata files
                           loads(tf.extractfile(m['name']).read().decode())),
                # Keep only the metadata
                filter(lambda m: m['name'].rfind('.meta', -5) >= 0,
                       # Build a list with mails and their metadata
                       [m.get_info() for m in tf.getmembers()]))}


def get_mails(tf):
    """Return a list of dicts with information from all mails in the
    archive

    """
    return filter(lambda m: m['name'].rfind('.eml', -4) >= 0,
                  [m.get_info() for m in tf.getmembers()])


def store_mail(tf, mail, maildir, metadata):
    """Store the given mail inside the maildir with its metadata"""
    # Retrieve the message
    msg = MaildirMessage(tf.extractfile(mail['name']))
    msg.set_flags(get_msgflags(metadata[mail['name']]))
    folder = path.dirname(mail['name'])
    md = Maildir(maildir)
    if not folder == 'Inbox':
        md = Maildir(path.join(maildir, '.' + folder), factory=None)
    md.add(msg)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {} /path/to/zmmailbox.tgz /path/to/dovecot/Maildir".format(sys.argv[0]))
        exit(1)
    with TarFile.gzopen(sys.argv[1]) as tf:
        metadata = get_metadata(tf)
        for m in get_mails(tf):
            print("{}".format(m['name'][:20]))
            store_mail(tf, m, sys.argv[2], metadata)
