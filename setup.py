from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fileflyer',
    version='0.1',
    author='Will Han',
    author_email='xingheng.hax@qq.com',
    license='MIT',
    keywords='twitter cli media downloader',
    url='https://github.com/python-cli/fileflyer',
    description='Host files to GitHub repository with ease.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['fileflyer'],
    include_package_data=True,
    install_requires=[
        'coloredlogs>=10.0',
        'configparser>=4.0.2',
        'click>=7.0',
    ],
    entry_points='''
        [console_scripts]
        fileflyer=main:cli
    ''',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Unix Shell',
        'Topic :: System :: Shells',
        'Topic :: Terminals',
      ],
)
