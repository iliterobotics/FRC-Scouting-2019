import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="frc1885-scouting-2019",
    version="0.0.1",
    author="Rahul Yarlagadda",
    author_email="knufire@gmail.com",
    description="Python CLI Application for processing exported scouting data from Airtable",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iliterobotics/FRC-Scouting-2019",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=['click','click-shell','pyfiglet']
)