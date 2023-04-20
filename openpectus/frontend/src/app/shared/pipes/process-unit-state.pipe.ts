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
      case ProcessUnitStateEnum.READY:
        return 'Ready';
      case ProcessUnitStateEnum.IN_PROGRESS:
        return 'In Progress';
      case ProcessUnitStateEnum.NOT_ONLINE:
        return 'Not Online';
      default:
        return UtilMethods.assertNever(value);
    }
  }

}
