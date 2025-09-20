# Docker Solution for APK Building on Windows

## Prerequisites
1. Install Docker Desktop for Windows
2. Make sure Docker is running

## Build APK using Docker

```bash
# Create a Dockerfile for APK building
# Run this in PowerShell in your project directory:

docker run --rm -v ${PWD}:/home/user/app -w /home/user/app \
  ubuntu:22.04 bash -c "
    apt update && apt install -y python3 python3-pip git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev && \
    python3 -m pip install buildozer cython kivy[base]==2.3.1 requests pillow plyer kivy-garden.mapview && \
    buildozer android debug
  "
```

## The APK will be created in the bin/ directory

This approach uses a Linux container to build your APK without installing WSL2.