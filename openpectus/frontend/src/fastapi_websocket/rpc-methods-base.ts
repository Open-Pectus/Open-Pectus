// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type RpcMethods = Record<string, (...args: any[]) => unknown>;

export function extendWithBaseMethods(methods: RpcMethods) {
  return {...methods, ping: () => 'pong'};
}
