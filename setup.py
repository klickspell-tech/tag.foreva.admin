from setuptools import setup, find_packages

setup(
    name='foreva_profiles',
    version='0.0.1',
    description='Foreva QR Profile Platform',
    author='KlickSpell',
    author_email='hello@forevastore.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['frappe'],
)
