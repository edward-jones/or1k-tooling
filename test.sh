#!/bin/bash


basedir=`pwd`

install=${basedir}/install
or1ksim_install=${basedir}/or1ksim-install

gcc_build=${basedir}/build/gcc
gcc_src=${basedir}/or1k-gcc
gcc_testdir=${gcc_src}/gcc/testsuite

or1k_tooling=${basedir}/or1k-tooling


# $1 is the file of ports to run or1ksim on
if [ -z "$1" ] ; then
    port_file="${or1k_tooling}/or1ksim_ports"
else
    port_file=$1
fi

# $2 is the file of blacklisted tests
if [ -z "$2" ] ; then
    test_blacklist="${or1k_tooling}/test_blacklist"
else
    test_blacklist=$2
fi
 

# set up path to find utilites and the simulator
PATH=${install}/bin:${or1ksim_install}/bin:${PATH}
export PATH
   
# set up environment to find the test tools
DEJAGNU=${or1k_tooling}/site.exp
DEJAGNULIBS=${install}/share/dejagnu
export DEJAGNU
export DEJAGNULIBS


# start multiple instances of or1ksim for each port in the port file
or1ksim_pids=""
while read port; do
    # trim leading colon character
    port_num=`echo ${port} | cut -c 2-`
    ${or1ksim_install}/bin/sim -m8M --srv=${port_num} &

    or1ksim_pids="${!} ${or1ksim_pids}"
done < ${port_file}
n_ports=`wc -l ${port_file}`

# export the port file so that the board definition can find it
PORT_FILE=${port_file}
export PORT_FILE


# rename blacklisted gcc tests so they won't be run
while read line; do
    mv -f "${gcc_testdir}/${line}" "${gcc_testdir}/${line}.notest"
done < ${test_blacklist}


# run gcc execution tests using clang, clang symlink probably isn't necessary
ln -sf ${install}/bin/clang ${install}/bin/or1k-elf-clang

cd ${gcc_build}/gcc
make -j${n_ports} check-gcc RUNTESTFLAGS="execute.exp --tool_exec ${install}/bin/or1k-elf-clang"


# rename blacklisted gcc tests back
while read line; do
    mv -f "${gcc_testdir}/${line}.notest" "${gcc_testdir}/${line}"
done < ${test_blacklist}


# delete the or1ksim processes
for pid in ${or1ksim_pids} ; do
    kill ${pid}
done

