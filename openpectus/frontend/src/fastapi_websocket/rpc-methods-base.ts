// export interface RpcMethods {
//   [P: string]: Function;
// }

export interface RpcMethods {
  // ping(): string;

  // getChannelId(): string;
  [P: string]: Function;
}

// export class RpcMethodsBase implements RpcMethods {
//
//   ping() {
//     return 'pong';
//   }
//
//   // getChannelId() {
//   //   return this['channelId']();
//   // }
//
//   [P: string]: Function;
// }


export function extendWithBaseMethods(methods: RpcMethods) {
  return {...methods, ping: () => 'pong'};
}
