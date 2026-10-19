import type { FlowContext } from "./index";

// Web timer form -> Socket.IO -> study/timer {"minutes"} -> ESP32 buzzer.
// Owner: hao

// TODO(hao): listen for the "timer:set" event from clients, validate
// minutes, publish to TOPIC_TIMER.
export function registerTimerFlow(ctx: FlowContext): void {}
