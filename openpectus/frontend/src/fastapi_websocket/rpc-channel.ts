import { RpcMessage, RpcResponse } from './fastapi_websocket_rpc.typings';
import { RpcMethodsBase } from './rpc-methods-base';

export class RpcChannel {
  // other = new Proxy<{[P: string]: Function}>(RpcMethodsBase, new RpcCaller(this));

  constructor(private methods: RpcMethodsBase, private socket: WebSocket, public id: string = crypto.randomUUID()) {}

  async call<T = unknown>(method: string, args: Object = {}, call_id: string = crypto.randomUUID()) {
    const message: RpcMessage = {request: {method, arguments: args, call_id}};
    return new Promise<RpcResponse<T>>((resolve, reject) => {
      const onmessage = (message: MessageEvent) => {
        this.socket.removeEventListener('message', onmessage);
        const parsedData = JSON.parse(message.data) as RpcMessage;
        if(parsedData.response?.call_id === call_id) resolve(parsedData.response);
      };
      setTimeout(() => {
        this.socket.removeEventListener('message', onmessage);
        reject('timeout');
      }, 1000);
      this.socket.addEventListener('message', onmessage);
      this.socket.send(JSON.stringify(message));
    });
  }
}
