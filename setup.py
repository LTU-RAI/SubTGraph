from setuptools import setup, find_packages

setup(
    name='subtgraph',  # Replace with your package name
    version='0.1.0',
    description='A short description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Fernando Labra Caso',
    author_email='fernando.labra.caso@gmail.com',
    url='https://github.com/fernand0labra/rai-subtgraph.git',
    packages=find_packages(exclude=["imgs*"]),
    install_requires=[
        # Add your package dependencies here, e.g.,
        # 'requests>=2.20.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update if needed
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
