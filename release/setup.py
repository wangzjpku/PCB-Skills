from setuptools import setup, find_packages

setup(
    name="kicad-auto-power-designer",
    version="1.0.0",
    description="Automated power supply design tool for KiCad",
    author="Auto Designer",
    author_email="",
    url="https://github.com/yourusername/kicad-auto-power-designer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.20.0",
        "pillow>=9.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'kicad-auto-design=auto_power_design_system:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
