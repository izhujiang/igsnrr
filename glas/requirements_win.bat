rem install python(Python 2.7.x or 3.4.x, ATTENTION). If not available, download and install from https://www.python.org/downloads/windows/
rem ATTENTION: IDL 8.5 only support Python 2.7.x or 3.4.x. NOT python2.5,2.6... and NOT python3.5, 3.6....
rem install numpy
pip install numpy

rem Remember to config path for idl_python bridge for Windows Platforms
rem You should ensure that your Python executable is on the Windows system PATH environment variable. IDL will use the first Python executable that it finds on the system path. You should also ensure that IDL's bin directory is on the Windows system PATH environment variable when launching Python. For 64-bit Windows this would look like:

rem PATH = ...;c:\Program Files\Exelis\IDLXX\bin\bin.x86_64;...
rem where XX is the IDL version number.

rem If you want multiple versions of IDL side-by-side on your Windows system, you cannot set this permanently in your Windows environment. You need to create a script to append the IDL bin directory to the PATH environment variable, then launch Python.

rem You will also need to add IDL's bin directory and the lib/bridges directory to the PYTHONPATH environment variable. For 64-bit Windows this would look like:

rem PYTHONPATH = c:\Program Files\Exelis\IDLXX\bin\bin.x86_64; C:\Program Files\Exelis\IDLXX\lib\bridges
rem where XX is the IDL version number.
