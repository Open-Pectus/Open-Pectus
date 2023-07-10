import { RpcResponse } from './fastapi_websocket_rpc.typings';
import { RpcChannel } from './rpc-channel';
import { extendWithBaseMethods, RpcMethods } from './rpc-methods-base';

export class WebsocketRpcClient {
  private readonly ws = new WebSocket(this.uri);
  private readonly channel = new RpcChannel(this.methods, this.ws);
  private readyPromise?: Promise<void>;

  /* Stuff skipped and maybe TODO:
   * - passing arguments directly to ws
   * - on_connect and on_disconnect handlers
   * - keep alive
   * - retry tactic and config
   * - channel id
   */


  constructor(private uri: string, private readonly methods: RpcMethods) {
    this.methods = extendWithBaseMethods(methods);
  }

  async waitForReady() {
    switch(this.ws.readyState) {
      case WebSocket.OPEN:
        return Promise.resolve();
      case WebSocket.CLOSED:
      case WebSocket.CLOSING:
        return Promise.reject(new Error('WebsocketRpcClient WebSocket is already closed or closing!'));
      case WebSocket.CONNECTING:
        if(this.readyPromise === undefined) this.readyPromise = this.createReadyPromise();
        return this.readyPromise;
    }
  }

  call(method: string, args: Object = {}) {
    return this.waitForReady().then(() => this.channel.call(method, args));
  }

  private createReadyPromise() {
    return new Promise<void>((resolve, reject) => {
      this.ws.onopen = async () => {
        let receivedResponse: RpcResponse<string> | undefined;
        let attemptCount = 0;
        while(receivedResponse === undefined && attemptCount < 5) {
          await this.ping().then(result => receivedResponse = result).catch(_ => {
            console.debug('ping failed, trying again');
            attemptCount += 1;
          });
        }
        if(receivedResponse?.result === 'pong') {
          this.readyPromise = undefined;
          return resolve();
        }
        this.readyPromise = undefined;
        return reject('Rpc waitForReady failed');
      };
    });
  }

  private ping() {
    return this.channel.call<string>('_ping_');
  }
}
