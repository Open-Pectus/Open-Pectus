/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { HttpClient, HttpHeaders } from '@angular/common/http';
import type { HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { forkJoin, of, throwError } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';
import type { Observable } from 'rxjs';

import { ApiError } from './ApiError';
import type { ApiRequestOptions } from './ApiRequestOptions';
import type { ApiResult } from './ApiResult';
import type { OpenAPIConfig } from './OpenAPI';

const isDefined = <T>(value: T | null | undefined): value is Exclude<T, null | undefined> => {
    return value !== undefined && value !== null;
};

const isString = (value: any): value is string => {
    return typeof value === 'string';
};

const isStringWithValue = (value: any): value is string => {
    return isString(value) && value !== '';
};

const isBlob = (value: any): value is Blob => {
    return (
        typeof value === 'object' &&
        typeof value.type === 'string' &&
        typeof value.stream === 'function' &&
        typeof value.arrayBuffer === 'function' &&
        typeof value.constructor === 'function' &&
        typeof value.constructor.name === 'string' &&
        /^(Blob|File)$/.test(value.constructor.name) &&
        /^(Blob|File)$/.test(value[Symbol.toStringTag])
    );
};

const isFormData = (value: any): value is FormData => {
    return value instanceof FormData;
};

const base64 = (str: string): string => {
    try {
        return btoa(str);
    } catch (err) {
        // @ts-ignore
        return Buffer.from(str).toString('base64');
    }
};

const getQueryString = (params: Record<string, any>): string => {
    const qs: string[] = [];

    const append = (key: string, value: any) => {
        qs.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
    };

    const process = (key: string, value: any) => {
        if (isDefined(value)) {
            if (Array.isArray(value)) {
                value.forEach(v => {
                    process(key, v);
                });
            } else if (typeof value === 'object') {
                Object.entries(value).forEach(([k, v]) => {
                    process(`${key}[${k}]`, v);
                });
            } else {
                append(key, value);
            }
        }
    };

    Object.entries(params).forEach(([key, value]) => {
        process(key, value);
    });

    if (qs.length > 0) {
        return `?${qs.join('&')}`;
    }

    return '';
};

const getUrl = (config: OpenAPIConfig, options: ApiRequestOptions): string => {
    const encoder = config.ENCODE_PATH || encodeURI;

    const path = options.url
        .replace('{api-version}', config.VERSION)
        .replace(/{(.*?)}/g, (substring: string, group: string) => {
            if (options.path?.hasOwnProperty(group)) {
                return encoder(String(options.path[group]));
            }
            return substring;
        });

    const url = `${config.BASE}${path}`;
    if (options.query) {
        return `${url}${getQueryString(options.query)}`;
    }
    return url;
};

const getFormData = (options: ApiRequestOptions): FormData | undefined => {
    if (options.formData) {
        const formData = new FormData();

        const process = (key: string, value: any) => {
            if (isString(value) || isBlob(value)) {
                formData.append(key, value);
            } else {
                formData.append(key, JSON.stringify(value));
            }
        };

        Object.entries(options.formData)
            .filter(([_, value]) => isDefined(value))
            .forEach(([key, value]) => {
                if (Array.isArray(value)) {
                    value.forEach(v => process(key, v));
                } else {
                    process(key, value);
                }
            });

        return formData;
    }
    return undefined;
};

type Resolver<T> = (options: ApiRequestOptions) => Promise<T>;

const resolve = async <T>(options: ApiRequestOptions, resolver?: T | Resolver<T>): Promise<T | undefined> => {
    if (typeof resolver === 'function') {
        return (resolver as Resolver<T>)(options);
    }
    return resolver;
};

const getHeaders = (config: OpenAPIConfig, options: ApiRequestOptions): Observable<HttpHeaders> => {
    return forkJoin({
        token: resolve(options, config.TOKEN),
        username: resolve(options, config.USERNAME),
        password: resolve(options, config.PASSWORD),
        additionalHeaders: resolve(options, config.HEADERS),
    }).pipe(
        map(({ token, username, password, additionalHeaders }) => {
            const headers = Object.entries({
                Accept: 'application/json',
                ...additionalHeaders,
                ...options.headers,
            })
                .filter(([_, value]) => isDefined(value))
                .reduce((headers, [key, value]) => ({
                    ...headers,
                    [key]: String(value),
                }), {} as Record<string, string>);

            if (isStringWithValue(token)) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            if (isStringWithValue(username) && isStringWithValue(password)) {
                const credentials = base64(`${username}:${password}`);
                headers['Authorization'] = `Basic ${credentials}`;
            }

            if (options.body) {
                if (options.mediaType) {
                    headers['Content-Type'] = options.mediaType;
                } else if (isBlob(options.body)) {
                    headers['Content-Type'] = options.body.type || 'application/octet-stream';
                } else if (isString(options.body)) {
                    headers['Content-Type'] = 'text/plain';
                } else if (!isFormData(options.body)) {
                    headers['Content-Type'] = 'application/json';
                }
            }

            return new HttpHeaders(headers);
        }),
    );
};

const getRequestBody = (options: ApiRequestOptions): any => {
    if (options.body) {
        if (options.mediaType?.includes('/json')) {
            return JSON.stringify(options.body)
        } else if (isString(options.body) || isBlob(options.body) || isFormData(options.body)) {
            return options.body;
        } else {
            return JSON.stringify(options.body);
        }
    }
    return undefined;
};

export const sendRequest = <T>(
    config: OpenAPIConfig,
    options: ApiRequestOptions,
    http: HttpClient,
    url: string,
    body: any,
    formData: FormData | undefined,
    headers: HttpHeaders
): Observable<HttpResponse<T>> => {
    return http.request<T>(options.method, url, {
        headers,
        body: body ?? formData,
        withCredentials: config.WITH_CREDENTIALS,
        observe: 'response',
    });
};

const getResponseHeader = <T>(response: HttpResponse<T>, responseHeader?: string): string | undefined => {
    if (responseHeader) {
        const value = response.headers.get(responseHeader);
        if (isString(value)) {
            return value;
        }
    }
    return undefined;
};

const getResponseBody = <T>(response: HttpResponse<T>): T | undefined => {
    if (response.status !== 204 && response.body !== null) {
        return response.body;
    }
    return undefined;
};

const catchErrorCodes = (options: ApiRequestOptions, result: ApiResult): void => {
    const errors: Record<number, string> = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        500: 'Internal Server Error',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        ...options.errors,
    }

    const error = errors[result.status];
    if (error) {
        throw new ApiError(options, result, error);
    }

    if (!result.ok) {
        throw new ApiError(options, result, 'Generic Error');
    }
};

/**
 * Request method
 * @param config The OpenAPI configuration object
 * @param http The Angular HTTP client
 * @param options The request options from the service
 * @returns Observable<T>
 * @throws ApiError
 */
export const request = <T>(config: OpenAPIConfig, http: HttpClient, options: ApiRequestOptions): Observable<T> => {
    const url = getUrl(config, options);
    const formData = getFormData(options);
    const body = getRequestBody(options);

    return getHeaders(config, options).pipe(
        switchMap(headers => {
            return sendRequest<T>(config, options, http, url, formData, body, headers);
        }),
        map(response => {
            const responseBody = getResponseBody(response);
            const responseHeader = getResponseHeader(response, options.responseHeader);
            return {
                url,
                ok: response.ok,
                status: response.status,
                statusText: response.statusText,
                body: responseHeader ?? responseBody,
            } as ApiResult;
        }),
        catchError((error: HttpErrorResponse) => {
            if (!error.status) {
                return throwError(error);
            }
            return of({
                url,
                ok: error.ok,
                status: error.status,
                statusText: error.statusText,
                body: error.error ?? error.statusText,
            } as ApiResult);
        }),
        map(result => {
            catchErrorCodes(options, result);
            return result.body as T;
        }),
        catchError((error: ApiError) => {
            return throwError(error);
        }),
    );
};
