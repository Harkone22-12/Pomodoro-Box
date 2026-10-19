import type { Server as HttpServer } from "http";
import type { Server } from "socket.io";

// Socket.IO server setup. Event names are listed in docs/topics.md.
// Owner: hao

// TODO(hao): create the Socket.IO server on httpServer with CORS for
// process.env.CLIENT_ORIGIN and return it.
export function setupSocket(httpServer: HttpServer): Server {
  throw new Error("TODO(hao): setupSocket not implemented");
}
