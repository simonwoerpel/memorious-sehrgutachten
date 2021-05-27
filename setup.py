from setuptools import setup, find_packages

setup(
    name="memorious-sehrgutachten",
    version="0.3",
    classifiers=[],
    keywords="",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=["memorious", "furl"],
)
