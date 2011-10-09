from distutils.core import setup, Extension

pkg = 'Extensions.OroscopoItalia'
setup (name = 'enigma2-plugin-extensions-oroscopoitalia',
       version = '0.1',
       license='GPLv2',
       url='https://github.com/E2OpenPlugins',
       description='OroscopoItalia',
       long_description='Italian horoscope',
       author='meo',
       author_email='lupomeo@hotmail.com',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data={pkg: ['*.png', 'icons/*.png']}
      )
