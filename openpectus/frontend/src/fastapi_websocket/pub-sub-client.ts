import { WebsocketRpcClient } from './websocket-rpc-client';

export type PubSubCallback = (value: { data: unknown, topic: string }) => void

export interface PubSubPromiseClientConfig {
  uri: string;
}

export class PubSubClient {
  // TODO: handle subscriptions on ALL_TOPICS key
  callbacks: { [topic: string]: PubSubCallback | undefined } = {};
  rpcClient = new WebsocketRpcClient(this.config.uri, {
    notify: (subscription: { topic: string }, data: Object) => {
      this.callbacks[subscription.topic]?.({data, topic: subscription.topic});
    },
  });

  constructor(private config: PubSubPromiseClientConfig) {}

  subscribe(topic: string, callback: PubSubCallback) {
    this.setCallbackForTopic(topic, callback);
    return this.rpcClient.call('subscribe', {topics: [topic]});
  }

  subscribeMany(topics: string[], callback: PubSubCallback) {
    topics.forEach(topic => this.setCallbackForTopic(topic, callback));
    return this.rpcClient.call('subscribe', {topics: topics});
  }

  unsubscribe(topic: string) {
    this.unsetCallbackForTopic(topic);
  }

  unsubscribeMany(topics: string[]) {
    topics.forEach(topic => this.unsetCallbackForTopic(topic));
  }

  private unsetCallbackForTopic(topic: string) {
    if(this.callbacks[topic] === undefined) console.warn(`Unsubscribing from topic ${topic} with no subscriber`);
    this.callbacks[topic] = undefined;
  }

  private setCallbackForTopic(topic: string, callback: PubSubCallback) {
    if(this.callbacks[topic] !== undefined) console.warn(`Callback for topic ${topic} overwritten!`);
    this.callbacks[topic] = callback;
  }
}
