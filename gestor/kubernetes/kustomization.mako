resources:
  - deployment.yaml
  - service.yaml

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
  gestor/server_port: "${server_port}"
  gestor/ssh_port: "${ssh_port}"
  gestor/created_at: "${created_at}"
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
      kind: Service
      name: erpserver
    patch: |-
      - op: replace
        path: /spec/ports/0/nodePort
        value: ${server_port}
      - op: replace
        path: /spec/ports/1/nodePort
        value: ${ssh_port}
