# chess.js source-map warning fix

The frontend Dockerfiles create `/app/node_modules/src/chess.ts` before React starts and remove stale chess.js source-map references.

Rebuild after replacing the project:

```bat
docker compose down
docker compose build --no-cache frontend
docker compose up
```

If Docker still reuses an old anonymous node_modules volume, run `docker compose down -v` once and rebuild.
