import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  EventEmitter,
  Injector,
  input,
  OnDestroy,
  Output,
  runInInjectionContext,
  ViewChild,
} from '@angular/core';
// import '@codingame/monaco-vscode-json-default-extension';
import '@codingame/monaco-vscode-theme-defaults-default-extension';
import { editor as MonacoEditor } from '@codingame/monaco-vscode-editor-api';
import { Store } from '@ngrx/store';
import { MonacoEditorLanguageClientWrapper } from 'monaco-editor-wrapper';
import { Observable, Subject, take } from 'rxjs';
import { MethodEditorBehaviours } from './method-editor-behaviours';
import { MonacoEditorBehaviours } from './monaco-editor-behaviours';
import { MonacoWrapperConfig } from './monaco-wrapper-config';


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
  unitId = input<string>();
  editorContent = input<string>();
  isMethodEditor = input<boolean>(false);
  editorOptions = input<MonacoEditor.IEditorOptions & MonacoEditor.IGlobalEditorOptions>({});
  @Output() editorContentChanged = new EventEmitter<string[]>();
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private wrapper = new MonacoEditorLanguageClientWrapper();

  constructor(private store: Store, private injector: Injector) {}

  async ngAfterViewInit() {
    await this.initAndStartWrapper();
    runInInjectionContext(this.injector, this.setupEditorBehaviours.bind(this));
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
    editor.updateOptions(this.editorOptions());
    new MonacoEditorBehaviours(this.componentDestroyed, editor, this.editorSizeChange(), this.editorContent,
      this.onEditorContentChanged.bind(this));
    if(this.isMethodEditor()) new MethodEditorBehaviours(this.store, this.componentDestroyed, editor);
  }

  private onEditorContentChanged(lines: string[]) {
    this.editorContentChanged.emit(lines);
  }

  private async initAndStartWrapper() {
    const wrapperConfig = MonacoWrapperConfig.buildWrapperUserConfig(this.editorElement.nativeElement, this.editorContent(),
      this.unitId(),
      this.isMethodEditor());
    await this.wrapper.initAndStart(wrapperConfig, false);
    this.componentDestroyed.pipe(take(1)).subscribe(() => this.wrapper.dispose());
  }
}
