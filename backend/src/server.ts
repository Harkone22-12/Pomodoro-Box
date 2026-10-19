// Backend entry point: Express + HTTP server + Socket.IO, then wires up the
// shared connections and every flow.
// Owner: hao

// TODO(hao): create the Express app and HTTP server, call setupSocket(),
// mount authRouter at /api/auth, await connectDb() and connectMqtt(), call
// every function in `flows` (src/flows/index.ts) with { io }, then listen on
// process.env.PORT.
export {};
