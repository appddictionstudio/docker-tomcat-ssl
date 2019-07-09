#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
#
# Authors: Jason Dobies
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

import logging
import os
import sys
import urllib2

LOG = logging.getLogger('choose_repo')

# Instance from one region will be redirected to another region's CDS for content
REDIRECTS = [('us-gov-west-1', 'us-west-2')]

def get_zone():
    try:
        fp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone')
    except urllib2.URLError, e:
        LOG.error("Error getting availability zone from EC2 instance metadata.  "
            "Are you running in EC2?")
        LOG.error(e)
        sys.exit(1)
    zone = fp.read()

    LOG.info('Zone [%s]' % zone)

    # Remove trailing character from the zone, we only care about the region
    # part, such as us-west-1 or us-west-2, not the actual zone.
    zone = zone[:-1]

    # Check for redirects
    for reg, redirect in REDIRECTS:
        if reg == zone:
            LOG.info('Zone %s is being redirected to %s.' % (zone, redirect))
            zone = redirect

    return zone

def enable_repo(zone, repo_suffix):
    repo_file = 'redhat-rhui%s.repo' % repo_suffix

    # Dynamically set the region, leave the word "REGION" so urls look consistent
    # across regions 
    # bz#921116, copy ami to another region

    # Set the region
    #LOG.info('Setting region in %s' % repo_file)
    #cmd = "sed -i 's/REGION/%s/' /etc/yum.repos.d/%s" % (zone, repo_file)
    #LOG.info('Executing [%s]' % cmd)
    #os.system(cmd)

    # Enable the binary repos
    LOG.info('Enabling binary repos in %s' % repo_file)
    lines = open('/etc/yum.repos.d/%s' % repo_file).read().split('\n')
    repo = False
    new_lines = []
    for line in lines:
        if line.startswith('[') and 'source' not in line and 'debug' not in line and 'supplementary' not in line and 'rhscl' not in line and 'extra' not in line and 'optional' not in line:
                repo = True
        if line.startswith('enabled') and repo:
            new_lines.append('enabled=1')
            repo = False
            continue

        new_lines.append(line)

    f = open('/etc/yum.repos.d/%s' % repo_file, 'w')
    f.write('\n'.join(new_lines))
    f.close()
            
    # Enable the RHUI 2.0 load balancer yum plugin
    LOG.info('Enabling load balancer plugin')
    cmd = "sed -i 's/enabled=0/enabled=1/' /etc/yum/pluginconf.d/rhui-lb.conf"
    LOG.info('Executing [%s]' % cmd)
    os.system(cmd)

    # Update the load balancers for the correct region
    LOG.info('Setting region in load balancer config')
    cmd = "sed -i 's/REGION/%s/' /etc/yum.repos.d/rhui-load-balancers.conf" % zone
    LOG.info('Executing [%s]' % cmd)
    os.system(cmd)

    # Enable the client config repo
    LOG.info('Enabling client config repo')
    repo_file = 'redhat-rhui-client-config%s.repo' % repo_suffix
    cmd = "sed -i 's/enabled=0/enabled=1/' /etc/yum.repos.d/%s" % repo_file
    LOG.info('Executing [%s]' % cmd)
    os.system(cmd)

    # Dynamically set the region, leave the word "REGION" so urls look consistent
    # across regions 
    # bz#921116, copy ami to another region
    
    # Set the region
    #LOG.info('Setting region in %s' % repo_file)
    #cmd = "sed -i 's/REGION/%s/' /etc/yum.repos.d/%s" % (zone, repo_file)
    #LOG.info('Executing [%s]' % cmd)
    #os.system(cmd)


def main():

    if len(sys.argv) > 1:
        repo_suffix = sys.argv[1]
    else:
        repo_suffix = ''

    if repo_suffix:
        repo_suffix = '-%s' % repo_suffix

    zone = get_zone()
    enable_repo(zone, repo_suffix)

if __name__ == '__main__':
    formatter = logging.Formatter("[%(levelname)s:%(name)s] %(module)s:%(lineno)d %(asctime)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('/var/log/choose_repo.log')
    file_handler.setFormatter(formatter)

    LOG.addHandler(console_handler)
    LOG.addHandler(file_handler)
    LOG.setLevel(logging.INFO)

    main()
