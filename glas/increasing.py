#!D:/Python27/python.exe
#coding=utf-8

def readFromInput(input):
    with open(input) as inputFile:
        data = inputFile.readlines()
    return data


def writeToOutput(output, data, mode="w"):
    with open(output, mode) as outputFile:
        outputFile.writelines(data)

def filterData(src1, src2):
    res = []
    for item in src1:
        if not item in src2:
            res.append(item)
    return res

src1 = readFromInput("./data_url_script_1.txt")
src2 = readFromInput("./data_url_script_2.txt")

res = filterData(src1, src2)
writeToOutput("./data_url_script_3.txt",res)

