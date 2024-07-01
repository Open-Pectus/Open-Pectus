export type RpcMethods = Record<string, (...args: never[]) => unknown>;

export function extendWithBaseMethods(methods: RpcMethods) {
  return {...methods, ping: () => 'pong'};
}
