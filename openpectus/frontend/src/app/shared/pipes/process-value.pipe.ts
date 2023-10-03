import { DecimalPipe } from '@angular/common';
import { Pipe, PipeTransform } from '@angular/core';
import {
  ProcessValue,
  ProcessValueCommandChoiceValue,
  ProcessValueCommandFreeTextValue,
  ProcessValueCommandNumberValue,
  ProcessValueType,
} from '../../api';

@Pipe({
  name: 'processValue',
})
export class ProcessValuePipe implements PipeTransform {
  constructor(private decimalPipe: DecimalPipe) {}

  transform(value: ProcessValue['value'] | Pick<ProcessValue, 'value' | 'value_type' | 'value_unit'> | ProcessValueCommandChoiceValue | ProcessValueCommandFreeTextValue | ProcessValueCommandNumberValue,
            type?: ProcessValue['value_type'] | ProcessValueCommandNumberValue['value_type'] | ProcessValueCommandFreeTextValue['value_type'] | ProcessValueCommandChoiceValue['value_type'],
            unit?: ProcessValue['value_unit']): string | null {
    if(typeof value === 'object') {
      const processValue = value as ProcessValue;
      value = processValue.value;
      type = processValue.value_type;
      unit = processValue.value_unit;
    }
    if(value === undefined) return null;
    if(type === undefined) return null;
    switch(type) {
      case ProcessValueType.STRING:
      case ProcessValueType.CHOICE:
      case ProcessValueCommandFreeTextValue.value_type.STRING:
      case ProcessValueCommandChoiceValue.value_type.CHOICE:
        return value.toString();
      case ProcessValueType.FLOAT:
      case 'float':
        return `${this.decimalPipe.transform(value, '1.2-2')} ${unit}`.trim();
      case ProcessValueType.INT:
      case 'int':
        return `${this.decimalPipe.transform(value, '1.0-0')} ${unit}`.trim();
    }
  }
}
