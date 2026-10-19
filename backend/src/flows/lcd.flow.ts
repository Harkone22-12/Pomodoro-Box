import type { FlowContext } from "./index";

// Web text -> Socket.IO -> study/lcd {"text"} -> ESP32 LCD1602.
// Owner: member3

// TODO(member3): listen for the "lcd:set" event from clients, validate and
// trim text for a 16x2 LCD, publish to TOPIC_LCD.
export function registerLcdFlow(ctx: FlowContext): void {}
