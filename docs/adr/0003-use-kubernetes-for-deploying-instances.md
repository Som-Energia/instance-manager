# 3. Use Kubernetes for deploying ERP server instances

Date: 28-02-2023

## Status

Accepted

## Context

Our ERP instance manager will need to run multiple independent ERP server instances. We will containerize the ERP server using Docker to achieve platform independence and pack all dependencies. Additionally, we will containerize three different database technologies for each ERP server instance.

As a result, we will have many containers running simultaneously, which could be challenging to manage. We will need a container orchestration system to manage and scale our container-based ERP server deployments.

## Decision

We decided between two options: Kubernetes and Docker Swarm. Because of the more advanced features and the larger ecosystem and community of Kubernetes, we decided to use it instead of Docker Swarm.

## Consequences

We will need to spend time learning Kubernetes. Also, we will need to install some tools to develop and test our application in a local environment. Finally, we will need to plan a deployment strategy for production.
