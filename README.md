# Until Then Translation Installer

  > **IMPORTANT:** This is the *very* first version of the installer that I made. It's currently obsolete. The logic served as the foundation for newer, more optimized, and cross-platform versions developed later.
> 
> **Please, for your own sake, check the newer versions of this project:**
> * ### [**Version 2.0 (Go/Wails)**](https://github.com/flyri0/ut-translation-setup-v2)
> *  [Version 1.0 (Python/PyQt)](https://github.com/flyri0/ut-translation-setup)

---

## About this project

An automated patch installer designed specifically to apply modified assets to games built on the Godot Engine (in this case, *Until Then*).

Developed entirely in **Python** using **Tkinter** for the UI, this tool was created to solve the problem of manual patch installations (which can be pretty complex for non-technical users), handling the extraction and injection of files directly into Godot's `.pck` archives.

### Some context

This tool was born out of necessity to safely and easily distribute (not sending the whole file -- the entire game in legal terms) our PT-BR fan ~~translation~~ localization of *Until Then*. If you are curious about the translation process, decisions, how we managed the project or just some cool curiosities you can check out the **[Translation Bible](https://app.notion.com/p/B-blia-de-Tradu-o-Until-Then-30d34b5540198077b691d65adaab9bf6).** (it's written in Portuguese though!)

## How it works

The core logic relies on automating file manipulation. The script does the following:
1. Locates the target game directory.
2. Extracts specific assets from the `.pck` file.
3. Injects the modified assets.
4. Backs up the original files if requested.
5. Repacks the archive without messing with the original game structure.

It was really functional and stable for quite a while, so much so that it keeps being used as a backup installation alternative to this day.

---

## Special thanks

- [Dmitri Sanikov](https://github.com/DmitriySalnikov): A massive thank you for creating the [Godot PCK Explorer](https://dmitriysalnikov.itch.io/godot-pck-explorer) and the [Inkcpp Localization Editor](https://dmitriysalnikov.itch.io/inkcpp-localization-editor). Without them, the file extraction and repacking logic used here would have been practically impossible. Really, you're awesome! =^)
- [Francisco (flyri0)](https://github.com/flyri0): This man is a hero!! 🙏 For the massive collaboration and for taking the logic of this humble program to cross-platform support, amazing performance and pretty UIs. Thanks to his help, we co-maintained and developed these babies.
