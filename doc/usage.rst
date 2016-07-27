MIC Usage
=========

.. contents:: Table of Contents

Overview
--------
MIC offers three major functions:

- creating an image with different format
- chrooting into an image

Getting help
------------
You can also use `$ mic --help` or `$ mic <subcmd> --help`  to get the help message.

How to get help:

- using 'man'

  * man mic

- using '--help' option

  * mic --help
  * mic create --help
  * mic create loop --help

Image formulation support
-------------------------
- Loop

  * Each loop corresponds to one partition
  * A file system will be created inside the image
  * For a configuration with multiple partitions, which is specified in the kickstartfile, mic will generate multiple loop images
  * And multiple loop images can be packed into a single archive file

- Raw

  * “raw” format means something like hard disk dumping
  * Including partition table and all the partitions
  * The image is bootable directly

- fs

  * “fs” means file-system
  * mic can install all the Tizen files to the specified directory, which can be used directly as chroot env

- qcow


Create
------
- Command line for image creation:

::

  mic [GLOBAL-OPTS] create(cr) SUBCOMMAND <ksfile> [OPTION]


- Sub-commands, to specify image format, include:

::

  auto               auto detect image type from magic header
  fs                 create fs image, which is also a chroot directory
  loop               create loop image, including multi-partitions
  raw                create raw image, containing multi-partitions
  qcow               create qcow image

- <ksfile>:

The kickstart file is a simple text file, containing a list of items about image partition, setup, Bootloader, packages to be installed, etc, each identified by a keyword.

In Tizen, the released image will have a ks file along with image. For example, you can download the ks file from: http://download.tizen.org/releases/weekly/tizen/mobile/latest/images/...

- Options include:

::

   -h, --help          Show this help message and exit
   --logfile=LOGFILE   Path of logfile
   -c CONFIG, --config=CONFIG
                       Specify config file for MIC
   -k CACHEDIR, --cachedir=CACHEDIR
                       Cache directory to store downloaded files
   -o OUTDIR, --outdir=OUTDIR
                       Output directory
   -A ARCH, --arch=ARCH
                       Specify repo architecture
   --release=RID       Generate a release of RID with all necessary files.
                       When @BUILD_ID@ is contained in kickstart file, it
                       will be replaced by RID.
   --record-pkgs=RECORD_PKGS
                       Record the info of installed packages. Multiple values
                       can be specified which joined by ",", valid values:
                       "name", "content", "license".
   --pkgmgr=PKGMGR     Specify backend package manager
   --local-pkgs-path=LOCAL_PKGS_PATH
                       Path for local pkgs(rpms) to be installed
   --pack-to=PACK_TO   Pack the images together into the specified achive,
                       extension supported: .zip, .tar, .tar.gz, .tar.bz2,
                       etc. by default, .tar will be used
   --runtime=RUNTIME_MODE
                       Sets runtime mode, the default is bootstrap mode, valid
                       values: "bootstrap". "bootstrap"  means mic uses one
                       tizen chroot environment to create image.
   --copy-kernel       Copy kernel files from image /boot directory to the
                       image output directory.
   --install-pkgs      INSTALL_PKGS  Specify what type of packages to be 
                       installed, valid: source, debuginfo, debugsource
   --check-pkgs=CHECK_PKGS  
                       Check if given packages would be installed,
                       packages should be separated by comma
   --tmpfs             Setup tmpdir as tmpfs to accelerate, experimental feature,
                       use it if you have more than 4G memory
   --strict-mode       Abort creation of image, if there are some errors 
                       during rpm installation
  
- Other options:

::

   --compress-image=COMPRESS_IMAGE (for loop & raw)
                       Sets the disk image compression. Note: The available
                       values might depend on the used filesystem type.
   --compress-disk-image=COMPRESS_IMAGE
                       Same with --compress-image
   --shrink (for loop)
                       Whether to shrink loop images to minimal size
   --include-src (for fs)
                       Generate a image with source rpms included
   --generate-bmap (for raw)
                       Generate the block map file
   --fstab-entry (for raw)
                       Set fstab entry, 'name' means using device names,
                       'uuid' means using filesystem uuid

- Examples:

::

   mic cr loop tizen.ks

Chroot
------
This command is used to chroot inside the image. It's a great enhancement of the chroot command in the Linux system.

- Usage:

::

   mic chroot(ch) <imgfile>

- Options:

::

   -h, --help          Show this help message and exit
   -s SAVETO, --saveto=SAVETO
                       Save the unpacked image to a specified dir  

- Examples:

::

   mic ch loop.img

Getting Start
-------------

How to create an image
~~~~~~~~~~~~~~~~~~~~~~~

**Prepare kickstart file**

To create an image, you need a proper ks file.
Here's a simple example:
::

  # filename: tizen-min.ks
  lang en_US.UTF-8
  keyboard us
  timezone --utc America/Los_Angeles

  part / --size 1824 --ondisk sda --fstype=ext3

  rootpw tizen
  bootloader  --timeout=0  --append="rootdelay=5"

  desktop --autologinuser=tizen
  user --name tizen  --groups audio,video --password 'tizen'

  repo --name=Tizen-base --baseurl=http://download.tizen.org/snapshots/trunk/latest/repos/base/ia32/packages/
  repo --name=Tizen-main --baseurl=http://download.tizen.org/snapshots/trunk/latest/repos/main/ia32/packages/

  %packages --ignoremissing
   @tizen-bootstrap
  %end

  %post
  rm -rf /var/lib/rpm/__db*
  rpm --rebuilddb
  %end

  %post --nochroot
  %end

The ks file above can be used to create a minimum Tizen image. For other repositories, you can replace with the appropriate repository url. For example:
::

  repo --name=REPO-NAME --baseurl=https://username:passwd@yourrepo.com/ia32/packages/ --save  --ssl_verify=no

**Create an loop image**

To create an image, run MIC in the terminal:
::

 $ sudo mic create loop tizen-min.ks

How to add/remove packages
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specific the packages you plan to install in the '%packages' section in ks file. Packages can be specified by group/pattern or by individual package name. The definition of the groups/pattern can be referred to in the repodata/\*comps.xml or repodata/pattern.xml file at the download server. For example: http://download.tizen.org/snapshots/latest/repos/base/ia32/packages/repodata/_.

The %packages section is required to end with '%end'. Also, multiple '%packages' sections are allowed. Additionally, individual packages may be specified using globs. For example:
::

  %packages
  ...
  @Tizen Core            # add a group named Tizen Core, and all the packages in this group would be added
  e17-*                  # add all the packages with name starting with "e17-"
  kernel                 # add kernel package
  nss-server.armv7hl     # add nss-server with arch armv7hl
  -passwd                # remove the package passwd
  ...
  %end

Use local rpm package
~~~~~~~~~~~~~~~~~~~~~

"How can I install my own rpm into the image, so I can test my package with the image?"
In such a case, using local package path would be very helpful. For example, if your rpm 'hello.rpm' is under directory 'localpath', run MIC like below:

::

    $ sudo mic create loop test.ks --local-pkgs-path=localpath

From the output, MIC will tell you "Marked 'hellop.rpm' as installed", and it will install hello.rpm in the image. Be sure your rpm is not in the repo of ks file and that your rpm's version is newer or equal to the repo rpm version.

How to set proxy
~~~~~~~~~~~~~~~~

**Proxy variable in bash**

It's common to use the proxy variable in bash. In general, you can set the following environment variables to enable proxy support:

::

  export http_proxy=http://proxy.com:port
  export https_proxy=http://proxy.com:port
  export ftp_proxy=http://proxy.com:port
  export no_proxy=localhost,127.0.0.0/8,.company.com

You don't need all the variables. Check what you do need. When your repo url in your ks file starts with 'https', MIC will use https_proxy. Be especially aware of when you set no_proxy (it indicates which domain should be accessed directly). Don't leave blank space in the string.

Because MIC needs sudo privilege, set /etc/sudoers, to keep the proxy environment, and add those proxy variables to "env_keep":

::

   Defaults        env_keep += "http_proxy https_proxy ftp_proxy no_proxy"

Note: Use "visudo" to modify /etc/sudoers

However, if you don't want to change your /etc/sudoers, there is an alternative for you to set the proxy in mic.conf. See the next section.

**Proxy setting in mic.conf**

The proxy environment variables may disturb other program, so if you would like to enable proxy support only for MIC, set the proxy in /etc/mic/mic.conf like this:

::

  [create]
   ; settings for create subcommand
   tmpdir= /var/tmp/mic
   cachedir= /var/tmp/mic/cache
   outdir= .
   pkgmgr = zypp
   proxy = http://proxy.yourcompany.com:8080/
   no_proxy = localhost,127.0.0.0/8,.yourcompany.com

**Proxy setting in ks file**

It's likely that you will need to enable proxy support only for a special repo url, and other things would remain at their existing proxy setting.
Here's how to handle that case:

::

  repo --name=oss --baseurl=http://www.example.com/repos/oss/packages --proxy=http://host:port

What's BootStrap?
~~~~~~~~~~~~~~~~~
When some important packages (like rpm) of the distribution (Tizen) is much different with native environment, the image created by native environment may be not bootable. Then a bootstrap environment will be required to create the image.

To create an image of one distribution (Tizen), MIC will create a bootstrap for this distribution (Tizen) at first, and then create the image by chrooting this bootstrap. This way is called "Bootstrap Mode" for MIC. And from 0.15 on, MIC will use this mode by default.

