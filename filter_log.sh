#!/bin/bash


log_file=$1


# Remove everything but the test results
sed -e '/Executing on host/,/PASS\|FAIL/{/PASS\|FAIL/!d}'  ${log_file} > 'a.tmp'
sed -e '/Executing on build/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'a.tmp'     > 'b.tmp'

# Delete the logs after a pass. Run repeatedly since the search
# doesn't start from the correct position if there are multiple 'PASS' logs 
# in a row
sed -e '/PASS/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'b.tmp' > 'a.tmp'
sed -e '/PASS/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'a.tmp' > 'b.tmp'
sed -e '/PASS/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'b.tmp' > 'a.tmp'
sed -e '/PASS/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'a.tmp' > 'b.tmp'
sed -e '/PASS/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'b.tmp' > 'a.tmp'
sed -e '/PASS/,/PASS\|FAIL/{/PASS\|FAIL/!d}' 'a.tmp' > 'b.tmp'

# Extract everything that isn't a failure
grep 'PASS'        'b.tmp' > 'pass.log'
grep 'UNRESOLVED'  'b.tmp' > 'unresolved.log'
grep 'XFAIL'       'b.tmp' > 'xfail.log'
grep 'UNSUPPORTED' 'b.tmp' > 'unsupported.log'

grep -v 'PASS\|UNRESOLVED\|XFAIL\|UNSUPPORTED' 'b.tmp' > 'fail.log'


# Sort all of the failures and remove stray gdb messages
./sort_failures.py 'fail.log' | grep 'FAIL:\|# Error regexp:' | sed 's/(gdb) //g' > 'fail_sorted.log'


# Create a test blacklist from the sorted log, by stripping all but filenames
# and comments
sed -e 's/FAIL: \(\S*\) \?.*$/\1/g' 'fail_sorted.log' > 'blacklist'


# Create an xfail manifest list by adding unresolved tests to the end of the
# sorted log
cat 'fail_sorted.log' <(echo -e "# Unresolved tests") 'unresolved.log' > 'result.xfail'


# remove the temporary files
rm 'a.tmp'
rm 'b.tmp'
