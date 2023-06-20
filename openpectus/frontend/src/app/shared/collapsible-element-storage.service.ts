import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class CollapsibleElementStorageService {
  saveHeight(name: string | undefined, height: number) {
    if(name === undefined) return;
    localStorage.setItem(this.getKeyForHeight(name), height.toString());
  }

  getHeight(name: string) {
    const item = localStorage.getItem(this.getKeyForHeight(name));
    if(item === null) return item;
    return parseInt(item);
  }

  saveCollapsedState(name: string | undefined, collapsed: boolean) {
    if(name === undefined) return;
    localStorage.setItem(this.getKeyForCollapsedState(name), collapsed.toString());
  }

  getCollapsedState(name: string) {
    const item = localStorage.getItem(this.getKeyForCollapsedState(name));
    if(item === null) return item;
    return item === 'true';
  }

  private getKeyForHeight(name: string) {
    return `[${window.location.pathname}] ${name} element height`;
  }

  private getKeyForCollapsedState(name: string) {
    return `[${window.location.pathname}] ${name} element collapsed`;
  }
}
