=====
 mic 
=====

SYNOPSIS
========

| mic [GLOBAL-OPTS] create SUBCOMMAND <ksfile> [OPTION]
| mic [GLOBAL-OPTS] chroot [OPTION] <imgfile>

DESCRIPTION
===========

The tools `mic` is used to create and manipulate images for Linux distributions.
It is composed of two subcommand: `create`, `chroot`.

USAGE
=====

create
------
This command is used to create various images, including loop.

Usage:
 | mic [GLOBAL-OPTS] create(cr) SUBCOMMAND <ksfile> [OPTION]

Subcommands:

 | auto         auto detect image type from magic header
 | fs           create fs image, which is also chroot directory
 | loop         create loop image, including multi-partitions
 | raw          create raw image, containing multi-partitions
 | qcow         create qcow image

Options:

  -h, --help  show the help message
  --logfile=LOGFILE  specify the path of logfile, save the output to logfile LOGFILE
  -c CONFIG, --config=CONFIG  specify configure file for mic, default is /etc/mic/mic.conf
  -k CACHEDIR, --cachedir=CACHEDIR  cache directory used to store the downloaded files and packages
  -o OUTDIR, --outdir=OUTDIR  directory used to locate the output image and files
  -A ARCH, --arch=ARCH  specify repo architecture, genarally mic would detect the architecture, if existed more than one architecture, mic would give hint to you
  --local-pkgs-path=LOCAL_PKGS_PATH  specify the path for local rpm packages, which would be stored your own rpm packages
  --pkgmgr=PKGMGR  specify backend package mananger, currently yum and zypp available
  --record-pkgs=RECORD_PKGS  record the info of installed packages, multiple values can be specified which joined by ",", valid values: "name", "content", "license"
  --pack-to=PACK_TO   pack the images together into the specified achive, extension supported: .zip, .tar, .tar.gz, .tar.bz2, etc. by default, .tar will be used
  --release=RID  generate a release of RID with all necessary files, when @BUILD_ID@ is contained in kickstart file, it will be replaced by RID. sample values: "latest", "tizen_20120101.1"
  --copy-kernel  copy kernel files from image /boot directory to the image output directory
  --runtime=RUNTIME  Specify  runtime mode, avaiable: bootstrap
  --install-pkgs=INSTALL_PKGS  Specify what type of packages to be installed, valid: source, debuginfo, debugsource
  --check-pkgs=CHECK_PKGS  Check if given packages would be installed, packages should be separated by comma
  --tmpfs  Setup tmpdir as tmpfs to accelerate, experimental feature, use it if you have more than 4G memory
  --strict-mode  Abort creation of image, if there are some errors during rpm installation

Options for fs image:
  --include-src  generate a image with source rpms included; to enable it, user should specify the source repo in the ks file

Options for loop image:
  --shrink       whether to shrink loop images to minimal size
  --compress-image=COMPRESS_IMAGE  compress all loop images with 'gz' or 'bz2' or 'lzo'
  --compress-disk-image=COMPRESS_DISK_IMAGE  same with --compress-image

Options for raw image:
  --compress-image=COMPRESS_IMAGE  compress all raw images with 'gz' or 'bz2'
  --compress-disk-image=COMPRESS_DISK_IMAGE  same with --compress-image
  --generate-bmap=GENERATE_BMAP also generate the block map file
  --fstab-entry=FSTAB_ENTRY  Set fstab entry, 'name' means using device names, 'uuid' means using filesystem uuid

Examples:

 | mic create loop tizen.ks
 | mic cr fs tizen.ks --local-pkgs-path=localrpm

chroot
------
This command is used to chroot inside the image, it's a great enhancement of chroot command in linux system.

Usage:

 | mic chroot(ch) <imgfile>

Options:

  -h, --help  show the help message
  -s SAVETO, --saveto=SAVETO  save the unpacked image to specified directory SAVETO

Examples:

 | mic chroot loop.img

Advanced Usage
==============
The advanced usage is just for bootstrap, please skip it if you don't care about it.

The major purpose to use bootstrap is that some important packages (like rpm) are customized
a lot in the repo which you want to create image, and mic must use the customized rpm to
create images, or the images can't be boot. So mic will create a bootstrap using the repo
in the ks file at first, then create the image via chrooting, which can make mic using the
chroot environment with the customized rpm.

Now mic will use bootstrap to create image by default, and to meet your requirement, you can
also change the setting for bootstrap (/etc/mic/bootstrap.conf):

| [main]
| # which distro will be used for creating bootstrap
| distro_name = tizen
| # which dir will be located when creating bootstrap
| rootdir = /var/tmp/mic-bootstrap
| # whether to enable the bootstrap mode
| enable = true
| 
| [tizen] # the supported distro for creating bootstrap
| # which packages will be optional when creating bootstrap for this distro
| optional:
| # which packages will be required when creating bootstrap for this distro
| packages:

KNOWN ISSUES
============
Bug of latest syslinux package
------------------------------
In some new Linux distributions, the "syslinux" package in their official
software repositories is the version 4.04. It will cause segment fault for
a fatal bug, and mic will failed with syslinux installation errors.

The solution is to install the patched "syslinux" package in MeeGo or Tizen's
tools repos, until the official released one being fixed.

Failed to create btrfs image in openSUSE
----------------------------------------
When creating btrfs image in openSUSE, it would hang up with showing image kernel
panic. This issue impact all openSUSE distributions: 12.1, 11.4, 11.3, etc

REPORTING BUGS
==============
The source code is tracked in review.tizen.org:

    https://review.tizen.org/git/tools/mic

The bug is registered in tizen.org:

    https://bugs.tizen.org/jira

Please report issues for bugs or feature requests.
