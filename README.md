# Freevia - Second-hand Item Sharing Platform

![Freevia Logo](blue_pin.png)

Freevia is a mobile application built with Kivy that allows users to share second-hand items with others in their community. Users can take photos of items they no longer need, add descriptions, and mark their location on a map for others to find.

## 🌟 Features

- **User Authentication**: Secure sign-up and login system
- **Item Sharing**: Take photos and share items with descriptions
- **Interactive Map**: View shared items on a map with GPS integration
- **Location Services**: Automatic location detection and manual selection
- **Profile Management**: User profiles and account management
- **iOS-style UI**: Beautiful, modern interface inspired by iOS design
- **Offline Capable**: Works without internet for basic functionality

## 📱 Screenshots

The app features a clean, iOS-inspired design with:
- Smooth animations and transitions
- Intuitive navigation
- Card-based UI elements
- Professional color scheme

## 🚀 APK Download

### Automated Builds
Every push to the main branch automatically builds a new APK:

1. **Go to the [Releases](../../releases) page**
2. **Download the latest `freevia-debug.apk`**
3. **Install on your Android device**

### Manual Download
If you need the APK immediately:

1. **Go to [Actions](../../actions) tab**
2. **Click on the latest "Build APK" workflow**
3. **Download the `freevia-debug-apk` artifact**
4. **Extract and install the APK**

## 🔧 Building Locally

### Prerequisites
- Linux, macOS, or WSL2 on Windows
- Python 3.8+
- Java 8 (OpenJDK)
- Android SDK (automatically downloaded by buildozer)

### Quick Build
```bash
# Clone the repository
git clone https://github.com/yourusername/freevia-kivy.git
cd freevia-kivy

# Install dependencies
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev

# Install Python packages
pip3 install buildozer cython

# Build APK (first build takes 30-60 minutes)
buildozer android debug

# APK will be in bin/ directory
ls bin/*.apk
```

### Dependencies
All required dependencies are listed in `requirements.txt`:
- **Kivy**: Cross-platform UI framework
- **Requests**: HTTP library for API calls
- **Pillow**: Image processing
- **Plyer**: Mobile platform features (GPS, camera)
- **kivy-garden.mapview**: Map widget

## 📂 Project Structure

```
freevia-kivy/
├── freevia_kivy.py          # Main application code
├── main.py                  # Entry point for buildozer
├── buildozer.spec           # Build configuration
├── requirements.txt         # Python dependencies
├── blue_pin.png            # Map marker image
├── users.csv               # User data storage
├── cache/                  # Map tile cache
├── .github/
│   └── workflows/
│       └── build-apk.yml   # GitHub Actions build script
└── README.md               # This file
```

## 🎯 How to Use

### 1. **Sign Up / Sign In**
- Create a new account or sign in with existing credentials
- User data is stored locally in `users.csv`

### 2. **Share Items**
- Tap "Eşya Paylaş" (Share Item)
- Take a photo of your item
- Add name and description
- Select location (current or from map)
- Tap "Eşyayı Paylaş" (Share Item)

### 3. **Browse Items**
- Tap "Eşyaları Keşfet" (Discover Items)
- View shared items on the interactive map
- Search for specific items
- Tap markers to see item details

### 4. **Profile Management**
- View and edit your profile
- See your sharing history
- Manage account settings

## 🌍 Localization

The app is currently in Turkish but can be easily localized:
- All text strings are in the source code
- UI supports RTL languages
- GPS and location services work globally

## 🔒 Privacy & Permissions

The app requests these Android permissions:
- **Internet**: For map tiles and location services
- **Location**: GPS for item location tagging
- **Storage**: Save photos and cache map data
- **Camera**: Take photos of items to share

## 🛠️ Development

### Running in Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run on desktop (for testing)
python freevia_kivy.py
```

### Code Structure
- `freevia_kivy.py`: Main application with all screens and logic
- iOS-style UI components with custom styling
- Modular screen-based architecture
- Cross-platform location services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Issues

If you encounter any issues:
1. Check the [Issues](../../issues) page
2. Create a new issue with:
   - Device information
   - Android version
   - Steps to reproduce
   - Screenshots if relevant

## 📧 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- **Kivy Team**: For the amazing cross-platform framework
- **OpenStreetMap**: For map data
- **Contributors**: Everyone who helps improve this project

---

**Made with ❤️ using Kivy and Python**