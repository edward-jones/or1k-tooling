#!/bin/bash


basedir=`pwd`

install=${basedir}/install
or1ksim_install=${basedir}/or1ksim-install

gcc_src=${basedir}/or1k-gcc
gcc_testdir=${gcc_src}/gcc/testsuite

or1k_tooling=${basedir}/or1k-tooling


test_blacklist=${or1k_tooling}/test_blacklist


# rename blacklisted gcc tests back
while read line; do
    if [ "x$line" = "x" ] ; then
        continue
    fi
    if [ `echo $line | cut -c 1` = "#" ] ; then
        continue
    fi

    if [ -e "${gcc_testdir}/${line}.notest" ] ; then
        mv -i "${gcc_testdir}/${line}.notest" "${gcc_testdir}/${line}"
    fi
done < ${test_blacklist}
