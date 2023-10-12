export class UtilMethods {
  static get isMobile() {
    return window.innerWidth < 1024;
  }

  static get isDesktop() {
    return !UtilMethods.isMobile;
  }

  static isNotNullOrUndefined<T>(value: T | null | undefined): value is T {
    return value !== null && value !== undefined;
  }

  static isNumber(value: unknown): value is number {
    return typeof value === 'number';
  }

  static isString(value: unknown): value is string {
    return typeof value === 'string';
  }

  static assertNever(x: never): never {
    throw Error(`${x} was not handled`);
  }

  static async delay(delayMs: number) {
    return new Promise(resolve => setTimeout(resolve, delayMs));
  }

  static getNumberRange(from: number, to: number): number[] {
    return Array(to - from + 1).fill(undefined).map((_, i) => i + from);
  }

  static arrayEquals<T>(a: T[], b: T[]): boolean {
    return a.length === b.length && a.every((value, index) => b[index] === value);
  }
}
