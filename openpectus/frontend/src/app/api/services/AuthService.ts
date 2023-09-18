/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Observable } from 'rxjs';

import type { AuthConfig } from '../models/AuthConfig';

import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

@Injectable({
  providedIn: 'root',
})
export class AuthService {

    constructor(public readonly http: HttpClient) {}

    /**
     * Get Config
     * @returns AuthConfig Successful Response
     * @throws ApiError
     */
    public getConfig(): Observable<AuthConfig> {
        return __request(OpenAPI, this.http, {
            method: 'GET',
            url: '/auth/config',
        });
    }

}
