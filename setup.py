from setuptools import setup, find_packages
import glob
import subprocess

# This is fine as long as that imports nothing else.
from falcon_unzip import __version__

install_requires = [
        "falcon-kit>=1.4.1",
        "pypeflow>=2.3.0",
        "networkx>=1.9.1",
        "pysam>=0.8.4",
        "msgpack",
        "intervaltree",
]

try:
    local_version = '+git.{}'.format(
        subprocess.check_output('git rev-parse HEAD', shell=True, encoding='ascii'))
except Exception:
    local_version = ''

setup(name='falcon_unzip',
      version=__version__ + local_version, # also in '__init_.py'
      description='Falcon unzip',
      author='Jason Chin',
      author_email='jchin@pacificbiosciences.com',
      maintainer='Christopher Dunn',
      maintainer_email='pb.cdunn@gmail.com',
      packages=find_packages(),
      package_dir={'falcon_unzip': 'falcon_unzip/'},
      entry_points={'console_scripts': [
          # We do not really need most of these, but mobs might depend on them.
          'fc_dedup_h_tigs.py=falcon_unzip.mains.dedup_h_tigs:main',
          'fc_get_read_hctg_map.py=falcon_unzip.mains.get_read_hctg_map:main',
          'fc_ovlp_filter_with_phase.py=falcon_unzip.mains.ovlp_filter_with_phase:main',
          'fc_phased_ovlp_to_graph.py=falcon_unzip.mains.phased_ovlp_to_graph:main',
          'fc_phasing_readmap.py=falcon_unzip.mains.phasing_readmap:main',
          'fc_quiver.py=falcon_unzip.mains.start_unzip:main', # alias
          'fc_rr_hctg_track.py=falcon_unzip.mains.rr_hctg_track:main',
          'fc_rr_hctg_track2.py=falcon_unzip.mains.rr_hctg_track:main2',
          'fc_select_reads_from_bam.py=falcon_unzip.mains.select_reads_from_bam:main',  # not used?
          'fc_unzip.py=falcon_unzip.mains.start_unzip:main',
          'fc_unzip_gen_gfa_v1.py=falcon_unzip.mains.unzip_gen_gfa_v1:main',
      ]},
      #scripts = scripts,
      zip_safe=True,
      install_requires=install_requires
      )
