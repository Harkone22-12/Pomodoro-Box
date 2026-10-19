import type { Socket } from "socket.io-client";

// Single shared Socket.IO client. Event names are listed in docs/topics.md.
// Owner: member3

// TODO(member3): create one io() connection (same origin, proxied by Vite)
// and return it on every call.
export function getSocket(): Socket {
  throw new Error("TODO(member3): getSocket not implemented");
}
