import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { compareAsc, compareDesc } from 'date-fns';

export interface TableColumn<T> {
  key: keyof T;
  header: string;
  isDate?: boolean;
}

export enum TableSortDirection {
  Ascending = 'ascending',
  Descending = 'descending',
}

export interface DefaultTableSort<T> {
  columnKey: keyof T;
  direction: TableSortDirection;
}

@Component({
  selector: 'app-table',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="bg-vscode-background-grey rounded-lg shadow-lg overflow-hidden">
      <table class="w-full table-auto border-collapse">
        <thead>
        <tr class="bg-sky-700 text-white cursor-pointer select-none">
          <th *ngFor="let column of columns" class="p-2" (click)="setSortByColumn(column)">
            <span>{{column.header}}</span>
            <ng-container *ngIf="sortColumn === column">
              <span *ngIf="sortDir === TableSortDirection.Descending" class="codicon codicon-arrow-up ml-1 -mr-5"></span>
              <span *ngIf="sortDir === TableSortDirection.Ascending" class="codicon codicon-arrow-down ml-1 -mr-5"></span>
            </ng-container>
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
  @Input() columns?: TableColumn<T>[];
  @Output() rowClicked = new EventEmitter<T>();
  protected sortDir = TableSortDirection.Ascending;
  protected sortColumn?: TableColumn<T>;
  protected readonly TableSortDirection = TableSortDirection;

  @Input() set defaultSort(defaultSort: DefaultTableSort<T>) {
    this.sortColumn = this.columns?.find((column => column.key === defaultSort.columnKey));
    this.sortDir = defaultSort.direction;
  }

  private _data?: T[];

  get data(): T[] | undefined {
    if(this.sortColumn !== undefined) this.sortData(this.sortColumn);
    return this._data;
  }

  @Input() set data(value: T[] | undefined) {
    this._data = structuredClone(value);
  }

  toDate(value: T[keyof T]): Date {
    if(typeof value !== 'string' && typeof value !== 'number') throw Error('Value is not Date!');
    return new Date(value);
  }

  format(value: T[keyof T]): string | T[keyof T] {
    if(Array.isArray(value)) return value.join(', ');
    return value;
  }

  setSortByColumn(column: TableColumn<T>) {
    if(this.sortColumn === column) {
      switch(this.sortDir) {
        case TableSortDirection.Ascending:
          this.sortDir = TableSortDirection.Descending;
          break;
        case TableSortDirection.Descending:
          this.sortDir = TableSortDirection.Ascending;
          break;
      }
    } else {
      this.sortColumn = column;
      this.sortDir = TableSortDirection.Ascending;
    }
  }

  private sortData(sortColumn: TableColumn<T>) {
    this._data?.sort((a, b) => {
      const aValue = a[sortColumn.key];
      const bValue = b[sortColumn.key];
      if(sortColumn.isDate) {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return compareAsc(this.toDate(aValue), this.toDate(bValue));
          case TableSortDirection.Descending:
            return compareDesc(this.toDate(aValue), this.toDate(bValue));
        }
      }
      if(typeof aValue === 'string' && typeof bValue === 'string') {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return aValue.localeCompare(bValue);
          case TableSortDirection.Descending:
            return bValue.localeCompare(aValue);
        }
      }
      if(typeof aValue === 'number' && typeof bValue === 'number') {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return aValue - bValue;
          case TableSortDirection.Descending:
            return bValue - aValue;
        }
      }
      if(Array.isArray(aValue) && Array.isArray(bValue)) {
        switch(this.sortDir) {
          case TableSortDirection.Ascending:
            return aValue.toString().localeCompare(bValue.toString());
          case TableSortDirection.Descending:
            return bValue.toString().localeCompare(aValue.toString());
        }
      }
      return 0;
    });
  }
}
