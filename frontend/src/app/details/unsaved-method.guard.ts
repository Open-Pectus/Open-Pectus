import { CanDeactivateFn } from '@angular/router';
import { UnitDetailsComponent } from './unit-details.component';

export const unsavedMethodGuard: CanDeactivateFn<UnitDetailsComponent> = (component) => {
  // if method isn't dirty, we don't have unsaved changes and can navigate away.
  let canDeactivate = !component.methodIsDirty();

  // let user override with confirm dialog
  if(!canDeactivate) canDeactivate = confirm('Are you sure you want to leave the page?\nYou have unsaved changes to the method.');
  
  // if we leave the page, remove the onbeforeunload listener set up in method-editor-behaviours.ts
  if(canDeactivate) window.onbeforeunload = null;

  return canDeactivate;
};
