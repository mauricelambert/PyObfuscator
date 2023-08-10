import PyObfuscator as package
from setuptools import setup

setup(
    name=package.__name__,
    version=package.__version__,
    py_modules=[package.__name__],
    install_requires=[],
    author=package.__author__,
    author_email=package.__author_email__,
    maintainer=package.__maintainer__,
    maintainer_email=package.__maintainer_email__,
    description=package.__description__,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url=package.__url__,
    project_urls={
        "Documentation": "https://mauricelambert.github.io/info/python/security/PyObfuscator.html",
        "Executable": "https://mauricelambert.github.io/info/python/security/PyObfuscator.pyz",
    },
    classifiers=[
        "Topic :: Security",
        "Environment :: Console",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points={
        "console_scripts": [
            "PyObfuscator = PyObfuscator:main",
        ],
    },
    python_requires=">=3.9",
    keywords=[
        "Python",
        "Obfuscation",
        "Security",
    ],
    platforms=["Windows", "Linux", "MacOS"],
    license=package.__license__,
)
