import type { Socket } from "socket.io-client";

// Single shared Socket.IO client. Event names are listed in docs/topics.md.
// Owner: hao

// TODO(hao): create one io() connection (same origin, proxied by Vite)
// and return it on every call.
export function getSocket(): Socket {
  throw new Error("TODO(hao): getSocket not implemented");
}
