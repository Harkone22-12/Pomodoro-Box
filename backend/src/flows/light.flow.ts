import type { FlowContext } from "./index";

// study/light {"raw", "level"} -> MongoDB -> Socket.IO.
// Advanced: Telegram alert (src/notify/telegram.ts).
// Owner: duong

// TODO(duong): subscribe to TOPIC_LIGHT, validate, store, emit to clients,
// and decide when to send a Telegram alert.
export function registerLightFlow(ctx: FlowContext): void {}
