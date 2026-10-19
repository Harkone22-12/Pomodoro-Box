import type { Server } from "socket.io";

import { registerDhtFlow } from "./dht.flow";
import { registerLightFlow } from "./light.flow";
import { registerRfidFlow } from "./rfid.flow";
import { registerTimerFlow } from "./timer.flow";
import { registerLcdFlow } from "./lcd.flow";

// Every flow exposes one register function; server.ts calls them all.
// (The focus flow is firmware-only, so it has no backend file.)

export interface FlowContext {
  io: Server;
}

export const flows: Array<(ctx: FlowContext) => void> = [
  registerDhtFlow,
  registerLightFlow,
  registerRfidFlow,
  registerTimerFlow,
  registerLcdFlow,
];
