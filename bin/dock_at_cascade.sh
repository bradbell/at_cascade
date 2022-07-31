#! /bin/bash -e
# -----------------------------------------------------------------------------
# at_cascade: Cascading Dismod_at Analysis From Parent To Child Regions
#           Copyright (C) 2021-22 University of Washington
#              (Bradley M. Bell bradbell@uw.edu)
#
# This program is distributed under the terms of the
#     GNU Affero General Public License version 3.0 or later
# see http://www.gnu.org/licenses/agpl.txt
# -----------------------------------------------------------------------------
driver='podman'
at_cascade_version='2022.4.18'
at_cascade_hash='2c66f70092dcc4d6f0f9b76190b0e4a0fbbcbeef'
# -----------------------------------------------------------------------------
if [ -e 'Dockerfile' ]
then
    echo 'dock_at_cascade.sh: Error'
    echo 'Must first remove ./DockerFile'
    exit 1
fi
# ---------------------------------------------------------------------------
cat << EOF > Dockerfile
FROM dismod_at.image

# LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=''

# 1. Make sure that that dismod_at is install where expected
RUN if [ ! -e /home/prefix/dismod_at.release ] ; \
then echo 'Cannot find /home/prefix/dismod_at.release' ; exit 1; fi
RUN if [ -e /home/prefix/dismod_at ] ; then rm /home/prefix/dismod_at ; fi && \
ln -s /home/prefix/dismod_at.release /home/prefix/dismod_at

# 2. Get source corresponding to at_cascasde-$at_cascade_version
WORKDIR /home
RUN git clone https://github.com/bradbell/at_cascade.git at_cascade.git
git checkout --quiet $at_cascade_hash && \
grep "$at_cascade_version" doc.xrst

# 3. Run Tests
RUN sed -i bin/check_all.sh -e '/run_sphinx.sh/d' && bin/check_all.sh

# 4. Install at_cascade
RUN python3 -m build && \
pip3 install --force-reinstall dist/at_cascade-$at_cascade_version.tar.gz \
    --prefix=/home/prefix/dismod_at

EOF
# ---------------------------------------------------------------------------
echo 'Creating at_cascade.image'
$driver build --tag at_cascade.image .
# ---------------------------------------------------------------------------
echo 'dock_at_cascade.sh: OK'
exit 0
