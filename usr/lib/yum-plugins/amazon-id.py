#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
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

import base64
import urllib2
try:
    import simplejson as json
except:
    import json

from urllib2 import ProxyHandler
from yum.plugins import TYPE_CORE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE,)

ID_DOC_HEADER = "X-RHUI-ID"
ID_SIG_HEADER = "X-RHUI-SIGNATURE"
ID_DOC_URL = "http://169.254.169.254/latest/dynamic/instance-identity/document"
ID_SIG_URL = "http://169.254.169.254/latest/dynamic/instance-identity/signature"

# Instance from one region will be redirected to another region's CDS for content
REDIRECTS = [('us-gov-west-1', 'us-west-2')]

# We do not want to use a proxy to read the Amazon instance metadata, so bypass
# any proxy that might be set, including by http{s}_proxy environment
# variable(s).
proxy_handler = ProxyHandler({})
opener = urllib2.build_opener(proxy_handler)


def init_hook(conduit):
    '''
    Plugin initialization hook. For each RHUI repo, replace yum's representation of the
    repo with a subclass that adds in the necessary headers.
    '''

    # Only process RHUI repos
    repos = conduit.getRepos()
    rhui_repos = repos.findRepos('rhui-*')

    # Retrieve the Amazon metadata
    id_doc = _load_id()
    id_sig = _load_signature()

    if id_doc and id_sig:
        # Encode it so it can be inserted as an HTTP header
        # Signature does not need to be encoded, it already is.
        id_doc = base64.urlsafe_b64encode(id_doc)
        id_sig = base64.urlsafe_b64encode(id_sig)

        # Add the headers to all RHUI repos
        for repo in rhui_repos:
            repo.http_headers[ID_DOC_HEADER] = id_doc
            repo.http_headers[ID_SIG_HEADER] = id_sig


def prereposetup_hook(conduit):
    # Dynamically set the mirrorlist to the appropriate region
    # bz#921116, copy ami to another region
    # Setting repo.mirrorlist causes traceback, setting repo.url instead

    # Only process RHUI repos
    repos = conduit.getRepos()
    rhui_repos = repos.findRepos('rhui-*')

    for repo in rhui_repos:
        original = repo.mirrorlist
        try:
            region_new = json.loads(_load_id())["region"]
            # Check if redirect is necessary
            for reg, redirect in REDIRECTS:
                if reg == region_new.strip():
                     region_new = redirect

            start = original.find(".") + 1
            end = original.find(".", start)
            region_old = original[start:end]
            if region_new != region_old:
                repo.mirrorlist = original.replace(region_old, region_new).encode('ascii')
                conduit.info(5, "mirrorlist: %s" % str(repo.mirrorlist))
        except:
            # We failed to get region name from EC2
            conduit.error(0, "Failed to get region name from EC2")


def _load_id():
    '''
    Loads and returns the Amazon metadata for identifying the instance.

    @rtype: string
    '''
    try:
        fp = opener.open(ID_DOC_URL)
        id_doc = fp.read()
        fp.close()
    except urllib2.URLError:
        return None

    return id_doc


def _load_signature():
    '''
    Loads and returns the signature of hte Amazon identification metadata.

    @rtype: string
    '''
    try:
        fp = opener.open(ID_SIG_URL)
        id_sig = fp.read()
        fp.close()
    except urllib2.URLError:
        return None

    return id_sig
