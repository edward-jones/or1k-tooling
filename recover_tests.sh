#!/bin/bash


basedir=`pwd`

gcc_src=${basedir}/or1k-gcc
gcc_testdir=${gcc_src}/gcc/testsuite

for test_name in `find ${gcc_testdir} -name '*.notest'`; do
    new_name=`echo ${test_name} | sed 's/.notest$//'`
    mv -n ${test_name} ${new_name}
done
