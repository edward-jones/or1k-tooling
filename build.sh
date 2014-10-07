#!/bin/bash

# Current shortcoming is that this can only set up the environment correctly
# when one of the commands is run. So things run outside the environment wont be
# set up right at all. Will be a major issue if doing incremental builds
#
# Hopefully will always run tests using this script, but at the very least
# PATH will need install/bin and or1ksim-install/bin in

basedir=`pwd`

# for make
build_parallel="-j12"


# Beware: the install directory and build directories will be nuked at the
# start of a clean build
install=${basedir}/install

binutils_build=${basedir}/build/binutils
binutils_src=${basedir}/or1k-src

llvm_build=${basedir}/build/llvm
llvm_src=${basedir}/llvm-or1k
clang_src=${basedir}/clang-or1k

compiler_rt_build=${basedir}/build/compiler-rt
compiler_rt_src=${basedir}/compiler-rt-or1k

newlib_build=${basedir}/build/newlib
newlib_src=${basedir}/or1k-src

gcc_build=${basedir}/build/gcc
gcc_src=${basedir}/or1k-gcc

or1ksim_build=${basedir}/build/or1ksim
or1ksim_src=${basedir}/or1ksim
or1ksim_install=${basedir}/or1ksim-install

cruntime_build=${basedir}/build/cruntime
cruntime_src=${basedir}/cruntime-or1k

dejagnu_build=${basedir}/build/dejagnu
dejagnu_src=${basedir}/or1k-dejagnu

or1k_tooling=${basedir}/or1k-tooling


# Set terminal title                                                            
# @param string $1  Tab/window title                                            
# @param string $2  (optional) Separate window title                            
# The latest version of this software can be obtained here:                     
# http://fvue.nl/wiki/NameTerminal                                              
# (Modified to avoid breakage with -e in this script by Simon Cook)             
nameTerminal() {                                                                
    echo " * $1"                                                                
    [ "${TERM:0:5}" = "xterm" ]   && local ansiNrTab=0                          
    [ "$TERM"       = "rxvt" ]    && local ansiNrTab=61                         
    [ "$TERM"       = "konsole" ] && local ansiNrTab=30 ansiNrWindow=0          
        # Change tab title                                                      
    [ $ansiNrTab ] && echo -n $'\e'"]$ansiNrTab;$0 - $1"$'\a'                   
} # nameTerminal()                                                              
                                                                                
mkcd() {                                                                        
  mkdir -p "${1}" && cd "${1}"                                                  
} 


binutilsConfig() {
    rm -rf ${binutils_build}
    mkcd ${binutils_build}
    ${binutils_src}/configure --prefix=${install} --target=or1k-elf \
      --enable-shared --disable-itcl --disable-tk --disable-tcl \
      --disable-winsup --disable-libgui --disable-rda --disable-sid \
      --disable-sim --disable-gdb --with-sysroot --disable-newlib \
      --disable-libgloss --disable-werror > config.log 2>&1
}

llvmConfig() {
    rm -rf ${llvm_build}

    # ensure theres a symlink to clang in the tools directory
    ln -sf ${clang_src} ${llvm_src}/tools/clang

    mkcd ${llvm_build}
    cmake ${llvm_src} -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_INSTALL_PREFIX=${install} > config.log 2>&1
}

or1ksimConfig() {
    rm -rf ${or1ksim_build}
    mkcd ${or1ksim_build}
    ${or1ksim_src}/configure --prefix=${or1ksim_install} > config.log 2>&1
}

# should be built after binutils and llvm/clang
compilerrtConfig() {
    # ensure clang/binutils in the PATH
    export PATH=${install}/bin:$PATH

    rm -rf ${compiler_rt_build}

    # hardcoded LLVM_CONFIG_PATH but it should be in path anyway
    mkcd ${compiler_rt_build}
    cmake ${compiler_rt_src} \
      -DCMAKE_INSTALL_PREFIX=${install} \
      -DLLVM_CONFIG_PATH=${install}/bin/llvm-config \
      -DCMAKE_C_COMPILER=${install}/bin/clang \
      -DCMAKE_CXX_COMPILER=${install}/bin/clang++ \
      -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug > config.log 2>&1
}

# should be built after clang, binutils and or1ksim. Testing with or1ksim is
# done via gdb so I don't think it's really necessary to link against it.
newlibConfig() {
    rm -rf ${newlib_build}

    # ensure clang/binutils in the path
    export PATH=${install}/bin:${PATH}

    # add symlink to find clang when looking for or1k-elf cross compiler
    ln -sf ${install}/bin/clang ${install}/bin/or1k-elf-cc

    mkcd ${newlib_build}
    ${newlib_src}/configure CC=${install}/bin/clang --prefix=${install} \
      --target=or1k-elf --enable-shared --disable-itcl --disable-tk \
      --disable-tcl --disable-winsup --disable-libgui --disable-rda \
      --disable-sid --enable-sim --enable-gdb --with-sysroot --enable-newlib \
      --enable-libgloss --disable-werror --with-or1ksim=${or1ksim_install} \
      > config.log 2>&1
}

# should be built after clang and binutils
cruntimeConfig() {
    rm -rf ${cruntime_build}

    # ensure clang/binutils in the path
    export PATH=${install}/bin:${PATH}

    # no gcc cross compiler atm, use clang
    mkcd ${cruntime_build}
    cmake ${cruntime_src} -DCMAKE_INSTALL_PREFIX=${install} \
      -DCMAKE_C_COMPILER=${install}/bin/clang \
      -DCMAKE_CXX_COMPILER=${install}/bin/clang++ > config.log 2>&1
}

# configure gcc cross-compiler for or1k tests, may need to be done after newlib
# built.
gccConfig() {
    rm -rf ${gcc_build}
    mkcd ${gcc_build}
    ${gcc_src}/configure --prefix=${install} --target=or1k-elf \
      --enable-languages=c,c++ --disable-shared --disable-libssp --with-newlib \
      > config.log 2>&1
}

# don't think this has any dependencies
dejagnuConfig() {
    rm -rf ${dejagnu_build}
    mkcd ${dejagnu_build}
    ${dejagnu_src}/configure --prefix=${install} > config.log 2>&1
}

makeInstall() {
    make V=1 VERBOSE=1 ${build_parallel} > build.log 2>&1
    make V=1 VERBOSE=1 ${build_parallel} install > install.log 2>&1
}

bootstrapAll() {
    nameTerminal "Deleting previous installations"
    rm -rf ${install}
    rm -rf ${or1ksim_install}

    nameTerminal "Configuring binutils"
    binutilsConfig
    nameTerminal "Building/Installing binutils"
    cd ${binutils_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error binutils"
        exit
    fi

    # add new binutils to the path
    export PATH=${install}/bin:${PATH}

    nameTerminal "Configuring LLVM/Clang"
    llvmConfig
    nameTerminal "Building/Installing llvm/clang"
    cd ${llvm_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: LLVM/Clang"
        exit
    fi

    nameTerminal "Configuring Compiler-RT"
    compilerrtConfig
    nameTerminal "Building/Installing compiler-rt"
    cd ${compiler_rt_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: Compiler-RT"
        exit
    fi

    nameTerminal "Configuring or1ksim"
    or1ksimConfig
    nameTerminal "Building/Installing or1ksim"
    cd ${or1ksim_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: or1ksim"
        exit
    fi

    # add symlink to find clang when looking for or1k-elf cross compiler
    ln -sf ${install}/bin/clang ${install}/bin/or1k-elf-cc

    nameTerminal "Configuring newlib"
    newlibConfig
    nameTerminal "Building/Installing newlib"
    cd ${newlib_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: newlib"
        exit
    fi

    nameTerminal "Configuring c-runtime"
    cruntimeConfig
    nameTerminal "Building/Installing cruntime"
    cd ${cruntime_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: c-runtime"
        exit
    fi

    nameTerminal "Configuring gcc"
    gccConfig
    nameTerminal "Building/Installing gcc"
    cd ${gcc_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: gcc"
        exit
    fi
    # don't actually need to install, but may be useful anyway

    nameTerminal "Configuring DejaGNU"
    dejagnuConfig
    nameTerminal "Building/Installing DejaGNU"
    cd ${dejagnu_build}
    makeInstall
    if [ $? != 0 ]; then
        nameTerminal "Error: DejaGNU"
        exit
    fi
}


if [ "$1" = "bootstrap" ]; then
    bootstrapAll
fi
if [ "$1" = "config" ]; then
    if [ "$2" = "binutils" ]; then
        binutilsConfig
    fi
    if [ "$2" = "llvm" ]; then
        llvmConfig
    fi
    if [ "$2" = "or1ksim" ]; then
        or1ksimConfig
    fi
    if [ "$2" = "compiler_rt" ]; then
        compilerrtConfig
    fi
    if [ "$2" = "newlib" ]; then
        newlibConfig
    fi
    if [ "$2" = "cruntime" ]; then
        cruntimeConfig
    fi
    if [ "$2" = "gcc" ]; then
        gccConfig
    fi
    if [ "$2" = "dejagnu" ]; then
        dejagnuConfig
    fi
fi

