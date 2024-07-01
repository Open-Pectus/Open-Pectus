export interface RpcRequest {
  method: string,
  arguments?: object,
  call_id: string,
}

export interface RpcResponse<T> {
  result: T,
  result_type?: string,
  call_id: string,
}

export interface RpcMessage<T = unknown> {
  request?: RpcRequest | null,
  response?: RpcResponse<T> | null
}

export interface RpcSubscription {
  id: string,
  subscriber_id: string,
  topic: string,
  notifier_id?: string,
}
