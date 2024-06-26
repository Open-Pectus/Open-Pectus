import { RpcResponse } from './fastapi_websocket_rpc.typings';
import { RpcChannel } from './rpc-channel';
import { extendWithBaseMethods, RpcMethods } from './rpc-methods-base';

export class WebsocketRpcClient {
  private readonly ws = new WebSocket(this.uri);
  private readonly channel = new RpcChannel(this.methods, this.ws);
  private readyPromise?: Promise<void>;
  private readonly maxReadyPingAttempts = 5;
  private readonly delayBetweenReadyPingsMs = 1000;

  constructor(private uri: string, private readonly methods: RpcMethods, private readonly onDisconnect?: () => void) {
    this.methods = extendWithBaseMethods(methods);
    if(onDisconnect !== undefined) this.ws.onclose = onDisconnect;
  }

  async call(method: string, args: Object = {}) {
    await this.waitForReady();
    return await this.channel.call(method, args);
  }

  private async waitForReady() {
    switch(this.ws.readyState) {
      case WebSocket.OPEN:
        return Promise.resolve();
      case WebSocket.CLOSED:
      case WebSocket.CLOSING:
        return Promise.reject(new Error('WebsocketRpcClient WebSocket is already closed or closing!'));
      case WebSocket.CONNECTING:
        if(this.readyPromise === undefined) {
          this.readyPromise = this.createReadyPromise().finally(() => this.readyPromise = undefined);
        }
        return this.readyPromise;
    }
  }

  private async delay(delayMs: number) {
    return new Promise(resolve => setTimeout(resolve, delayMs));
  }

  private createReadyPromise() {
    return new Promise<void>((resolve, reject) => {
      this.ws.onopen = async () => {
        let receivedResponse: RpcResponse<string> | undefined;
        let attemptCount = 0;
        while(receivedResponse === undefined && attemptCount < this.maxReadyPingAttempts) {
          await this.ping().then(result => receivedResponse = result).catch(_ => {
            console.debug('ping failed, trying again');
            attemptCount += 1;
          });
          if(receivedResponse === undefined) await this.delay(this.delayBetweenReadyPingsMs);
        }
        if(receivedResponse?.result === 'pong') {
          return resolve();
        }
        return reject('Rpc waitForReady failed');
      };
    });
  }

  private ping() {
    return this.channel.call<string>('_ping_');
  }
}
