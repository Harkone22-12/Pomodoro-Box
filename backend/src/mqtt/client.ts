// Shared MQTT connection to the broker, used by every backend flow.
// Owner: minh

export type MessageHandler = (payload: unknown, topic: string) => void;

// TODO(minh): connect to process.env.MQTT_URL (with optional username and
// password), log connect / reconnect / error, resolve once connected.
export async function connectMqtt(): Promise<void> {
  throw new Error("TODO(minh): connectMqtt not implemented");
}

// TODO(minh): JSON.stringify the payload and publish it to topic.
export function publish(topic: string, payload: object): void {
  throw new Error("TODO(minh): publish not implemented");
}

// TODO(minh): subscribe to topic and call handler with the parsed JSON;
// ignore (and log) messages that are not valid JSON.
export function subscribe(topic: string, handler: MessageHandler): void {
  throw new Error("TODO(minh): subscribe not implemented");
}
