import { createServer } from "node:http";
import next from "next";

const app = next({
  dev: true,
  hostname: "127.0.0.1",
  port: 32177,
  conf: { distDir: ".next-playwright" },
});
await app.prepare();

const handle = app.getRequestHandler();
const server = createServer((request, response) => handle(request, response));
server.listen(32177, "127.0.0.1");

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => server.close(() => process.exit(0)));
}
