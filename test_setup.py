#!/usr/bin/env python3
"""
Test script to verify Python 3.13 and all required libraries are working properly.
"""

import sys
print(f"Python version: {sys.version}")

# Test all required imports
try:
    import kivy
    print(f"✅ Kivy: {kivy.__version__}")
    
    import requests
    print(f"✅ Requests: {requests.__version__}")
    
    import PIL
    print(f"✅ Pillow: {PIL.__version__}")
    
    import plyer
    print(f"✅ Plyer: {plyer.__version__}")
    
    # Test Kivy components
    from kivy.app import App
    from kivy.uix.widget import Widget
    print("✅ Kivy core components imported")
    
    # Test MapView
    from kivy_garden.mapview import MapView, MapMarker
    print("✅ MapView components imported")
    
    # Test platform-specific modules
    try:
        import pyjnius
        print("✅ PyJNIus available (for Android)")
    except ImportError:
        print("⚠️  PyJNIus not available (normal on non-Android)")
    
    print("\n🎉 All required libraries are working correctly!")
    print("Your Freevia app is ready to run with Python 3.13!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)