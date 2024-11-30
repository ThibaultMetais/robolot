from pathlib import Path

from setuptools import find_packages, setup

if __name__ == "__main__":
    project_name = "robolot"
    project_description = "A coinche game with integrated AI"
    package_path = Path(__file__).parent
    package_name = project_name

    with open(package_path / package_name / "version.txt") as fp:
        version = fp.read().strip()
    
    with open(package_path / "requirements" / "prod.in") as fp:
        install_requires = fp.readlines()

    with open(package_path / "requirements" / "dev") as fp:
        extra_requires_dev = fp.readlines()

    setup(
        name=project_name,
        version=version,
        description=project_description,
        python_requires=">=3.11",
        packages=find_packages(exclude=["tests"]),
        install_requires=install_requires,
        extras_require={"dev": extra_requires_dev},
        include_package_data=True,
        zip_safe=False
    )