# 4. In-memory SQLite database

Date: 28-02-2023

## Status

Accepted

## Context

Our ERP server instance manager will keep track of all the deployed instances for monitoring and management purposes.

## Decision

After considering different options, we have decided to use an in-memory SQLite database to keep track of all deployed ERP server instances. This decision is based on the following factors:

- Low resource usage
- Easy to setup, integrated with Python
- We want to store little information
- Persistence is not needed because we can restore the state from Kubernetes
- Simple

## Consequences

This decision will have the following consequences:

- Limited scalability
- Limited storage capacity
- No data persistence

However, in our use case, these consequences do not concern us.
