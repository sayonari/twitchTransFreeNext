import os
import sys
import subprocess
import shutil

def get_version():
    try:
        # UTF-8エンコーディングでファイルを読み込む
        with open("twitchTransFN.py", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("version ="):
                    return line.split("'")[1]
    except UnicodeDecodeError:
        # UTF-8で読み込めない場合は、他のエンコーディングを試す
        try:
            with open("twitchTransFN.py", "r", encoding="shift-jis") as f:
                for line in f:
                    if line.startswith("version ="):
                        return line.split("'")[1]
        except Exception as e:
            print(f"Error reading file with shift-jis encoding: {e}")
    except Exception as e:
        print(f"Error reading file: {e}")

    # バージョン情報が取得できない場合は、環境変数から取得を試みる
    import os
    if "VERSION" in os.environ:
        return os.environ["VERSION"]

    return "unknown"

def build_for_os(os_name, arch):
    version = get_version()
    print(f"Building for {os_name} ({arch}) with Nuitka...")

    # distフォルダを削除
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # 共通のNuitkaオプション
    base_command = [
        "python", "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--assume-yes-for-downloads",
        "--include-data-file=cacert.pem=cacert.pem",
    ]

    # OS別の設定
    if os_name == "windows":
        base_command.extend([
            "--windows-console-mode=force",
            "--windows-icon-from-ico=icon.ico",
            "--output-filename=twitchTransFN.exe",
        ])
        output_file = "twitchTransFN.exe"
        final_name = f"twitchTransFN_{version}_win.exe"
    elif os_name == "linux":
        base_command.extend([
            "--output-filename=twitchTransFN",
        ])
        output_file = "twitchTransFN"
        final_name = f"twitchTransFN_{version}_linux"
    elif os_name == "macos":
        base_command.extend([
            "--output-filename=twitchTransFN.command",
        ])
        output_file = "twitchTransFN.command"
        if arch == "arm64":
            final_name = f"twitchTransFN_{version}_macos_M1.command"
        elif arch == "x86_64":
            final_name = f"twitchTransFN_{version}_macos_Intel.command"

    # メインスクリプトを追加
    base_command.append("twitchTransFN.py")

    # ビルド実行
    subprocess.run(base_command, check=True)

    # distフォルダを作成
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # ファイル名の変更と移動
    if os.path.exists(output_file):
        shutil.move(output_file, f"dist/{final_name}")

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

    # 各OS向けにビルド
    if target_os == "windows":
        build_for_os("windows", "")
    elif target_os == "linux":
        build_for_os("linux", "")
    elif target_os == "macos_M1":
        build_for_os("macos", "arm64")
    elif target_os == "macos_Intel":
        build_for_os("macos", "x86_64")

    print("Build process completed.")

if __name__ == "__main__":
    main(sys.argv[1])
