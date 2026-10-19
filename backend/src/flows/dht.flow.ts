import type { FlowContext } from "./index";

// study/dht {"temp", "hum"} -> MongoDB time series -> Socket.IO -> chart.
// Advanced: time-series storage, history API for the chart, own analysis model.
// Owner: member1

// TODO(member1): define the reading model (time-series collection), subscribe
// to TOPIC_DHT, validate and store each reading, emit it to clients, add a
// history route for the chart, and build your analysis model.
export function registerDhtFlow(ctx: FlowContext): void {}
