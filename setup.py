from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A powerful, intuitive, node-based editor for creating branching dialogue and narrative-driven experiences."

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    # Split on '>=' to get just the package name for runtime deps
                    if line.startswith(("pytest", "black", "flake8", "mypy", "pre-commit")):
                        continue  # Skip dev dependencies
                    requirements.append(line)
    except FileNotFoundError:
        requirements = ["customtkinter>=5.0.0", "Pillow>=10.0.0", "reportlab>=4.0.0", "markdown>=3.4.0"]
    
    return requirements

setup(
    name="dialogue-venture-game-engine",
    version="1.0.0",
    author="Dice Verce",
    author_email="",
    description="A powerful, intuitive, node-based editor for creating branching dialogue and narrative-driven experiences",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/BatuhanUtebay/DVEngine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "isort>=5.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dvge=main:main",
            "dialogue-venture=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dvge": [
            "templates/*.json",
            "data/*",
            "constants/*.py",
        ],
    },
    keywords=[
        "game-development",
        "visual-novel",
        "interactive-fiction",
        "branching-dialogue",
        "node-editor",
        "story-telling",
        "narrative-design",
        "game-engine",
        "gui",
        "export-html"
    ],
    project_urls={
        "Bug Reports": "https://github.com/BatuhanUtebay/DVEngine/issues",
        "Source": "https://github.com/BatuhanUtebay/DVEngine",
        "Documentation": "https://github.com/BatuhanUtebay/DVEngine/blob/main/README.md",
    },
)