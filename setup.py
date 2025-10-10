"""Setup script for weather-tool package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="weather-tool",
    version="0.1.0",
    author="Weather Tool Team",
    author_email="your.email@example.com",
    description="A comprehensive tool for plotting weather time series data for airports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/weather-tool",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "advanced": [
            "plotly>=5.0.0",
            "bokeh>=2.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "weather-tool=weather_tool.cli:main",
        ],
    },
)
