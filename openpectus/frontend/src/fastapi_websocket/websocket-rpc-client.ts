import { RpcMessage, RpcResponse } from './fastapi_websocket_rpc.typings';
import { RpcChannel } from './rpc-channel';
import { RpcMethodsBase } from './rpc-methods-base';

export class WebsocketRpcClient {
  private readonly ws = new WebSocket(this.uri);
  private readonly channel = new RpcChannel(this.methods, this.ws);

  /* Stuff skipped and maybe TODO:
   * - passing arguments directly to ws
   * - on_connect and on_disconnect handlers
   * - keep alive
   * - more logging
   * - retry tactic and config
   */


  constructor(private uri: string, private methods: RpcMethodsBase = new RpcMethodsBase()) {
    this.ws.addEventListener('message', this.reader.bind(this));
  }

  async waitForReady() {
    return new Promise((resolve, reject) => {
      this.ws.onopen = async () => {
        let receivedResponse: RpcResponse<string> | undefined;
        let attemptCount = 0;
        while(receivedResponse === undefined && attemptCount < 5) {
          await this.ping().then(result => receivedResponse = result).catch(_ => attemptCount += 1);
        }
        if(receivedResponse?.result === 'pong') resolve(receivedResponse);
        reject();
      };
    });
  }

  async call(method: string, args: Object = {}) {
    return await this.channel.call(method, args);
  }

  private reader(message: MessageEvent) {
    const parsedMessage = JSON.parse(message.data) as RpcMessage;
    if(parsedMessage.request !== null) console.log('new request: ' + parsedMessage.request);
  }

  private async ping() {
    return await this.channel.call<string>('_ping_');
  }
}
