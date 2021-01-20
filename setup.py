import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyBitrix",
    version="1.0.0",
    install_requires=['requests'],
    author="Momoru_kun",
    author_email="wowgonit@gmail.com",
    description="PyBitrix is my lightweight implementation of Bitrix 24 REST API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/momoru-kun/PyBitrix",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)