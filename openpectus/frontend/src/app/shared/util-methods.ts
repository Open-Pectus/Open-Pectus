export class UtilMethods {
  static isNotNullOrUndefined<T>(value: T | null | undefined): value is T {
    return value !== null && value !== undefined;
  }

  static isNumber(value: unknown): value is number {
    return typeof value === 'number';
  }

  static assertNever(x: never): never {
    throw Error(`${x} was not handled`);
  }

  static async delay(delayMs: number) {
    return new Promise(resolve => setTimeout(resolve, delayMs));
  }
}
