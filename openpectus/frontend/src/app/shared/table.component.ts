import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

export interface TableColumn<T> {
  key: keyof T;
  header: string;
  isDate?: boolean;
}

@Component({
  selector: 'app-table',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bg-vscode-background-grey rounded-lg shadow-lg overflow-hidden">
      <table class="w-full table-auto border-collapse">
        <thead>
        <tr class="bg-sky-700 text-white">
          <th *ngFor="let column of columns" class="p-2">
            {{column.header}}
          </th>
        </tr>
        </thead>
        <tbody class="cursor-pointer">
        <tr *ngFor="let row of data" class="border-y last-of-type:border-none border-slate-500" (click)="rowClicked.emit(row)">
          <td *ngFor="let column of columns" class="text-center p-2">
            <span *ngIf="column.isDate; else defaultFormat">{{toDate(row[column.key]) | date}}</span>
            <ng-template #defaultFormat>{{format(row[column.key])}}</ng-template>
          </td>
        </tr>
        </tbody>
      </table>
    </div>


  `,
})
export class TableComponent<T> {
  @Input() data?: T[];
  @Input() columns?: TableColumn<T>[];
  @Output() rowClicked = new EventEmitter<T>();

  toDate(value: T[keyof T]): Date {
    if(typeof value !== 'string' && typeof value !== 'number') throw Error('Value is not Date!');
    return new Date(value);
  }

  format(value: T[keyof T]): string | T[keyof T] {
    if(Array.isArray(value)) return value.join(', ');
    return value;
  }
}
