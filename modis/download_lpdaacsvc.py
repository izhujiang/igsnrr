#!/usr/bin/env python3
from fileinput import filename
import os
import cgi
import requests
import re


# token_response example
# {
#   "token_type": "Bearer",
#   "token": "31ncqphv-1jpPjcTe-hgWXM2xZ1bBqQxST5pcieiHKq0cMwz8IFKOxG3FZgLQonk8hBsLV_ruAqikYXfzWy7kw",
#   "expiration": "2022-02-20T20:24:27Z"
# }
apiUrl = 'https://appeears.earthdatacloud.nasa.gov/api'
# This token will expire approximately 48 hours after being acquired.


def login(user, password):
    # response = requests.post(
    #     'https://lpdaacsvc.cr.usgs.gov/appeears/api/login',
    #     auth=(user, password))
    response = requests.post(
        '{0}/login'.format(apiUrl),
        auth=(user, password))
    if response.status_code != 200:
        print("{0} failed to login:{1}".format(user, response.reason))
        return None

    token_response = response.json()
    print("login successfully")
    return token_response


def logout(token_response):
    token = token_response['token']
    response = requests.post(
        '{0}/logout'.format(apiUrl),
        headers={'Authorization': 'Bearer {0}'.format(token)})
    print(response.status_code)


def getBundle(token_response, task_id):
    token = token_response['token']
    response = requests.get(
        '{0}/bundle/{1}'.format(apiUrl, task_id),
        headers={
            'Authorization': 'Bearer {0}'.format(token)
        }
    )
    bundle_response = response.json()
    if response.status_code != 200:
        print("failed to fetch bundle with task {0}: {1}".format(
            task_id, response.reason))
        return None
    return bundle_response
    # print(bundle_response)


def downloadFiles(token_response, task_id, bundle_response, dest_dir, orderFunc):
    # token = token_response['token']
    for f in bundle_response["files"]:
        filename = f["file_name"]
        dir = dest_dir
        subDir = orderFunc(filename)
        if subDir:
            dir = os.path.join(dest_dir, subDir)
        if not os.path.exists(dir):
            os.makedirs(dir)

        # print(dir)
        # print(f)
        curlFile(token_response, task_id, f, dir)


def curlFile(token_response, task_id, f, dest_dir):
    token = token_response['token']
    # rpath = "https://lpdaacsvc.cr.usgs.gov/appeears/api/bundle/0974a514-13fd-4bf0-b8c9-65e6e5d6b06a/4d2ddf7c-598e-499d-86ff-2ebe57b3121f"
    rpath = "{0}/bundle/{1}/{2}".format(apiUrl, task_id, f["file_id"])

    fileName = f["file_name"]
    fileName = fileName.replace("\\", "/")
    fileName = fileName[fileName.find("/") + 1:]

    lpath = os.path.join(dest_dir, fileName)

    # curl -O --remote-header-name --header "Authorization: Bearer your-token" --location "https://lpdaacsvc.cr.usgs.gov/appeears/api/bundle/0974a514-13fd-4bf0-b8c9-65e6e5d6b06a/4d2ddf7c-598e-499d-86ff-2ebe57b3121f"
    # cmd = "curl -C - --remote-header-name --header \"Authorization: Bearer {0}\" --location {1} --output {2}".format(token, rpath, lpath)
    cmd = "curl -C - --header \"Authorization: Bearer {0}\" --location {1} --output {2}".format(
        token, rpath, lpath)
    # print(cmd)
    print("downloading {0} from {1}".format(fileName, rpath))
    os.system(cmd)

# helper function:


def getSubDirectoryByYear(fileName):
    fileName = fileName.replace("\\", "/")
    fileName = fileName[fileName.find("/") + 1:]

    match = re.search("\d{7}", fileName)
    if match:
        return match.group(0)[0:4]
    return None


if __name__ == "__main__":
    user = "m.zhujiang"
    psword = "Qaz@1234"
    task_id = "d9b9a4f6-658e-49e8-9a7a-5cb97fb09f07"
    dest_dir = "C:/igsnrr/data/modis/MOD13Q1.061"

    # --------------------
    os.environ["CURL_SSL_BACKEND"] = "secure-transport"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # token_response = {'token_type': 'Bearer', 'token': 'fBx51fb8ofQWAw9E94so2l4c_GYKK43sy_Qo5U3VhRGvVhIr5d42fqRmXPPkv4TOaYmacP3O5MhdCQmbIgJvog', 'expiration': '2022-03-21T16:51:50Z'}
    token_response = login(user, psword)

    orderFunc = getSubDirectoryByYear
    if token_response != None:
        bundle = getBundle(token_response, task_id)
        if bundle != None:
            # f = {'sha256': 'bc19963bfbcc2eb2b5bd036c0e119994364a51d4478ab40696f30bebd65bcc34', 'file_id': 'dd6f5cd0-1897-46db-aa0b-13a904fb6122', 'file_name': 'MOD13Q1.061_2019351_to_2022001/MOD13Q1.061__250m_16_days_VI_Quality_doy2022001_aid0001.tif', 'file_size': 32476187, 'file_type': 'tif'}
            # dest_dir = "/Users/hurricane/share/modis/MOD13Q1.061/2022"
            # curlFile(token_response, task_id, f, dest_dir)

            downloadFiles(token_response, task_id, bundle, dest_dir, orderFunc)
        else:
            print("invalid bundle: check task_id please.")
        logout(token_response)
