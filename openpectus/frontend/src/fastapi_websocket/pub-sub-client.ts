import { WebsocketRpcClient } from './websocket-rpc-client';

export type PubSubCallback = (data: Object, topic: string) => void

export class PubSubClient {
  // TODO: handle subscriptions on ALL_TOPICS key
  callbacks: { [K: string]: Function | undefined } = {};
  rpcClient = new WebsocketRpcClient(`ws://${window.location.host}/api/frontend-pubsub`, {
    notify: (subscription: { topic: string }, data: Object) => {
      this.callbacks[subscription.topic]?.(data, subscription.topic);
    },
  });

  constructor(topics: string[], callback: PubSubCallback) {
    this.subscribeMany(topics, callback).then();
  }

  subscribe(topic: string, callback: PubSubCallback) {
    this.callbacks[topic] = callback;
    return this.rpcClient.call('subscribe', {topics: [topic]});
  }

  subscribeMany(topics: string[], callback: PubSubCallback) {
    topics.forEach(topic => this.callbacks[topic] = callback);
    return this.rpcClient.call('subscribe', {topics: topics});
  }
}
