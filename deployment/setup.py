from setuptools import setup, find_packages

setup(
    name="license_checker",
    version="0.1.0",
    description="A library for detecting licenses from websites and processing ToS text.",
    author="Tomáš Peterka",
    author_email="petert13@cvut.cz",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "protego",
        "validators",
        "huggingface_hub",
        "google-genai",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.10",
)