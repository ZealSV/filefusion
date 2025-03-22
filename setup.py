from setuptools import setup, find_packages

setup(
    name="filefusion",
    version="0.1.0",
    description="A tool to combine multiple files from a directory into a single document",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.4",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "flake8>=3.9.0",
            "black>=21.5b2",
            "pytest-cov>=2.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "filefusion=filefusion:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Documentation",
        "Topic :: Utilities",
    ],
    license="MIT",
    url="https://github.com/ZealSV/filefusion",
)