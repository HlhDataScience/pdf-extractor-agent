# cyberbullying-detection

An approach to the agentic workflow combining classic DL and MLOps methodology.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)
- [ToDos](#ToDos)
- [Done](#done)

## Introduction

cyberbullying-detection is a Python project designed to combine classic DL and MLOps methodology. This project has been refactored to include two main directories: `images` for the dockerization of the production environment and `src` as the main source code for training and production testing.

The project now features several interfaces using Python protocols and abstract base classes (ABCs). The use of ABCs allows us to define a clear and consistent interface for our components, ensuring that any subclass implements the required methods. This promotes code reusability and maintainability, as developers can easily understand and extend the functionality of the project.

Additionally, Python protocols provide a way to define structural subtyping, allowing us to specify the expected behavior of objects without requiring them to inherit from a specific class. This flexibility enhances the reusability of our code, as it allows different classes to be used interchangeably as long as they adhere to the defined protocol.

We have also transitioned from using Poetry to `uv` for dependency management. This change was made to streamline our workflow and simplify the management of dependencies. `uv` offers a more lightweight and efficient approach, making it easier to handle project dependencies while maintaining compatibility with our development practices. We continue to utilize pre-commit hooks for code formatting and linting to ensure code quality and consistency across the project.

## Installation

"To be done"

## Usage

to be done.

## Contributing

## License

## Author

Héctor López Hidalgo

## ToDos

- ~~Clean the dataset and combine it in the EDA first approach~~
- ~~Create a comprehensive descriptive statistics to understand the data in the eda_jupyter notebook.~~
- Create a functional style pipeline to preprocess the data for ModernBert Sequence Classification.
- Create a functional style pipeline to train the model with Protocols.
- Track the experiments and compare them. Select the best overall result based on the Sequence classification metrics.
- Select the best open-source decoder-only llm for the langchain architecture.
- Design a semantic router for the model. Check AurelioAI to do so.

## Done

- Dataset cleaned and prepared for statistical analysis.
- Dataset analysed with plots and statistical insides.