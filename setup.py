from setuptools import setup, find_packages

setup(
    name="src",  
    version="0.1.0",
    author="Janvita Reddy",
    author_email="reddyjanvita11@gmail.com",
    description="A brief description of your project",
    packages=find_packages(),  # Automatically finds sub-packages
    install_requires=[],  # Add dependencies if needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Specify the minimum Python version
)
