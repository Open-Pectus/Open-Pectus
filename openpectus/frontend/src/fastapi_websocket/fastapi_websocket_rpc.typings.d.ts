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

export enum WebSocketFrameType {
  Text = 'text',
  Binary = 'binary'
}


/*
UUID = str


class RpcRequest(BaseModel):
method: str
arguments: Optional[Dict] = {}
call_id: Optional[UUID] = None


ResponseT = TypeVar('ResponseT')


class RpcResponse(GenericModel, Generic[ResponseT]):
result: ResponseT
result_type: Optional[str]
call_id: Optional[UUID] = None


class RpcMessage(BaseModel):
request: Optional[RpcRequest] = None
response: Optional[RpcResponse] = None


class WebSocketFrameType(str, Enum):
Text = "text"
Binary = "binary"*/
