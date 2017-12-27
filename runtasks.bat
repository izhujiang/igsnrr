rem print help, and comment out the tools you want by remove 'rem' command and erase others
rem D:/Python26/ArcGIS10.0/python.exe tasksrunner.py -h

rem Grads files to Arcgis grd files
rem D:/Python26/ArcGIS10.0/python.exe tasksrunner.py Grads2ArcGisConverterTool C:/Users/hurricane/Documents/GitHub/sda_tools/data/cmorph/CHN_PRCP_HOUR_MERG_DISPLAY_0.1deg.lnx.ctl C:/Users/hurricane/Documents/GitHub/sda_tools/data/cmorph C:/Users/hurricane/Documents/GitHub/sda_tools/data/arcgis -i C:/Users/hurricane/Documents/GitHub/sda_tools/converters/inc.txt -e C:/Users/hurricane/Documents/GitHub/sda_tools/converters/exc.txt

rem ArcGis grd files to time-series file
rem D:/Python26/ArcGIS10.0/python.exe tasksrunner.py Grid2SeriesConverterTool C:/Users/hurricane/Documents/GitHub/sda_tools/data/inputs C:/Users/hurricane/Documents/GitHub/sda_tools/data/mask/bound C:/Users/hurricane/Documents/GitHub/sda_tools/data/gs/gs.txt -t C:/Users/hurricane/Documents/GitHub/sda_tools/data/temp -i C:/Users/hurricane/Documents/GitHub/sda_tools/converters/inc2.txt -e C:/Users/hurricane/Documents/GitHub/sda_tools/converters/exc2.txt
D:/Python26/ArcGIS10.0/python.exe tasksrunner.py Grid2SeriesConverterTool C:/Users/hurricane/Documents/GitHub/sda_tools/data/inputs2 C:/Users/hurricane/Documents/GitHub/sda_tools/data/mask/testbound C:/Users/hurricane/Documents/GitHub/sda_tools/data/gs/gs.txt -t C:/Users/hurricane/Documents/GitHub/sda_tools/data/temp
rem statistics for observation period of each station.
rem D:/Python26/ArcGIS10.0/python.exe tasksrunner.py SurfMonthly2ByStationTool C:/Users/hurricane/Documents/GitHub/sda_tools/data/surf C:/Users/hurricane/Documents/GitHub/sda_tools/data/output
rem D:/Python26/ArcGIS10.0/python.exe tasksrunner.py StationHistoryTool C:/Users/hurricane/Documents/GitHub/sda_tools/data/output C:/Users/hurricane/Documents/GitHub/sda_tools/data/statistics/result.txt
