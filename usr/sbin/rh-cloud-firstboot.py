#!/usr/bin/python2
#
# Mike McCune <mmccune@redhat.com
#
# Copyright 2010 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use, modify,
# copy, or redistribute it subject to the terms and conditions of the GNU
# General Public License v.2.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.  Any Red Hat
# trademarks that are incorporated in the source code or documentation are not
# subject to the GNU General Public License and may only be used or replicated
# with the express permission of Red Hat, Inc. 
#
# Based off firstboot script and adapted for a cloud specific use case

import os, string, sys

def writeSysconfigFile():
    fd = open("/etc/sysconfig/rh-cloud-firstboot", "w")
    fd.write("RUN_FIRSTBOOT=NO\n")
    fd.close()

if __name__ == "__main__":
    
    # Auto import GPG keys
    release_key = "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
    aux_key = "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-auxiliary"

    code1 = os.system("rpm --import %s" % release_key)

    # Auxiliary key is not packaged separately on RHEL 6.
    if os.path.exists(aux_key):
        code2 = os.system("rpm --import %s" % aux_key)
    else:
        code2 = 0

    if (code1 != 0 or code2 != 0):
        raise Exception("redhat keys not auto-imported!")
        
    writeSysconfigFile()

    os._exit(0)
