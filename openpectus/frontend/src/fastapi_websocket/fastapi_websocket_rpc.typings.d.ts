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

export interface RpcSubscription {
  id: string,
  subscriber_id: string,
  topic: string,
  notifier_id?: string,
}
