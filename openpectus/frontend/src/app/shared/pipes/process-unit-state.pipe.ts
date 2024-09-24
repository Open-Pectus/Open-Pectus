import { Pipe, PipeTransform } from '@angular/core';
import { ProcessUnitStateEnum } from '../../typings';
import { UtilMethods } from '../util-methods';

@Pipe({
  name: 'processUnitState',
  standalone: true,
})
export class ProcessUnitStatePipe implements PipeTransform {
  transform(value: ProcessUnitStateEnum | undefined): string {
    switch(value) {
      case 'ready':
        return 'Ready';
      case 'in_progress':
        return 'In progress';
      case 'not_online':
        return 'Not online';
      case 'error':
        return 'Interrupted by error';
      case undefined:
        return '';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
