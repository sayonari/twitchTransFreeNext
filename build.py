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

    # distフォルダを作成
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # OS別の設定
    if os_name == "windows":
        output_file = "twitchTransFN.exe"
        final_name = f"twitchTransFN_{version}_win.exe"
        nuitka_options = [
            "--windows-console-mode=force",
        ]
        # icon.icoが存在する場合のみアイコンを設定
        if os.path.exists("icon.ico"):
            nuitka_options.append("--windows-icon-from-ico=icon.ico")
    elif os_name == "linux":
        output_file = "twitchTransFN"
        final_name = f"twitchTransFN_{version}_linux"
        nuitka_options = []
    elif os_name == "macos":
        output_file = "twitchTransFN.command"
        nuitka_options = []
        if arch == "arm64":
            final_name = f"twitchTransFN_{version}_macos_M1.command"
        elif arch == "x86_64":
            final_name = f"twitchTransFN_{version}_macos_Intel.command"

    # Nuitkaコマンドの構築（uv経由で実行）
    base_command = [
        "uv", "run", "python", "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--assume-yes-for-downloads",
        "--nofollow-import-to=config",  # config.pyをバイナリに含めない
        "--include-data-file=cacert.pem=cacert.pem",
        f"--output-dir=dist",
        f"--output-filename={output_file}",
    ]
    base_command.extend(nuitka_options)
    base_command.append("twitchTransFN.py")

    # ビルド実行
    print(f"Running: {' '.join(base_command)}")
    subprocess.run(base_command, check=True)

    # ファイル名の変更
    built_file = os.path.join("dist", output_file)
    final_file = os.path.join("dist", final_name)

    if os.path.exists(built_file):
        if built_file != final_file:
            shutil.move(built_file, final_file)
        print(f"Successfully created: {final_file}")
    else:
        print(f"Warning: Expected output file not found: {built_file}")
        print("Looking for build outputs...")
        for root, dirs, files in os.walk("dist"):
            for file in files:
                print(f"  Found: {os.path.join(root, file)}")

    # Nuitkaが生成した不要なディレクトリを削除
    nuitka_temp_dirs = [
        os.path.join("dist", "twitchTransFN.dist"),
        os.path.join("dist", "twitchTransFN.onefile-build"),
        os.path.join("dist", "twitchTransFN.build"),
    ]
    for temp_dir in nuitka_temp_dirs:
        if os.path.exists(temp_dir):
            print(f"Removing Nuitka temp directory: {temp_dir}")
            shutil.rmtree(temp_dir)

    # distディレクトリ内の最終的なファイルリストを表示
    print("\nFinal dist contents:")
    for item in os.listdir("dist"):
        item_path = os.path.join("dist", item)
        if os.path.isfile(item_path):
            print(f"  File: {item}")
        else:
            print(f"  Dir: {item}/")

    print(f"\nBuild for {os_name} ({arch}) completed.")

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
