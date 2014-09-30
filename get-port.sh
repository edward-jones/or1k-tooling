#!/bin/bash


port_file=$1
lock_file=`dirname ${DEJAGNU}`/get-port.lock
tmp=/tmp/get-port-$$

# Lock all file manipulation
(
    flock -e 200

    # Check for available port
    if [ ! -s ${port_file} ]
    then
        echo "No available port" >&2
        exit 1
    fi

    # Get the top port
    port=`head -1 ${port_file}`

    # Rotate to the bottom of the port file
    tail -n +2 ${port_file} > ${tmp}
    echo ${port} >> ${tmp}
    mv ${tmp} ${port_file}

    echo ${port}
) 200> ${lock_file}

