from setuptools import find_packages, setup

with open("requirements.txt") as fp:
    install_requires = fp.read()

setup(
    name="dino",
    version="0.0.1",
    description="DICOM node",
    author="Andrii Yurchuk",
    author_email="ay@mntw.re",
    install_requires=install_requires,
    packages=find_packages(),
)
