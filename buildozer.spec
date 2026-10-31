[app]

# (str) Title of your application
title = Whistle Assistant

# (str) Package name
package.name = whistleassistant

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = src

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,yaml,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,cactus-needle[mic],numpy,plyer,pyyaml,psutil,watchdog,sounddevice

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source = my_requirements

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

# (str) Author of the application
author = Your Name

# (str) Copyright of the application
# copyright = 2024

# (str) URL of the application
# url = https://example.com

#
# Kivy Specific
#

# (str) Kivy version to use
# kivy_version = master

# (str) Kivy version to use (git commit, tag, or branch)
# kivy_git_revision = master

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
# android.presplash_color = #FFFFFF

# (string) Presplash animation using Lottie format
# android.presplash_lottie = %(source.dir)s/data/presplash.json

# (list) Permissions
android.permissions = RECORD_AUDIO,INTERNET,FOREGROUND_SERVICE,WAKE_LOCK,POST_NOTIFICATIONS

# (list) Features to add to manifest
android.features = android.hardware.microphone

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
#android.ndk_api = 24

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
# android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
# android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid any unexpected behavior on the download
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# Use that to provide a custom filename for the manifest or to add other attributes.
# android.manifest_extra_xml =

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# android.application_extra_xml =

# (str) Full name including package path of the Java class that implements PythonService
# android.service_class_name = org.kivy.android.PythonService

# (str) Android theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, e.g. OPTIONAL-*.jar
# android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the project
# android.add_src =

# (list) Android AAR archives to add
# android.add_aars =

# (list) Put these Gradle dependencies in the build.gradle file
# android.gradle_dependencies =

# (list) Add android:defaultConfig to build.gradle
# android.gradle_default_config =

# (list) Put these Groovy lines in the build.gradle file at the end of the android block
# android.gradle_extra =

# (list) Put these Groovy lines in the build.gradle file inside the dependencies block
# android.gradle_dependencies_extra =

# (list) Use this to add custom Gradle configuration to the build.gradle file
# android.gradle_custom_config =

# (str) The format of the package to build: 'apk' or 'aab'
android.package_format = apk

# (str) The architecture(s) to build for. Can be: arm64-v8a, armeabi-v7a, x86_64, x86
android.archs = arm64-v8a,armeabi-v7a

# (int) Port number for the debug server (0 = disable)
android.debug_port = 0

# (bool) Enable verbose logging for the build process
log_level = 2

# (bool) Warn if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to buildozer file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin

# (list) List of files to include in the build
# buildozer.include =

# (list) List of files to exclude from the build
# buildozer.exclude =

#
# Python for Android (p4a) specific
#

# (str) p4a branch to use (master, develop, or a specific tag)
p4a.branch = master

# (str) p4a bootstrap to use (sdl2, webview, or other)
# p4a.bootstrap = sdl2

# (str) Whitelist of modules to include in the p4a build
# p4a.whitelist =

# (str) Blacklist of modules to exclude from the p4a build
# p4a.blacklist =

# (list) Additional arguments for p4a
# p4a.extra_args =

#
# iOS specific
#

# (str) Path to a custom xcode project
# ios.xcode_project =

# (str) Name of the certificate to use for signing the debug version
# ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
# ios.codesign.release = "iPhone Distribution: <lastname> <firstname> (<hexstring>)"

# (str) Name of the provisioning profile to use for the debug version
# ios.provisioning.debug =

# (str) Name of the provisioning profile to use for the release version
# ios.provisioning.release =

# (str) URL to a custom provisioning profile
# ios.provisioning.url =

# (str) Name of the App ID to use for the application
# ios.app_id =

# (str) Name of the Team ID to use for the application
# ios.team_id =

#
# Buildozer internal
#

# (number) Buildozer version
# buildozer.version = 1.5.0

# (bool) Do not ask for confirmation on buildozer commands
# buildozer.force_yes = False