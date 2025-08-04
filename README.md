Dialogue Venture Game Engine (DVGE)
A powerful, intuitive, node-based editor for creating branching dialogue and narrative-driven experiences. Export your story to a single, playable HTML file with zero hassle.

✨ Features
Visual Node-Based Editor: Craft complex narratives by visually connecting dialogue nodes, choices, and story branches.

Dynamic Storytelling:

Player Stats: Define character attributes (e.g., Strength, Charisma, Sanity) that can influence the story.

Inventory System: Give players items that can unlock new dialogue options or paths.

Story Flags: Use boolean flags to track world states, character knowledge, or completed quests.

Conditional Logic: Make choices available only if the player meets certain stat, item, or flag conditions.

Character & World Building:

Set custom themes, background images, and chapter titles for each node.

Customize node colors for better organization.

One-Click HTML Export: Package your entire game, including images and logic, into a single, self-contained HTML file that can be played anywhere.

Undo/Redo & Search: A robust editor with essential quality-of-life features to make development a breeze.


🚀 Getting Started
There are two ways to use the Dialogue Venture Game Engine: running the pre-built executable or running it from the source code.

Option 1: Running the Executable (Easiest)
Go to the Releases page of this repository.

Download the DialogueVenture.exe file from the latest release.

Run the file. No installation is needed!

Option 2: Running from Source Code
This is for developers who want to modify the engine or contribute to the project.

Prerequisites:

Python 3.8+

1. Clone the Repository:

git clone https://github.com/BatuhanUtebay/DVEngine.git
cd DVEngine

2. Install Dependencies:
It's recommended to use a virtual environment.

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required packages
pip install -r requirements.txt

3. Run the Application:

python main.py

📖 How to Use
Right-click on the grid to create a new dialogue node.

Select a node to edit its properties in the right-hand panel. You can change its ID, NPC name, dialogue text, and more.

Add Choices to a node via the "Choices" tab or the "+ Add Choice" button on the node itself.

Connect Nodes by clicking and dragging from a choice's circular handle to another node.

Define Player Stats, Items, and Flags in their respective tabs to create a dynamic story.

Use Conditions and Effects on choices to check against and modify player data.

Export Your Game using the "Export to HTML Game" button to generate a playable file.

🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Please see the CONTRIBUTING.md file for more detailed guidelines on our development process.

📜 License
Distributed under the MIT License. See LICENSE for more information.
