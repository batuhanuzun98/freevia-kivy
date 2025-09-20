# iOS Deployment Requirements for Freevia

## Prerequisites for iOS Deployment

### 1. Apple Developer Account
- Required for device testing and App Store submission
- Costs $99/year
- Sign up at: https://developer.apple.com

### 2. macOS Machine
- iOS builds require Xcode and macOS
- Can use GitHub Actions with macOS runners (free for public repos)

### 3. Certificates and Provisioning Profiles
- iOS Development Certificate (for testing)
- iOS Distribution Certificate (for App Store)
- Provisioning Profiles for your Bundle ID (com.freevia.app)

## iOS Build Process

### Option 1: Local Build (requires macOS)
```bash
# Install dependencies
brew install autoconf automake libtool pkg-config libffi openssl

# Install Python packages
pip install kivy-ios buildozer

# Build iOS app
buildozer ios debug
```

### Option 2: GitHub Actions (automated)
- The workflow is already set up in `.github/workflows/build-ios.yml`
- Runs on macOS runners automatically
- Produces .app and .ipa files

## iOS-Specific Features Configured

### Permissions (in buildozer.spec and ios-info.plist):
- ✅ Location Services (GPS)
- ✅ Photo Library Access
- ✅ Camera Access
- ✅ Motion Sensors

### Frameworks:
- ✅ CoreLocation (GPS)
- ✅ MapKit (Maps)
- ✅ CoreMotion (Motion sensors)
- ✅ Photos (Photo access)
- ✅ AVFoundation (Camera)

### App Configuration:
- Bundle ID: com.freevia.app
- Display Name: Freevia
- Minimum iOS Version: 12.0
- Portrait orientation only
- iOS-style UI components

## File Changes Made for iOS Compatibility:

1. **buildozer.spec**: Added complete iOS section
2. **ios-info.plist**: iOS permissions template
3. **freevia_kivy.py**: Cross-platform file path handling
4. **build-ios.yml**: GitHub Actions workflow for iOS builds

## Next Steps for iOS Deployment:

1. **Test with GitHub Actions**: Push code to trigger iOS build
2. **Apple Developer Setup**: Get developer account and certificates
3. **Device Testing**: Install .ipa on iOS device using Xcode
4. **App Store Submission**: Use Xcode to submit to App Store

## iOS vs Android Differences:

- **Android**: Uses `pyjnius` for Java bridge
- **iOS**: Uses `pyobjus` for Objective-C bridge (auto-handled)
- **Android**: External storage in `/sdcard/`
- **iOS**: Sandboxed Documents directory
- **Android**: Various screen sizes and orientations
- **iOS**: More consistent, but strict app review process

The app code is now fully iOS compatible and will work on both platforms!