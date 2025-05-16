import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, input, OnDestroy, ViewChild } from '@angular/core';
// import '@codingame/monaco-vscode-json-default-extension';
import '@codingame/monaco-vscode-theme-defaults-default-extension';
import { Store } from '@ngrx/store';
import { MonacoEditorLanguageClientWrapper } from 'monaco-editor-wrapper';
import { firstValueFrom, Observable, Subject, take } from 'rxjs';
import { MonacoEditorBehaviours } from './monaco-editor-behaviours';
import { MonacoWrapperConfig } from './monaco-wrapper-config';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';


@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['monaco-editor.component.scss'],
  template: `
    <div #editor class="w-full h-full"></div>
  `,
})
export class MonacoEditorComponent implements AfterViewInit, OnDestroy {
  editorSizeChange = input.required<Observable<void>>();
  readOnlyEditor = input(false);
  unitId = input<string>();
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private wrapper = new MonacoEditorLanguageClientWrapper();
  private methodContent = this.store.select(MethodEditorSelectors.methodContent);

  constructor(private store: Store) {}

  async ngAfterViewInit() {
    await this.initAndStartWrapper();
    this.setupEditorBehaviours();
    await this.startLanguageClient();
  }

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private async startLanguageClient() {
    if(this.unitId() !== undefined) {
      this.wrapper.initLanguageClients();
      await this.wrapper.startLanguageClients();
    }
  }

  private setupEditorBehaviours() {
    const editor = this.wrapper.getEditor();
    if(editor === undefined) throw Error('Monaco Editor Wrapper returned no editor!');
    new MonacoEditorBehaviours(this.store, this.componentDestroyed, editor, this.readOnlyEditor, this.editorSizeChange());
  }

  private async initAndStartWrapper() {
    const methodContent = await firstValueFrom(this.methodContent);
    const wrapperConfig = MonacoWrapperConfig.buildWrapperUserConfig(this.editorElement.nativeElement, methodContent, this.unitId());
    await this.wrapper.initAndStart(wrapperConfig, false);
    this.componentDestroyed.pipe(take(1)).subscribe(() => this.wrapper.dispose());
  }
}
