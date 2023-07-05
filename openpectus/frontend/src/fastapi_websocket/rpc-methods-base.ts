import { RpcChannel } from './rpc-channel';

export interface RpcMethods {
  ping(): string;

  getChannelId(): string | undefined;
}

export class RpcMethodsBase implements RpcMethods {
  channel?: RpcChannel;

  ping() {
    return 'pong';
  }

  getChannelId() {
    return this.channel?.id;
  }
}
