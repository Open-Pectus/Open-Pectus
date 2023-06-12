import { DecimalPipe } from '@angular/common';
import { Pipe, PipeTransform } from '@angular/core';
import { ProcessValueType } from '../../api';

@Pipe({
  name: 'processValuePipe',
})
export class ProcessValuePipePipe implements PipeTransform {
  constructor(private decimalPipe: DecimalPipe) {}

  transform(value: any, type?: ProcessValueType, unit?: string): string | null {
    if(type === undefined) return null;
    switch(type) {
      case ProcessValueType.STRING:
        return value.toString();
      case ProcessValueType.FLOAT:
        return `${this.decimalPipe.transform(value, '1.2-2')} ${unit}`.trim();
      case ProcessValueType.INT:
        return `${this.decimalPipe.transform(value, '1.0-0')} ${unit}`.trim();
    }
  }

}
