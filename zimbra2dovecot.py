#!/usr/bin/env python3

from os import path
from json import loads
from tarfile import TarFile
from mailbox import Maildir
from mailbox import MaildirMessage

import sys


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


def get_metadata(tf, mailfile):
    """Get the metadata for a given member from the tarfile"""
    return loads(tf.extractfile(mailfile + '.meta').read().decode())


def get_mails(tf):
    return filter(lambda m: m['name'].rfind('.eml', -4) >= 0,
                  [m.get_info() for m in tf.getmembers()])


def store_mail(tf, member):
    md = Maildir(path.join('/tmp/out', path.dirname(member['name'])))
    msg = MaildirMessage(tf.extractfile(member['name']))
    #msg.set_flags(get_msgflags(get_metadata(tf, member['name'])))
    md.add(msg)


if __name__ == '__main__':
    with TarFile.gzopen(sys.argv[1]) as tf:
        for m in get_mails(tf):
            print("{}".format(m['name'][:20]))
            store_mail(tf, m)
