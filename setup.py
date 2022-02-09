import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyBitrix",
    version="1.2.6",
    install_requires=['requests', 'aiohttp'],
    author="Aleksandr Lenets",
    author_email="wowgonit@gmail.com",
    description="PyBitrix is my lightweight implementation of Bitrix 24 REST API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/momoru-kun/PyBitrix",
    packages=setuptools.find_packages(),
    keywords='bitrix24 rest api bx24',
    classifiers=[
        "Development Status :: 5 - Production/Stable",

        'Intended Audience :: Developers',

        'Natural Language :: Russian',
        'Natural Language :: English',

        'Topic :: Software Development :: Libraries :: Python Modules',

        "Programming Language :: Python :: 3",

        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)