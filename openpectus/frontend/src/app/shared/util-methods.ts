export class UtilMethods {
  static isNotNullOrUndefined<T>(value: T | null | undefined): value is T {
    return value !== null && value !== undefined;
  }

  static assertNever(x: never): never {
    throw Error(`${x} was not handled`);
  }
}
