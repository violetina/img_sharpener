from setuptools import setup

setup(name='viaa-sharpener',
      version='0.1',
      description='VIAA image sharpener.',
      long_description='use imagemagick to sharpen image.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: © 2015 VIAA',
        'Programming Language :: Python :: 3.4',
        'Topic :: Image Converting',
      ],
      keywords='convert sharpen image',
      author='Tina Cochet',
      author_email='tina.cochet@viaa.be',
      license='© 2015 VIAA',
      packages=['sharpener'],
      install_requires=[
          'pika',
      ],
      entry_points={
          'console_scripts': ['sharpener=sharpener.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)
