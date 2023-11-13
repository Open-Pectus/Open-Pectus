import { RpcSubscription } from './fastapi_websocket_rpc.typings';
import { WebsocketRpcClient } from './websocket-rpc-client';

export interface PubSubCallbackParameters {
  data: unknown,
  topic: string
}

export type PubSubCallback = (_: PubSubCallbackParameters) => void

export interface PubSubPromiseClientConfig {
  uri: string;
}

export class PubSubClient {
  // TODO: handle subscriptions on ALL_TOPICS key

  rpcClient = new WebsocketRpcClient(this.config.uri, {
    notify: (subscription: RpcSubscription, data: unknown) => {
      this.getCallbacks(subscription.topic).forEach(callback => callback({data, topic: subscription.topic}));
    },
  });
  private readonly _callbacks: { [topic: string]: PubSubCallback[] | undefined } = {};

  constructor(private config: PubSubPromiseClientConfig) {}

  getCallbacks(topic: string): PubSubCallback[] {
    return this._callbacks[topic] ?? [];
  }

  async subscribe(topic: string, callback: PubSubCallback) {
    const newCallbacks = this.getCallbacks(topic).concat(callback);
    this._callbacks[topic] = newCallbacks;
    if(newCallbacks.length === 1) {
      // this is the first callback on this topic, so we should subscribe on server
      return this.rpcClient.call('subscribe', {topics: [topic]});
    } else {
      return Promise.resolve();
    }
  }

  async subscribeMany(topics: string[], callback: PubSubCallback) {
    return Promise.all(topics.map(topic => this.subscribe(topic, callback)));
  }

  async unsubscribe(topic: string, callbackToRemove: PubSubCallback) {
    const otherCallbacks = this.getCallbacks(topic).filter(callback => callback !== callbackToRemove);
    if(otherCallbacks.length === 0) {
      delete this._callbacks[topic];
      return this.rpcClient.call('unsubscribe', {topics: [topic]});
    } else {
      this._callbacks[topic] = otherCallbacks;
      return Promise.resolve();
    }
  }

  async unsubscribeMany(topics: string[], callback: PubSubCallback) {
    return Promise.all(topics.map(topic => this.unsubscribe(topic, callback)));
  }
}
