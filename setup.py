from setuptools import setup, find_packages

setup(
    name='constrained-values',
    version='0.1.0',
    packages=find_packages(),
    author='OODesigns',
    author_email='your.email@example.com',
    description='A library for creating constrained value objects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/OODesigns/constrained-values',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.6',
)
