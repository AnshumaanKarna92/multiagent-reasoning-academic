"""
Setup configuration for multi-agent problem-solving system.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multiagent-reasoning-academic",
    version="1.0.0",
    author="Anshumaan Karna",
    author_email="anshumaan@example.com",
    description="Research implementation of a multi-agent problem-solving architecture with teacher, student, evaluator, and coordinator agents working collaboratively through structured conversation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AnshumaanKarna92/multiagent-reasoning-academic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "ollama>=0.0.1",
    ],
    keywords="multi-agent reasoning problem-solving AI collaboration",
    project_urls={
        "Bug Reports": "https://github.com/AnshumaanKarna92/multiagent-reasoning-academic/issues",
        "Source Code": "https://github.com/AnshumaanKarna92/multiagent-reasoning-academic",
    },
)
