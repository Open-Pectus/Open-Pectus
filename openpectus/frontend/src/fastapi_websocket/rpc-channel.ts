import { RpcMessage, RpcResponse } from './fastapi_websocket_rpc.typings';
import { RpcMethods } from './rpc-methods-base';

export class RpcChannel {
  // other = new Proxy<{[P: string]: Function}>(RpcMethodsBase, new RpcCaller(this));

  constructor(private methods: RpcMethods, private socket: WebSocket, public id: string = crypto.randomUUID()) {
    this.socket.addEventListener('message', this.onMessage.bind(this));
  }

  async call<T = unknown>(method: string, args: Object = {}, call_id: string = crypto.randomUUID()) {
    const message: RpcMessage = {request: {method, arguments: args, call_id}};
    return new Promise<RpcResponse<T>>((resolve, reject) => {
      const onmessage = (msgEvent: MessageEvent) => {
        const parsedData = JSON.parse(msgEvent.data) as RpcMessage;
        if(parsedData.response?.call_id === call_id) {
          this.socket.removeEventListener('message', onmessage);
          resolve(parsedData.response);
        }
      };
      setTimeout(() => {
        this.socket.removeEventListener('message', onmessage);
        reject('timeout');
      }, 1000);
      this.socket.addEventListener('message', onmessage);
      this.socket.send(JSON.stringify(message));
    });
  }

  private onMessage(msgEvent: MessageEvent) {
    const parsedData = JSON.parse(msgEvent.data) as RpcMessage;
    if(parsedData.request === null || parsedData.request === undefined) return;
    if(!Object.keys(this.methods).includes(parsedData.request.method)) return;
    const method = this.methods[parsedData.request.method];
    const result = parsedData.request.arguments === undefined
                   ? method()
                   : method(...Object.values(parsedData.request.arguments));
    const resultMsg: RpcMessage = {
      response: {result, call_id: parsedData.request.call_id, result_type: 'str'},
    };
    this.socket.send(JSON.stringify(resultMsg));
  }
}
