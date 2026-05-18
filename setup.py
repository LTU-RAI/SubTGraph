from setuptools import setup, find_packages

dependencies = [
    'PyYAML',
    'numpy==1.26.4',
    'mathutils==3.3.0',
    'seaborn==0.13.2',
    'matplotlib==3.5.1',
    'scipy==1.15.3',
    'torchmetrics==1.7.4',
    'torch',
]

setup(
    name='subtgraph',
    version='0.1.0',
    packages=find_packages(),
    install_requires=dependencies,
    python_requires='>=3.10',  # Specify Python version compatibility
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    author='Fernando Labra Caso',
    author_email='fernando.labra.caso@gmail.com',
    description='Subterranean World Generator for Simulation Techniques.',
    long_description=open('README.md').read(),  # Ensure you have a README.md file for long description
    long_description_content_type='text/markdown',
    url='https://github.com/fernand0labra/SubTGraph.git',  # Update with your GitHub repo
)