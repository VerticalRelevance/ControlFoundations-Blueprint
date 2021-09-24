import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="blueprint_pipelines",
    version="0.0.1",

    description="Vertical Relevance's Controls Foundation Blueprint",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "blueprint_pipelines"},
    packages=setuptools.find_packages(where="blueprint_pipelines"),

    install_requires=[
        "aws-cdk.core==1.122.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
