import { CanDeactivateFn } from '@angular/router';
import { UnitDetailsComponent } from './unit-details.component';

export const unsavedMethodGuard: CanDeactivateFn<UnitDetailsComponent> = (component) => {
  if(!component.methodIsDirty()) return true;
  return confirm('Are you sure you want to leave the page?\nYou have unsaved changes to the method.');
};
