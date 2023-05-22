export class MswEnablement {
  private static readonly MswEnabledKey = 'MSW_ENABLED';

  static get isEnabled() {
    return localStorage.getItem(MswEnablement.MswEnabledKey) === 'true';
  }

  static set isEnabled(isEnabled: boolean) {
    localStorage.setItem(MswEnablement.MswEnabledKey, isEnabled.toString());
  }
}
