---
author: Ilma Jaganjac, Marvin ..., Pravesha ..., Angelos ...

title: "..."
image: ""
date: 04/04/25
summary: |-
  Sustainability in software engineering is crucial when it comes to reducing the environmental footprint of our society. Therefore, creating more efficient and long-lasting software plays a key role in achieving this goal. Governments keep their software open-source, promoting transparency together with collaboration and showing their commitment to accessibility, accountability, and long-term sustainability. However, government open-source projects often lack accessibility, since datasets are often not available, there exist language barriers and often an absence of incentives for broad usage. These reasons make it hard for researchers to assess the sustainability of these government software projects. For this reason, this project proposes a dataset based on government-developed open-source software to make it more accessible for researchers researching sustainability practices of government software. The dataset has a focus on sustainability metrics based on development history, buildability and presentence of documentation. Additionally, we propose a dashboard to visualize various repository metrics of government software projects, providing insights into the overall health, progress, and sustainability of their software projects. By exploring different open-source projects from multiple different countries, this dataset and dashboard provide insights into the sustainability of government software, making improvements in sustainability practices more accessible to researchers and governments.
  
---

# Abstract
Sustainability in software engineering is crucial when it comes to reducing the environmental footprint of our society. Therefore, creating more efficient and long-lasting software plays a key role in achieving this goal. Governments keep their software open-source, promoting transparency together with collaboration and showing their commitment to accessibility, accountability, and long-term sustainability. However, government open-source projects often lack accessibility, since datasets are often not available, there exist language barriers and often an absence of incentives for broad usage. These reasons make it hard for researchers to assess the sustainability of these government software projects. For this reason, this project proposes a dataset based on government-developed open-source software to make it more accessible for researchers researching sustainability practices of government software. The dataset has a focus on sustainability metrics based on development history, buildability and presentence of documentation. Additionally, we propose a dashboard to visualize various repository metrics of government software projects, providing insights into the overall health, progress, and sustainability of their software projects. By exploring different open-source projects from multiple different countries, this dataset and dashboard provide insights into the sustainability of government software, making improvements in sustainability practices more accessible to researchers and governments.

# Introduction

Our society becomes more dependent on digital infrastructure, making the environmental and social impacts of software development under more scrutiny. For this reason, there is a strong need for sustainability in software engineering practices, as it is crucial for minimizing our environmental carbon footprint and to ensure that our systems remain relevant and usable in the long-term. Government-developed software plays an important role in promoting sustainable software engineering practices, since it can support sustainability through methods such as open-source development. Moreover, it can also avoid duplication of efforts in tasks and support long-term maintenance. Unfortunately, there is currently a big gap in understanding the sustainability practices of these government open source projects. This reduces the ability to evaluate the long-term impact of these projects in its effectiveness, and areas for improvement.

Several challenges make it hard to study the software practices of government-developed software. In the first palace, there is a lack of accessible datasets that show insights into government development practices. Moreover, there are often language barriers since projects are documented in different languages, limiting global collaboration and understandability of projects. This language barrier also leads to a lack of incentives to adopt and reuse government-developed projects, since the documentation is often unclear and not accessible. Furthermore, without a clear picture of the current state of these projects, it is hard for developers and policymakers to identify areas of improvement to adjust their practices to a more sustainable manner. For these reasons, it is difficult to assess the sustainability practices within government software projects, increasing the need for clear, centralized data from which insights can be easily extracted.

In this project we aim to address these challenges by providing a centralized dataset that contains sustainability metrics of government repositories across different countries, making it easier for researchers studying the sustainability practices within government software. Additionally, we provide a dashboard that contains insights derived from these metrics, allowing governments to view their strengths and weaknesses in terms of sustainable software engineering practices. By providing this dataset together with the dashboard, we aim to promote more sustainable software engineering practices within government software projects, encouraging governments to not only build functional software but also software that is sustainable in the long term.

# Related work

# Solution description


## Social Sustainability in Government Open Source Software
To ensure that government-developed software can achieve long-term impact, it must demonstrate social sustainability. Social sustainability includes that the software should be maintainable, accessible, inclusive, and open to collaboration over time.  To make it easier to assess how different government software projects perform in terms of social sustainability, we collected various metrics from the GitHub repositories of the projects for our dataset. Although these metrics might be highly technical attributes, they also pose as indicators for social sustainability, primarily around openness, community involvement, accessibility, and long-term maintainability. Below, a table is provided that outlines the metrics that we extracted from the government repositories, together with their interpretation from a social sustainability perspective.

| **Collected Metric**                       | **CSV Metric Name(s)**                                   | **Social Sustainability Relevance**                                                                 |
|-------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Development history           | `total_commits`, `repo_age_months`                        | Indicates openness, transparency and activeness of the repository; this is essential for understanding project evolution and collaboration. |
| Number and diversity of contributors      | `num_contributors`, `external_pr_percentage`              | Indicates whether development is centralized or open to the community; more diverse developers indicate accessibility. |
| Commit activity / most recent commit          | `commit_frequency_per_month`, `days_since_last_commit`    | Indicates if the repository is still being actively used and whether the project has long-term maintainability
| Documentation (README, requirements, etc) | `has_readme`, `has_contributing`, `has_license`           | Enables understandability of the reposptory and accesibility of easy onboarding; this supports knowledge sharing.                                 |
| Buildability of the software              | `has_cicd`                                                | Ensures others can reuse or improve the code; this is a basic requirement for sustainable use of projects.                 |
| Open issues and pull requests          | `open_issues`, `closed_issues`, `merged_pr_percentage`    | Indicate collaboration, openness to feedback, and contributions by the community                          |

We examined these metrics for multiple repositories across various countries, aiming to map the technical state of the government repositories. Additionally, we aimed to demonstrate the social sustainability patterns, such as how accessible, inclusive, and maintainable these systems are over time. With these insights, governments can more easily understand the strengths and weaknesses of their software project practices. Identifying areas of improvement will be simplified, together with promoting a more inclusive and transparent digital infrastructure. Moreover, this dataset gives researchers access to structured and clear data supporting social sustainability studies in government open-source software. This enables a more profound analysis of development practices, policy impacts, and comparison of practices between various countries.

## Streamlit

## Data analysis

# Discussion

## Validation

## Limitations & Future work

# Conclusion