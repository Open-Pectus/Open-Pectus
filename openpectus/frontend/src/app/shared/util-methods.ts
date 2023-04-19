export class UtilMethods {
  static assertNever(x: never): never {
    throw Error(`${x} was not handled`);
  }
}
