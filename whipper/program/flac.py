from subprocess import check_call, CalledProcessError

import logging
logger = logging.getLogger(__name__)


def encode(infile, outfile, level=None):
    """
    Encode infile to outfile, with flac.

    Uses ``-f`` because whipper already creates the file.

    :param level: flac compression level (0-8); ``None`` keeps flac's
                  own default
    :type level: int or None
    """
    cmd = ['flac', '--silent', '--verify']
    if level is not None:
        cmd.append('-%d' % level)
    cmd += ['-o', outfile, '-f', infile]
    try:
        # TODO: Replace with Popen so that we can catch stderr and write it to
        # logging
        check_call(cmd)
    except CalledProcessError:
        logger.exception('flac failed')
        raise
