from setuptools import setup, find_packages

setup(
    name="VibeJoy",
    version="1.0.0",
    description="A modern media player with a sleek GUI",
    author="VibeJoy Team",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "Pillow",
        "mutagen",
        "tkinter"
    ],
    entry_points={
        "console_scripts": [
            "vibejoy=main:main"
        ]
    },
    python_requires=">=3.6",
)