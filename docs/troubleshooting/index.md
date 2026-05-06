# Troubleshooting

Common issues and solutions for DClaw Monitor.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-monitor

# Check logs
kubectl logs -n dclaw-monitor deployment/dclaw-monitor-backend

# Check database
kubectl get clusters -n dclaw-monitor
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
