from setuptools import setup, find_packages

setup(
    name="battery_health_monitor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "matplotlib"
    ],
    entry_points={
        "console_scripts": [
            "battery_health_monitor=src.main:main"
        ]
    },
    author="Achref",
    description="A Python-based desktop application that monitors the health of a Windows laptop battery.",
    url="https://github.com/achref/battery_health_monitor"
)
