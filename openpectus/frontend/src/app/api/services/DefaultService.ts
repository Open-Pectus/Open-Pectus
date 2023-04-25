/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BatchJob } from '../models/BatchJob';
import type { ProcessUnit } from '../models/ProcessUnit';
import type { ProcessValue } from '../models/ProcessValue';
import type { ProcessValueUpdate } from '../models/ProcessValueUpdate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Get Unit
     * @param id 
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public static getUnitProcessUnitIdGet(
id: number,
): CancelablePromise<ProcessUnit> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/process_unit/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Units
     * @returns ProcessUnit Successful Response
     * @throws ApiError
     */
    public static getUnitsProcessUnitsGet(): CancelablePromise<Array<ProcessUnit>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/process_units',
        });
    }

    /**
     * Get Batch
     * @param id 
     * @returns BatchJob Successful Response
     * @throws ApiError
     */
    public static getBatchBatchJobIdGet(
id: number,
): CancelablePromise<BatchJob> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/batch_job/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Process Values
     * @param id 
     * @returns ProcessValue Successful Response
     * @throws ApiError
     */
    public static getProcessValuesProcessUnitIdProcessValuesGet(
id: number,
): CancelablePromise<Array<ProcessValue>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/process_unit/{id}/process_values',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Set Process Value
     * @param id 
     * @param requestBody 
     * @returns any Successful Response
     * @throws ApiError
     */
    public static setProcessValueProcessUnitIdProcessValuePost(
id: number,
requestBody: ProcessValueUpdate,
): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/process_unit/{id}/process_value',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
