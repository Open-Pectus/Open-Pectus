export interface RpcRequest {
  method: string,
  arguments?: Object,
  call_id: string,
}

export interface RpcResponse<T> {
  result: T,
  result_type?: string,
  call_id: string,
}

export interface RpcMessage<T = any> {
  request?: RpcRequest | null,
  response?: RpcResponse<T> | null
}
