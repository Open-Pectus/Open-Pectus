export interface RpcMethods {
  [methodName: string]: Function;
}

export function extendWithBaseMethods(methods: RpcMethods) {
  return {...methods, ping: () => 'pong'};
}
