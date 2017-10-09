import json
import logging
import msgpack
import os
import pprint

try:
    # pylint: disable=no-name-in-module, import-error, fixme, line-too-long
    from pysam.calignmentfile import AlignmentFile
except ImportError:
    # pylint: disable=no-name-in-module, import-error, fixme, line-too-long
    from pysam.libcalignmentfile import AlignmentFile

LOG = logging.getLogger()

def log(*msgs):
    LOG.info(' '.join(repr(m) for m in msgs))

def validate_config(config, fn=None):
    # This simple and quick check catches common problems early.
    # This code might go somewhere else someday.
    LOG.info('From {!r}, config={}'.format(fn, pprint.pformat(config)))
    smrt_bin = config['smrt_bin']
    assert os.path.isdir(smrt_bin), 'Not a directory: smrt_bin={!r}'.format(smrt_bin)
    smrt_bin_cmds = [
        'blasr', 'samtools', 'pbalign', 'variantCaller',
    ]
    smrt_bin_cmds = [os.path.join(smrt_bin, cmd) for cmd in smrt_bin_cmds]
    path_cmds = [
        'nucmer', 'show-coords',
        'fc_rr_hctg_track2.exe',
    ]
    for cmd in smrt_bin_cmds + path_cmds:
        syscall('which ' + cmd)

def mkdirs(*dirnames):
    for dirname in dirnames:
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
            if len(dirnames) == 1:
                log('mkdir -p {!r}'.format(dirnames[0]))

def eng(number):
    return '{:.1f}MB'.format(number / float(2**20))

def read_as_msgpack(stream):
    content = stream.read()
    log('  Read {} as msgpack'.format(eng(len(content))))
    return msgpack.loads(content)

def read_as_json(stream):
    content = stream.read()
    log('  Read {} as json'.format(eng(len(content))))
    return json.loads(content)

def write_as_msgpack(stream, val):
    content = msgpack.dumps(val)
    log('  Serialized to {} as msgpack'.format(eng(len(content))))
    stream.write(content)

def write_as_json(stream, val):
    content = json.dumps(val, indent=2, separators=(',', ': '))
    log('  Serialized to {} as json'.format(eng(len(content))))
    stream.write(content)

def deserialize(fn):
    log('Deserializing from {!r}'.format(fn))
    with open(fn) as ifs:
        log('  Opened for read: {!r}'.format(fn))
        if fn.endswith('.msgpack'):
            val = read_as_msgpack(ifs)
        elif fn.endswith('.json'):
            val = read_as_json(ifs)
        else:
            raise Exception('Unknown extension for {!r}'.format(fn))
    log('  Deserialized {} records'.format(len(val)))
    return val

def serialize(fn, val):
    """Assume dirname exists.
    """
    log('Serializing {} records'.format(len(val)))
    mkdirs(os.path.dirname(fn))
    with open(fn, 'w') as ofs:
        log('  Opened for write: {!r}'.format(fn))
        if fn.endswith('.msgpack'):
            write_as_msgpack(ofs, val)
        elif fn.endswith('.json'):
            write_as_json(ofs, val)
        else:
            raise Exception('Unknown extension for {!r}'.format(fn))

def yield_bam_fn(input_bam_fofn_fn):
    log('Reading BAM names from FOFN {!r}'.format(input_bam_fofn_fn))
    fofn_basedir = os.path.normpath(os.path.dirname(input_bam_fofn_fn))
    def abs_fn(maybe_rel_fn):
        if os.path.isabs(maybe_rel_fn):
            return maybe_rel_fn
        else:
            return os.path.join(fofn_basedir, maybe_rel_fn)
    for row in open(input_bam_fofn_fn):
        yield abs_fn(row.strip())

def yield_abspath_from_fofn(fofn_fn):
    """Yield each filename.
    Relative paths are resolved from the FOFN directory.
    """
    basedir = os.path.dirname(fofn_fn)
    for line in open(fofn_fn):
        fn = line.strip()
        if not os.path.isabs(fn):
            fn = os.path.abspath(os.path.join(basedir, fn))
        yield fn

def syscall(call, nocheck=False):
    """Raise Exception in error, unless nocheck==True
    """
    LOG.info('$(%s)' %repr(call))
    rc = os.system(call)
    msg = 'Call %r returned %d.' % (call, rc)
    if rc:
        LOG.warning(msg)
        if not nocheck:
            raise Exception(msg)
    else:
        LOG.debug(msg)
    return rc

def rm(f):
    syscall('rm -f {}'.format(f))

def touch(f):
    syscall('touch {}'.format(f))

def filesize(fn):
    return os.stat(fn).st_size

def exists_and_not_empty(fn):
    if not os.path.exists(fn):
        return False
    if 0 == filesize(fn):
        LOG.debug('File {} is empty.'.format(fn))
        return False
    return True
