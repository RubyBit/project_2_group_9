---
author: Ilma Jaganjac, Marvin ..., Pravesha ..., Angelos ...

title: "..."
image: ""
date: 04/04/25
summary: |-
  Sustainability in software engineering is crucial when it comes to reducing the environmental footprint of our society. Therefore, creating more efficient and long-lasting software plays a key role in achieving this goal. Governments keep their software open-source, promoting transparency together with collaboration and showing its commitment to accessibility, accountability, and long-term sustainability. However, government open-source projects often lack accessibility, since datasets are often not available, there exist language barriers and often have an absence of incentives for broad usage. These reasons make it hard for researchers to assess the sustainability of these government software projects. For this reason, this project proposes a dataset based on government-developed open-source software in order to make it more accessible for researchers doing research in sustainability practices of government software. The dataset has a focus on sustainability metrics based on development history, buildability and presentence of documentation. Additionally, we propose a dashboard to visualize various repository metrics of the government software projects, providing insights into the overall health, progress, and sustainability of their software projects. By exploring different open-source projects from multiple different countries, this dataset and dashboard provide insights into the sustainability of government software, making improvements in sustainability practices more accessible to researchers and governments.
  
---

# Abstract
Sustainability in software engineering is crucial when it comes to reducing the environmental footprint of our society. Therefore, creating more efficient and long-lasting software plays a key role in achieving this goal. Governments keep their software open-source, promoting transparency together with collaboration and showing its commitment to accessibility, accountability, and long-term sustainability. However, government open-source projects often lack accessibility, since datasets are often not available, there exist language barriers and often have an absence of incentives for broad usage. These reasons make it hard for researchers to assess the sustainability of these government software projects. For this reason, this project proposes a dataset based on government-developed open-source software in order to make it more accessible for researchers doing research in sustainability practices of government software. The dataset has a focus on sustainability metrics based on development history, buildability and presentence of documentation. Additionally, we propose a dashboard to visualize various repository metrics of the government software projects, providing insights into the overall health, progress, and sustainability of their software projects. By exploring different open-source projects from multiple different countries, this dataset and dashboard provide insights into the sustainability of government software, making improvements in sustainability practices more accessible to researchers and governments.

# Introduction

# Related work

# Solution description


## Social Sustainability in Government Open Source Software
Ensuring that government-developed software can achieve long-term impact, it must demonstrate social sustainability. Social sustainability includes that the software should be maintainable, accessible, inclusive, and open to collaboration over time.  In order to make it easier to assess how different government-software projects perform in terms of social sustainability, we collected various metrics from the GitHub repositories of the projects for our dataset. Although these metrics might be highly technical attributes, they also pose as indicators for social sustainability, primarily around openness, community involvement, accessibility, and long-term maintainability. Below, a table is provided that outlines the metrics that we extracted from the government repositories, together with their interpretation from an social sustainability perspective.


| **Collected Metric**                       | **CSV Metric Name(s)**                                   | **Social Sustainability Relevance**                                                                 |
|-------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Development history           | `total_commits`, `repo_age_months`                        | Indicates openness, transparency and activeness of the repository; this is essential for understanding project evolution and collaboration. |
| Number and diversity of contributors      | `num_contributors`, `external_pr_percentage`              | Indicates whether development is centralized or open to the community; more diverse developers indicate accessibility. |
| Commit activity / most recent commit          | `commit_frequency_per_month`, `days_since_last_commit`    | Indicates if the repository is still being actively used and whether the project has long-term maintainability 
| Documentation (README, requirements, etc) | `has_readme`, `has_contributing`, `has_license`           | Enables understandability of the reposptory and accesibility of easy onboarding; this supports knowledge sharing.                                 |
| Buildability of the software              | `has_cicd`                                                | Ensures others can reuse or improve the code; this is a basis requirement for sustainable use of projects.                 |
| Open issues and pull requests          | `open_issues`, `closed_issues`, `merged_pr_percentage`    | Indicate collaboration, openess to feedback, and contributions by the community                          |

We examined these metrics for multiple repositories across various countries, aiming to map the technical state of the government repositories. Additionally, we aimed to demonstrate the social sustainability patterns, such as how accessible, inclusive, and maintainable these systems are over time. With these insights, governments can more easily understand their strenghts and weaknesses of their software projects practices. Identifying areas of improvement will be simlpified, together with promoting a more inclusive and transparent digital infrastructure. Moreover, this dataset gives researchers access to a structured and clear data that supports the study of social sustainability in government open-source software. This enables deeper analysis of development practices, policy impacts, and comparison in practices between various countries.

## Streamlit

## Data analysis

# Discussion

## Validation

## Limitations & Future work

# Conclusion