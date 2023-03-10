resources:
  - deployment.yaml
  - service.yaml
  - ingress.yaml

# Set prefix to all resource names
# Also to the ones in Ingress rules
namePrefix: ${name}-

# Add labels to resources
# Also adds them to service selectors
commonLabels:
  gestor/name: "${name}"

commonAnnotations:
  gestor/commit: "${commit}"
  gestor/branch: "${branch}"
  gestor/repository: "${repository}"
  gestor/pull_request: "${pull_request}"
% for key, value in labels.items():
  gestor/${key}: "${value}"
% endfor

# Generate a ConfigMap with scripts and environment variables
configMapGenerator:
  - name: environmentvars
    literals:
      - CI_PULL_REQUEST=${pull_request}
      - CI_REPO=${repository}
      - COMMIT=${commit}
      - BRANCH=${branch}
      - GITHUB_TOKEN=secret

patches:
  - target:
      kind: Ingress
      name: erpserver
    # TODO: Value should be set dynamically
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: ${name}.${domain}
