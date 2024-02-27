/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Specifies whether a tag is read from or written to hardware and whether is can be changed in UI.
 *
 * Direction of the tag is in relation to the physical IO. Sensors are regarded as inputs and
 * actuators as outputs. Derived values are regarded as NA.
 */
export enum TagDirection {
    INPUT = 'input',
    OUTPUT = 'output',
    NA = 'na',
    UNSPECIFIED = 'unspecified',
}
