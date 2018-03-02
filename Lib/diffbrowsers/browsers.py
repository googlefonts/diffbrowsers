"""
Browser info for Browser Stack api

"""

win_7_pc_chrome = {"os":"Windows",
    "os_version":"7",
    "browser":"chrome",
    "device":None,
    "browser_version":"50.0",
    "real_mobile":None}

win_7_pc_ie = {"os":"Windows",
    "os_version":"7",
    "browser":"ie",
    "browser_version":"9.0"}

win_10_pc_edge = {"os":"Windows",
    "os_version":"10",
    "browser":"edge",
    "device":None,
    "browser_version":"15.0",
    "real_mobile":None}

win_7_pc_firefox = {"os":"Windows",
    "os_version":"7",
    "browser":"firefox",
    "device":None,
    "browser_version":"45.0",
    "real_mobile":None}

osx_yosemite_pc_safari = {"os":"OS X",
    "os_version":"El Capitan",
    "browser":"safari",
    "device":None,
    "browser_version":"9.1",
    "real_mobile":None}

android = {"os":"android",
    "os_version":"5.0",
    "browser":"Android Browser",
    "device":"Google Nexus 5",
    "browser_version":None,
    "real_mobile":None}

all_browsers = {'browsers': [
    win_7_pc_chrome,
    win_7_pc_ie,
    win_10_pc_edge,
    win_7_pc_firefox,
    osx_yosemite_pc_safari,
    android,
]}

osx_browser = {'browsers': [osx_yosemite_pc_safari]}

gdi_browsers = {'browsers': [win_7_pc_ie]}

android_browsers = {'browsers': [android]}

test_browsers = {
    'all_browsers': all_browsers,
    'gdi_browsers': gdi_browsers,
    'osx_browser': osx_browser,
    'android_browsers': android_browsers,
}