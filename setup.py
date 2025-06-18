from setuptools import find_packages, setup

# reading long description from file
with open("README.md", encoding="utf-8") as file:
    long_description = file.read()


# specify requirements of your package here
REQUIREMENTS = []


# calling the setup function
setup(
    name="bouyomichan",
    version="0.1.1",
    description="Text to speech interface for BouyomiChan",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="yumimint",
    author_email="i.yumimint@gmail.com",
    url="https://github.com/yumimint/bouyomichan",
    py_modules=["bouyomichan"],
    license="Apache License 2.0",
    packages=find_packages(include=["bouyomichan"]),
    install_requires=REQUIREMENTS,
)
