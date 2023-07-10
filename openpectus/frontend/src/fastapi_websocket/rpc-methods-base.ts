export interface RpcMethods {
  [P: string]: Function;
}

export function extendWithBaseMethods(methods: RpcMethods) {
  return {...methods, ping: () => 'pong'};
}
