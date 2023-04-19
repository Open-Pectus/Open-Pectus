import { Pipe, PipeTransform } from '@angular/core';
import { ProcessUnitStateEnum } from '../../api';
import { UtilMethods } from '../util-methods';

@Pipe({
  name: 'processUnitState',
})
export class ProcessUnitStatePipe implements PipeTransform {

  transform(value: ProcessUnitStateEnum | undefined, ...args: unknown[]): string {
    if(value === undefined) return '';
    switch(value) {
      case ProcessUnitStateEnum.Ready:
        return 'Ready';
      case ProcessUnitStateEnum.InProgress:
        return 'In Progress';
      case ProcessUnitStateEnum.NotOnline:
        return 'Not Online';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
