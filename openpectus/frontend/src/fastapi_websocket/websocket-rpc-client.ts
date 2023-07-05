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
    this.ws.onmessage = this.reader.bind(this);
  }

  async waitForReady() {
    await this.waitForRpcReady();
  }

  private reader(message: MessageEvent) {

  }

  private async waitForRpcReady() {
    return new Promise(resolve => {
      this.ws.onopen = async () => {
        let receivedResponse = undefined;
        let attemptCount = 0;
        while(receivedResponse === undefined && attemptCount < 5) {
          await this.ping().then(result => receivedResponse = result).catch(_ => attemptCount += 1);
          console.log(receivedResponse);
        }
        resolve(receivedResponse);
        console.log(attemptCount);
      };
    });
  }

  private async ping() {
    return await this.channel.call('_ping_');
  }
}
