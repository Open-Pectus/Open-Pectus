import { RpcMessage } from './fastapi_websocket_rpc.typings';
import { RpcMethodsBase } from './rpc-methods-base';

export class RpcChannel {
  // other = new Proxy<{[P: string]: Function}>(RpcMethodsBase, new RpcCaller(this));

  constructor(private methods: RpcMethodsBase, private socket: WebSocket, public id: string = crypto.randomUUID()) {}

  async async_call(method: string, args: Object = {}, call_id: string = crypto.randomUUID()) {
    const message: RpcMessage = {request: {method, arguments: args, call_id}};
    return new Promise<string>(resolve => {
      const onmessage = (message: MessageEvent) => {
        this.socket.removeEventListener('message', onmessage);
        const parsedData = JSON.parse(message.data);
        resolve(parsedData.response);
      };
      this.socket.addEventListener('message', onmessage);
      this.socket.send(JSON.stringify(message));
    });
  }

  async call(method: string, args: Object = {}) {
    return await this.async_call(method, args);
  }
}
