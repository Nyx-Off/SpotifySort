from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spotifysort",
    version="2.0.0",
    author="SpotifySort Team",
    description="Organize your Spotify library into smart playlists by genre, mood, decade, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nyx-Off/SpotifySort",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.10",
    install_requires=[
        "spotipy>=2.23.0",
        "requests>=2.31.0",
        "Flask>=3.0.0",
        "Flask-CORS>=4.0.0",
        "Flask-Session>=0.5.0",
        "click>=8.1.0",
        "PyYAML>=6.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "spotifysort=spotifysort.cli:main",
        ],
    },
    include_package_data=True,
)
