import { RpcSubscription } from './fastapi_websocket_rpc.typings';
import { WebsocketRpcClient } from './websocket-rpc-client';

export interface PubSubCallbackParameters {
  data?: unknown,
  topic: string
}

export type PubSubCallback = (_: PubSubCallbackParameters) => void

export interface PubSubPromiseClientConfig {
  uri: string;
  imitatePublishOnReconnect?: boolean;
  onDisconnect?: () => void;
  onReconnect?: () => void;
}

const RECONNECT_DELAY_MS = 3000;

export class PubSubClient {
  // TODO: handle subscriptions on ALL_TOPICS key

  private readonly _callbacks: Record<string, PubSubCallback[]> = {};
  private readonly rpcClientMethods = {
    notify: (subscription: RpcSubscription, data: unknown) => {
      this.getCallbacks(subscription.topic).forEach(callback => callback({data, topic: subscription.topic}));
    },
  };
  private rpcClient = this.createRpcClient();

  constructor(private config: PubSubPromiseClientConfig) {}

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

  private getCallbacks(topic: string): PubSubCallback[] {
    return this._callbacks[topic] ?? [];
  }

  private createRpcClient() {
    return new WebsocketRpcClient(this.config.uri, this.rpcClientMethods, () => {
      if(this.config.onDisconnect !== undefined) this.config.onDisconnect();
      setTimeout(this.reconnect.bind(this), RECONNECT_DELAY_MS);
    });
  }

  private async reconnect() {
    this.rpcClient = this.createRpcClient();
    const topics = Object.keys(this._callbacks);
    await this.rpcClient.call('subscribe', {topics});
    if(this.config.onReconnect !== undefined) this.config.onReconnect();
    if(this.config.imitatePublishOnReconnect) {
      // imitate backend publishing to all topics, as we might have missed some while websocket connection was down.
      Object.entries(this._callbacks).forEach(([topic, callbacks]) => callbacks.forEach(callback => callback({topic})));
    }
  }
}
