# scripts/test.sh
#!/bin/bash
docker compose -f docker/docker-compose.yml run --rm web pytest