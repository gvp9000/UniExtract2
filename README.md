# Universal Extractor 2 _(UniExtract2)_

[![Download](https://img.shields.io/badge/download-success?style=for-the-badge)](https://github.com/gvp9000/UniExtract2/releases)

Universal Extractor 2 is a tool designed to **extract files from a wide variety of archive, installer, disk image, game archive, and multimedia formats**.

Unlike most archiving programs, UniExtract is not limited to **standard archives** such as `.zip` and `.rar`. It can also handle **application installers**, **disk images**, **game archives**, and various **multimedia files**. An overview of supported file types can be found [here](/docs/FORMATS.md).

This program is an unofficial updated and extended version of the [original UniExtract by Jared Breland](http://legroom.net/software/uniextract). After development of the original version stopped, several community-maintained forks appeared. This fork continues to maintain and extend Universal Extractor 2 with updated extractors, bug fixes, and additional format support.

## New features in version 2

- 500+ new supported file types
- Batch mode
- Scan-only mode to detect the type of any given file
- Built-in updater
- Support for password lists for common archives
- Improved context menu integration and status box
- Better and faster file analysis
- Silent mode without prompts
- Many interface improvements and redesigned dialogs
- Resource usage and speed improvements, plus numerous bug fixes

See the [changelog](docs/changelog.txt) for a complete log of all improvements.

## Download

Get the latest version [here](https://github.com/gvp9000/UniExtract2/releases).

###### Virus alert?

Universal Extractor does not contain malware. Some antivirus programs may occasionally misidentify files inside UniExtract's program directory. If you downloaded UniExtract from the official source at `https://github.com/gvp9000/UniExtract2`, such detections may be false positives. A more detailed explanation can be found [here](/docs/ANTI-MALWARE.md). If you encounter a false positive, please report it [here](https://github.com/gvp9000/UniExtract2/issues/8).

###### 'Windows protected your PC'?

Modern versions of Windows include *Microsoft Defender SmartScreen*, which may warn about applications that have little or no established reputation. This warning does not necessarily indicate malware and may appear more often after a new UniExtract release. The warning may disappear over time as the executable gains SmartScreen reputation. If you downloaded UniExtract from the official source and want to continue, click **More info**, then **Run anyway**.

###### System requirements

Universal Extractor 2 is intended for Windows. Support for legacy Windows versions is limited and may depend on the bundled third-party extractors.

- Modern Windows versions are recommended.
- Windows 7 may require additional TLS configuration for online features such as sending feedback. See [Microsoft's TLS 1.1/1.2 guidance](https://support.microsoft.com/en-us/help/3140245/update-to-enable-tls-1-1-and-tls-1-2-as-default-secure-protocols-in-wi).
- Windows XP compatibility is currently **not verified**. Some or all functionality, especially online features and newer third-party extractors, may not work.

###### Updating

Universal Extractor 2 includes a built-in updater. You will receive a notification when a new version is available. You can also check manually at any time using **Help → Check for Updates**.

Stable releases are published periodically. If you want to receive development builds, you can [opt in to beta updates](#beta--development-builds).

**Do not manually replace individual files in UniExtract's program directory unless you know exactly what you are doing. Use the built-in updater to keep the installation consistent.**

###### Older versions

Older versions can be found on the [Releases](https://github.com/gvp9000/UniExtract2/releases) page. They are provided mainly for historical or troubleshooting purposes. In general, the latest version is recommended.

###### Uninstalling

- If you enabled **context menu entries**, open Universal Extractor and select `Edit` > `Context Menu Entries`. Uncheck both `enabled` checkboxes and click `OK`.
- If you saved the program to a directory without write access (for example, `C:\Program Files`) and want to remove all settings, remove the directory `%APPDATA%\Bioruebe\UniExtract`. Open File Explorer, enter `%APPDATA%\Bioruebe` in the address bar, and delete the `UniExtract` directory.
- Finally, delete the program directory.

## FAQ

#### Is there a portable version?

Universal Extractor itself is largely portable, with some exceptions:

- Enabling context menu entries creates registry entries.
- UniExtract uses many different third-party extractors to support a wide range of file types. Some of them may leave traces on the system. Extraction of common archives and installers can generally be considered portable, while other formats may not be fully portable.
- Storing Universal Extractor in a directory without write access (for example, `C:\Program Files`) enables multi-user mode. In that case, configuration files are stored in `%APPDATA%\Bioruebe\UniExtract` (`C:\Users\YourUsername\AppData\Roaming\Bioruebe\UniExtract`).

#### Why are there many different versions, modifications, and repacks of Universal Extractor?

When development of the original UniExtract stopped, people from around the world continued to update and improve it. Some versions mainly updated the third-party tools used by Universal Extractor, while others added new features. As a result, the available versions differ in supported formats, bundled tools, and functionality.

This fork continues the open-source Universal Extractor 2 codebase on GitHub. Over the years, the project has incorporated many user requests, added support for additional file formats, and introduced numerous convenience features. Community contributions include translations, bug reports, testing, discussions, and code improvements.

Universal Extractor 2 may occasionally fail to unpack a file that another Universal Extractor variant can handle. If you need access to a particular archive and extraction fails, you can report the problem on the [issue tracker](https://github.com/gvp9000/UniExtract2/issues).

#### Can UniExtract (re)compress files?

No. This tool was designed as an extraction utility.

## Beta / Development Builds

You can opt in to receive current development builds of Universal Extractor 2. Open the preferences dialog from the `Edit` menu and enable **Install beta updates**. The next time you check for updates, you will receive the development build instead of the latest stable release.

After disabling **Install beta updates**, check for updates again to return to the latest stable version when applicable.

## Reporting bugs

If you encounter a problem with UniExtract, please report it. There are several ways to do so:

- If you have a GitHub account, you can **[open an issue](https://github.com/gvp9000/UniExtract2/issues)**. This is the preferred method for **feature requests**, **suggestions**, and **general technical problems**.
- From within Universal Extractor, select **Give feedback** from the **Help** menu. This is the preferred method for reporting **failed extractions**. If extraction is unsuccessful, UniExtract may automatically offer to send feedback, depending on your settings. This feedback includes a log containing diagnostic information that can help identify the problem.
- You can also contribute code by opening a [pull request](https://github.com/gvp9000/UniExtract2/pulls).

## Building from Source

1. Download and install [AutoIt](https://www.autoitscript.com/site/autoit/downloads/).
2. Download and install [SciTE](https://www.autoitscript.com/site/autoit-script-editor/downloads/) (optional).
   - Running UniExtract through SciTE has the additional benefit of real-time logging in the built-in console.
3. Clone this repository **or** download a source archive and extract it to a folder of your choice.
4. Open `UniExtract.au3` in SciTE and press `F5` to run it in debug mode or `F7` to build an executable. Alternatively, compile `UniExtract.au3` using Aut2Exe.
5. Download the required program files that are not part of the source package:
   1. Run the program.
   2. UniExtract will display a message that the program files are incomplete. Select `No`.
   3. Go to `Edit` → `Preferences` and enable **Install beta updates**.
   4. Select `Help` → `Check for Updates`, then confirm the update when prompted.
6. If the main executable is overwritten during the update process, rebuild it as described in step 4.

## Contributions

Contributions in the form of ideas, bug reports, code commits, documentation improvements, translations, and testing are welcome. Help may be needed to update translations for various languages. If you can translate UniExtract, see the corresponding issue (#2) or open the language file in the `/lang` subdirectory and check for missing strings. English and German can be used as reference translations where they are up to date.

Feel free to submit bug reports or feature requests using the [issue tracker](https://github.com/gvp9000/UniExtract2/issues) or the built-in feedback window in Universal Extractor, available from the `Help` menu. The file `todo.txt` is a leftover from the original Universal Extractor project and is used only for development notes.

## License

Universal Extractor is licensed under **GPLv2**. See `LICENSE` for the full legal text.

As stated by the original project author, code (functions, UDFs, etc.) written from scratch by that author and not otherwise subject to copyleft may also be used under the terms of the BSD 3-clause license.

Universal Extractor (gvp9000 version) uses [Detect-It-Easy by horsicq](https://github.com/horsicq/detect-it-easy), [TrIDLib by Marco Pontello](http://mark0.net/code-tridlib-e.html), several [7-Zip plugins by Dec Software](https://www.tc4shell.com/en/7zip/), and many other tools and libraries to support as many file formats as possible. Please consider supporting the authors of the software [listed here](/docs/helper_binaries_info.txt).

Please note that Universal Extractor includes third-party software with licenses that differ from the license of the main program. Specifically, **some extractors do not allow commercial use**. If you intend to use the software commercially, check the individual license files in the `/docs` subdirectory and the [helper binary information file](docs/helper_binaries_info.txt) first.

You may remove third-party tools from the `/bin` subdirectory if their licenses do not fit your use case, although doing so will reduce the range of supported formats.
