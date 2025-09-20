[app]

# (str) Title of your application
title = Freevia

# (str) Package name
package.name = freevia

# (str) Package domain (needed for android/ios packaging)
package.domain = com.freevia

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,csv

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.1.0,requests,Pillow,plyer,pyjnius

# (list) Garden requirements
garden_requirements = mapview

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

[app:android]

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
android.activity_class_name = org.kivy.android.PythonActivity

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Android app theme, default is ok for Kivy-based app
android.theme = @android:style/Theme.NoTitleBar

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) Target Android API
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK version to use
android.sdk = 31

# (str) NDK path (if empty, it will be auto-detected)
android.ndk_path = 

# (str) SDK path (if empty, it will be auto-detected)
android.sdk_path =

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

[buildozer:remote]

# (str) Remote server IP
#remote.server = 192.168.1.1

# (str) Remote server port
#remote.port = 22

# (str) Remote server username
#remote.username = user

# (str) Remote server password (optional)
#remote.password = 

# (str) Path to remote directory
#remote.path = /home/user/buildozer

[buildozer:vm]

# (str) VM IP
#vm.ip = 127.0.0.1

# (str) VM port
#vm.port = 2222

# (str) VM username
#vm.username = kivy

# (str) VM password
#vm.password = kivy

# (str) VM path
#vm.path = /home/kivy/buildozer