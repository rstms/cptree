cptree
======

Command Line Interface Enhancement for Data Transfer and Verification

Purpose 

cptree is a user interface wrapper for rsync.  It aims to enhance the process of interactive, manual data transfers. It integrates rsync for data transfer, SSH for secure communication, and adds a level of redundancy with post-transfer cryptographic hash verification using the Python hashlib module. Aimed at system administrators and power users, cptree simplifies file synchronization tasks by offering an improved user interface for progress monitoring and integrity checks.


Core Functionality

 - Progress Visualization: Features a consolidated progress bar for the entirety of the directory transfer, displaying essential metrics such as transfer speed, elapsed time, and the estimated time to completion. This is particularly beneficial for lengthy transfers, providing a comprehensive overview at a glance.


 - Cryptographic Verification: Employs the Python hashlib module for cryptographic hashing, alongside hashtree, a companion tool for generating hash digest files. This facilitates automated post-transfer integrity checks between the source and destination directories, ensuring the accuracy and security of the transferred data.


Technical Details

cptree leverages existing technologies (rsync and SSH) for its foundational operations, focusing on augmenting the user experience with additional functionalities. The use of Python’s hashlib for cryptographic operations and the introduction of hashtree for hash digest generation are pivotal in automating the verification process, making cptree a comprehensive tool for data transfer and integrity assurance.


Installation

Implemented as pure Python modules, cptree and hashtree are easily installed via pip. This installation approach facilitates quick integration into existing workflows, with more detailed installation instructions provided in a separate section.


Application and Usage

Designed for scenarios that require detailed progress tracking and stringent data integrity verification, cptree is particularly valuable for manual transfers of large datasets. Its intuitive interface and verification capabilities make it an indispensable tool for tasks that demand high levels of oversight and security.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme 
   cli 
   installation
   modules

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
