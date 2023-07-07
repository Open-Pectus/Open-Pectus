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
    const method = this.methods[parsedData.request.method];
    if(method === undefined) return;
    const result = method(...Object.values(parsedData.request.arguments ?? {}));
    const resultMsg: RpcMessage = {
      response: {
        result,
        result_type: this.calculateResultType(result),
        call_id: parsedData.request.call_id,
      },
    };
    this.socket.send(JSON.stringify(resultMsg));
  }

  private calculateResultType(result: unknown): string | undefined {
    switch(typeof result) {
      case 'undefined':
        return undefined;
      case 'boolean':
        return 'bool';
      case 'bigint':
      case 'number':
        return 'float';
      case 'string':
      case 'object':
        return 'str';
      case 'function':
      case 'symbol':
        console.error('Rpc result of incompatible type:', result);
        return 'unknown-type';

    }
  }
}
