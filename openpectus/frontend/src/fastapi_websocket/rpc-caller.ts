import { RpcChannel } from './rpc-channel';

export class RpcCaller implements ProxyHandler<{ [P: string]: Function }> {
  constructor(private channel: RpcChannel) {}

  get(target: Object, prop: string, receiver: Object) {
    return this.channel.call(prop);
  }
}
