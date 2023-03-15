from setuptools import setup

with open("requirements.txt") as f:
    required = f.read().splitlines()


setup(
    name="convo",
    version="0.0.0",
    description="",
    url="https://github.com/sshh12/csgo-match-prediction",
    author="Shrivu Shankar",
    license="MIT",
    packages=["convo"],
    include_package_data=True,
    install_requires=required,
)
