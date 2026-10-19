import type { FlowContext } from "./index";

// study/rfid {"uid", "action": "start"|"stop"} -> study sessions in MongoDB.
// Advanced: weekly email report (src/notify/email.ts).
// Owner: duong

// TODO(duong): define the session model, subscribe to TOPIC_RFID, open and
// close sessions per uid, emit to clients, schedule the weekly email.
export function registerRfidFlow(ctx: FlowContext): void {}
