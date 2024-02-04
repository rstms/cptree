
cptree
======

rsync interface adding total transfer progress and redundant cryptographic hash verification


.. image:: https://img.shields.io/github/license/rstms/cptree
   :target: https://img.shields.io/github/license/rstms/cptree
   :alt: Image


.. image:: https://img.shields.io/pypi/v/cptree.svg
   :target: https://img.shields.io/pypi/v/cptree.svg
   :alt: Image



* Free software: MIT license

.. code-block::

   Usage: cptree [OPTIONS] SRC DST

     rsync transfer with progress indicator and checksum verification

   Options:
     --version                       Show the version and exit.
     -d, --debug                     debug mode
     --shell-completion TEXT         configure shell completion
     -c, --create [ask|force|never]  create DST if nonexistent
     -D, --delete [ask|force|never|force-no-countdown]
                                     delete DST contents before transfer
     -p, --progress [enable|ascii|none]
                                     animated transfer progress
     -o, --output DIRECTORY          checksum output dir
     -h, --hash [sha3_512|blake2s|sha3_256|md5|sha256|sha512|sha3_384|sha384|sha3_224|blake2b|sha224|sha1|none]
                                     select checksum hash
     -r, --rsync / -R, --no-rsync    enable/disable rsync transfer
     -r, --rsync / -R, --no-rsync    enable/disable rsync transfer
     -a, --rsync-args TEXT           rsync pass-through arguments
     --help                          Show this message and exit.

.. code-block::

   Usage: cptree [OPTIONS] SRC DST

     rsync transfer with progress indicator and checksum verification

   Options:
     --version                       Show the version and exit.
     -d, --debug                     debug mode
     --shell-completion TEXT         configure shell completion
     -c, --create [ask|force|never]  create destination directory if nonexistent
     -D, --delete [ask|force|never|force-no-countdown]
                                     delete destination directory before transfer
     -p, --progress [enable|ascii|none]
                                     total transfer progress
     -o, --output DIRECTORY          checksum output dir
     -h, --hash [md5|sha1|sha256|sha512|none]
                                     select checksum hash
     -r, --rsync / -R, --no-rsync    enable/disable rsync transfer
     -a, --rsync-args TEXT           rsync pass-through arguments
     --help                          Show this message and exit.
