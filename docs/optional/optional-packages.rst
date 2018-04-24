Get the rlease key for the syslog-ng software
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    wget -qO - http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_16.04/Release.key | sudo apt-key add -

Create the syslog-ng repository listing for apt-get
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    echo "deb http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_16.04 ./" | sudo tee -a /etc/apt/sources.list.d/syslog-ng.list

Install syslog-ng software
^^^^^^^^^^^^^^^^^^^^^^^^^^
::
    sudo apt-get update && sudo apt-get install syslog-ng-core