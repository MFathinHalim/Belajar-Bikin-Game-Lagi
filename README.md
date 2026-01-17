# 🐸 Ninja Frog Platformer (Learning Project)

A simple 2D platformer game made with **Python + Pygame**.

You play as a **ninja frog** who jumps, wall-sticks, and wall-jumps across platforms to reach a **big coin** at the end of the level. Fall too far and it is game over. Touch the coin and you win. Simple rules, simple pain.

---

## 🎮 Game Concept

* **Character**: A ninja frog (agile, fast, sticks to walls like it owns the place)
* **Goal**: Reach the **big coin** to finish the level
* **Challenge**:

  * No floor except near spawn
  * You must rely on **parkour mechanics**
  * Wall stick + wall jump are essential
* **Lose condition**: Falling below the level
* **Win condition**: Touching the coin

---

## 🕹️ Controls

* **A / D** → Move left / right
* **SPACE** → Jump
* **Hold A or D on a wall** → Wall stick
* **SPACE while wall sticking** → Wall jump

---

## ⚙️ Mechanics Implemented

* Gravity & jumping
* Double jump
* Wall stick
* Wall jump
* Camera scrolling (horizontal)
* Text-based level loading
* Win & lose screens

---

## 🗺️ Level System

Levels are loaded from a `.txt` file using simple characters:

* `P` → Player spawn
* `M` → Platform block
* `F` → Goal (big coin)
* `.` → Empty space

Each character represents **one block**.

This makes level design fast, readable, and beginner-friendly.

---

## 🧠 Purpose of This Project

This project is **not meant to be a polished game**.

It was created for:

* Learning **Pygame basics**
* Understanding **platformer physics**
* Practicing **collision handling**
* Experimenting with **wall mechanics**
* Having fun while breaking things and fixing them again

The development process:

* Followed **online tutorials**
* Read documentation
* Trial & error
* Help from **internet resources and AI**

This is purely a **learning project**.

---

## 🛠️ Tech Stack

* **Python**
* **Pygame**
* Text-based level design
* Free pixel assets (for learning purposes)

---

## 📌 Notes

* Code is intentionally simple and readable
* Not optimized
* Not production-ready
* Built to understand concepts, not to ship a commercial game

---

## 📚 Disclaimer

All assets and logic are used **for educational purposes only**.
This project exists to learn, experiment, and improve programming skills.
