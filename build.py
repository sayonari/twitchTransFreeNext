import os
import sys
import subprocess
import shutil

def get_version():
    with open("twitchTransFN.py", "r") as f:
        for line in f:
            if line.startswith("version ="):
                return line.split("'")[1]
    return "unknown"

def build_for_os(os_name, arch, add_data_option):
    version = get_version()
    print(f"Building for {os_name} ({arch})...")
    
    # distフォルダを削除
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # build
    command = [
        "pyinstaller",
        "--onefile",
        "--icon=icon.ico",  # アイコン設定を追加
        "--runtime-tmpdir=.", # runtime-tmpdirを追加
        add_data_option,
        "twitchTransFN.py"
    ]
    subprocess.run(command, check=True)

    # ファイル名の変更
    if os_name == "windows":
        os.rename("dist/twitchTransFN.exe", f"dist/twitchTransFN_{version}_win.exe")
    elif os_name == "linux":
        os.rename("dist/twitchTransFN", f"dist/twitchTransFN_{version}_linux")
    elif os_name == "macos":
        if arch == "arm64":
            os.rename("dist/twitchTransFN", f"dist/twitchTransFN_{version}_macos_M1")
        elif arch == "x86_64":
            os.rename("dist/twitchTransFN", f"dist/twitchTransFN_{version}_macos_Intel")

    print(f"Build for {os_name} ({arch}) completed.")

def main(target_os):
    # cacert.pemが存在することを確認
    if not os.path.exists("cacert.pem"):
        print("Error: cacert.pem not found. Downloading...")
        try:
            import urllib.request
            urllib.request.urlretrieve("https://curl.se/ca/cacert.pem", "cacert.pem")
            print("cacert.pem downloaded successfully.")
        except Exception as e:
            print(f"Failed to download cacert.pem: {e}")
            return

    # distフォルダの準備
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # 各OS向けにビルド
    if target_os == "windows":
        build_for_os("windows", "", "--add-data=cacert.pem;.")
    elif target_os == "linux":
        build_for_os("linux", "", "--add-data=cacert.pem:.")
    elif target_os == "macos_M1" or target_os == "macos_Intel":
        # macOSの場合は区切り文字がコロン
        add_data_option = "--add-data=cacert.pem:."
        if target_os == "macos_M1":
            build_for_os("macos", "arm64", add_data_option)
        else:
            build_for_os("macos", "x86_64", add_data_option)

    print("Build process completed.")

if __name__ == "__main__":
    main(sys.argv[1])
