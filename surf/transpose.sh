#!/bin/bash

input_dir=/Users/jiangzhu/workspace/igsnrr/data/hours/bydate
output_dir=/Users/jiangzhu/workspace/igsnrr/data/hours/result
rm -rf ${output_dir}
mkdir -p ${output_dir}/bystation
find ${input_dir} -type f | sort | xargs awk '
BEGIN {
    print "processing " FILENAME " ... "
    FS=","
    ORS="\n"
    OFS="\t"
    OUT_ROOT="/Users/jiangzhu/workspace/igsnrr/data/hours/result/bystation/"
}
{
    # print $0
    if ($0 ~ /^[A-Za-z_0-9]+,[0-9]+/) {
        ofile = OUT_ROOT $1
        id = $1
        year = $2
        mon = $3
        day = $4
        hour = $5
        pres = $6
        temp = $7
        prec_h1 = $8
        # print id, $2$3$4$5, year, mon, day, hour, pres, temp, prec_h1
        # printf("%-8s %4d%02d%02d%02d %6d %4d %4d %4d %10.1f %10.1f %10.1f\n", id, year, mon, day, hour,
        #                                  year, mon, day, hour, pres, temp, prec_h1)

        printf("%-6s\t%4d%02d%02d%02d\t%6d\t%4d\t%4d\t%4d\t%6.1f\t%6.1f\t%6.1f\n", id, year, mon, day, hour,
                                         year, mon, day, hour, pres, temp, prec_h1) >> ofile
    }
}
END { }
'
# ./transpose.awk
# find ./result/bystation -type f

# find ${output_dir}/bystation -type f -print0 | xargs -t -0 -I fpath sed -i "" -e '1 i\'$'\nSID\tDATETIME\tYEAR\tMON\tDAY\tHR\tPRES\tTEMP\tPREC' fpath
find ${output_dir}/bystation -type f -print0 | xargs -0 -I fpath sed -i "" -e '1 i\'$'\nSID\tDATETIME\tYEAR\tMON\tDAY\tHR\tPRES\tTEMP\tPREC' fpath
# find ./result/bystation -type f -print0 | xargs -t -0 -I fpath echo fpath
