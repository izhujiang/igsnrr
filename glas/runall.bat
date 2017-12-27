rem step0: comment wget's fetch data from  NASA NSIDC DAAC, using gla14-download script instead under unix-like system (linux, cgywin, et.)
rem wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -i data_url_script_2017-05-09_143646.txt -P ./data/

rem define envi variables that should be replaced with python and idl where had been installed.


rem step1-1: generate ngat inifile for batch_read_altimetry.sav, change the paras in ngat.py file if necessay
python.exe ngat.py ElevationExtractor

rem step1-2: run idl batch_read_altimetry.sav
rem waiting ... until reading altimetry is done.
idlrt.exe batch_read_altimetry.sav

rem step2: run ElevationCorrection including saturation correction and ellipsoid converter
python.exe ngat.py ElevationCorrection

rem All things done!!