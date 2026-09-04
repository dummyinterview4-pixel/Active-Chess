FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund
# chess.js 1.4.0 ships a stale sourceMappingURL pointing to a missing source file.
RUN mkdir -p /app/node_modules/src \
    && printf '%s\n' '// Placeholder source file for chess.js source-map resolution.' > /app/node_modules/src/chess.ts \
    && find /app/node_modules/chess.js -type f -name '*.js' -exec sed -i '/sourceMappingURL.*chess\.ts/d' {} + || true

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
